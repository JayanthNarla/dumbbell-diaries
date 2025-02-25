from typing import List, Optional, Dict, Any
from datetime import datetime, date
from bson import ObjectId

from app.models.measurement import MeasurementCreate, MeasurementUpdate, MeasurementInDB, Measurement
from app.db.mongodb.mongodb import get_database
from app.db.elasticsearch.sync import sync_measurement


async def create_measurement(measurement: MeasurementCreate, user_id: str) -> MeasurementInDB:
    """
    Create a new body measurement record.
    
    Args:
        measurement: Measurement data
        user_id: User ID
        
    Returns:
        Created measurement
    """
    db = await get_database()
    
    measurement_in_db = MeasurementInDB(
        **measurement.dict(),
        user_id=ObjectId(user_id),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        date=measurement.date or datetime.utcnow()
    )
    
    result = await db.measurements.insert_one(measurement_in_db.dict(by_alias=True))
    measurement_in_db.id = result.inserted_id
    
    # Index in Elasticsearch
    await sync_measurement(measurement_in_db.dict(by_alias=True))
    
    return measurement_in_db


async def get_measurement_by_id(measurement_id: str) -> Optional[MeasurementInDB]:
    """
    Get a measurement by ID.
    
    Args:
        measurement_id: Measurement ID
        
    Returns:
        Measurement or None if not found
    """
    db = await get_database()
    
    measurement_data = await db.measurements.find_one({"_id": ObjectId(measurement_id)})
    if measurement_data:
        return MeasurementInDB(**measurement_data)
    
    return None


async def update_measurement(measurement_id: str, measurement_update: MeasurementUpdate) -> Optional[MeasurementInDB]:
    """
    Update a measurement.
    
    Args:
        measurement_id: Measurement ID
        measurement_update: Measurement update data
        
    Returns:
        Updated measurement or None if not found
    """
    db = await get_database()
    
    # Filter out None values
    update_data = {k: v for k, v in measurement_update.dict().items() if v is not None}
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Update the measurement
    result = await db.measurements.update_one(
        {"_id": ObjectId(measurement_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        # Get the updated measurement
        updated_measurement = await get_measurement_by_id(measurement_id)
        
        # Update in Elasticsearch
        if updated_measurement:
            await sync_measurement(updated_measurement.dict(by_alias=True), operation="update")
            
        return updated_measurement
    
    return None


async def delete_measurement(measurement_id: str) -> bool:
    """
    Delete a measurement.
    
    Args:
        measurement_id: Measurement ID
        
    Returns:
        True if measurement was deleted, False otherwise
    """
    db = await get_database()
    
    result = await db.measurements.delete_one({"_id": ObjectId(measurement_id)})
    
    # Delete from Elasticsearch
    if result.deleted_count:
        await sync_measurement({"_id": measurement_id}, operation="delete")
        
    return result.deleted_count > 0


async def get_user_measurements(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    measurement_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "date",
    sort_direction: int = -1
) -> List[MeasurementInDB]:
    """
    Get a user's measurements with pagination and filters.
    
    Args:
        user_id: User ID
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        measurement_type: Optional measurement type for filtering
        skip: Number of measurements to skip
        limit: Maximum number of measurements to return
        sort_by: Field to sort by
        sort_direction: Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        List of measurements
    """
    db = await get_database()
    measurements = []
    
    # Build query filters
    filters = {"user_id": ObjectId(user_id)}
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            date_filter["$gte"] = start_datetime
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            date_filter["$lte"] = end_datetime
        filters["date"] = date_filter
    
    if measurement_type:
        filters["measurement_type"] = measurement_type
    
    cursor = db.measurements.find(filters).sort(sort_by, sort_direction).skip(skip).limit(limit)
    
    async for measurement_data in cursor:
        measurements.append(MeasurementInDB(**measurement_data))
    
    return measurements


async def get_measurement_history(
    user_id: str,
    measurement_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get a history of a specific measurement type for a user.
    
    Args:
        user_id: User ID
        measurement_type: Measurement type
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        limit: Maximum number of measurements to return
        
    Returns:
        List of measurement history records
    """
    db = await get_database()
    
    # Build query filters
    filters = {
        "user_id": ObjectId(user_id),
        "measurement_type": measurement_type
    }
    
    if start_date or end_date:
        date_filter = {}
        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            date_filter["$gte"] = start_datetime
        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            date_filter["$lte"] = end_datetime
        filters["date"] = date_filter
    
    # Project only fields necessary for history
    projection = {
        "_id": 1,
        "date": 1,
        "value": 1,
        "measurement_type": 1,
        "unit": 1
    }
    
    cursor = db.measurements.find(
        filters, 
        projection
    ).sort("date", 1).limit(limit)
    
    history = []
    async for measurement_data in cursor:
        # Convert ObjectId to string
        measurement_data["_id"] = str(measurement_data["_id"])
        history.append(measurement_data)
    
    return history


async def get_latest_measurements(user_id: str) -> Dict[str, Dict[str, Any]]:
    """
    Get the latest measurement of each type for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary of measurement types with their latest values
    """
    db = await get_database()
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$sort": {"date": -1}},
        {
            "$group": {
                "_id": "$measurement_type",
                "latest": {"$first": "$$ROOT"}
            }
        }
    ]
    
    result = await db.measurements.aggregate(pipeline).to_list(length=None)
    
    latest_measurements = {}
    for item in result:
        measurement_type = item["_id"]
        measurement = item["latest"]
        
        # Convert ObjectId to string
        measurement["_id"] = str(measurement["_id"])
        measurement["user_id"] = str(measurement["user_id"])
        
        latest_measurements[measurement_type] = measurement
    
    return latest_measurements 
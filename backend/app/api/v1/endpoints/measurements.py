from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from datetime import datetime, date

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.measurement import Measurement, MeasurementCreate, MeasurementUpdate, MeasurementHistory


router = APIRouter()


# Mock database functions - would be replaced with actual MongoDB operations
async def create_measurement_db(measurement: MeasurementCreate, user_id: str) -> Measurement:
    """Create a measurement record in the database."""
    # This would be replaced with actual DB call
    measurement_id = str(ObjectId())
    return Measurement(
        id=measurement_id,
        user_id=user_id,
        **measurement.dict(),
        created_at=datetime.utcnow()
    )


async def get_measurement_by_id_db(measurement_id: str) -> Optional[Measurement]:
    """Get a measurement by ID from the database."""
    # This would be replaced with actual DB call
    return None


async def update_measurement_db(measurement_id: str, measurement_update: MeasurementUpdate) -> Optional[Measurement]:
    """Update a measurement in the database."""
    # This would be replaced with actual DB call
    return None


async def delete_measurement_db(measurement_id: str) -> bool:
    """Delete a measurement from the database."""
    # This would be replaced with actual DB call
    return True


async def get_user_measurements_db(user_id: str, start_date: date = None, end_date: date = None, skip: int = 0, limit: int = 100) -> List[Measurement]:
    """Get a user's measurements from the database with date range filter."""
    # This would be replaced with actual DB call
    return []


async def get_measurement_history_db(user_id: str, measurement_types: List[str] = None, start_date: date = None, end_date: date = None) -> MeasurementHistory:
    """Get a user's measurement history for specified types."""
    # This would be replaced with actual DB call
    return MeasurementHistory(
        dates=[],
        weights=[],
        body_fat=[],
        measurements={}
    )


@router.post("/", response_model=Measurement)
async def create_measurement(
    measurement: MeasurementCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new body measurement record.
    
    Args:
        measurement: Measurement data
        current_user: Current authenticated user
        
    Returns:
        Created measurement
    """
    return await create_measurement_db(measurement, str(current_user.id))


@router.get("/{measurement_id}", response_model=Measurement)
async def read_measurement(
    measurement_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a measurement by ID.
    
    Args:
        measurement_id: Measurement ID
        current_user: Current authenticated user
        
    Returns:
        Measurement
    """
    measurement = await get_measurement_by_id_db(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if measurement.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return measurement


@router.put("/{measurement_id}", response_model=Measurement)
async def update_measurement(
    measurement_id: str,
    measurement_update: MeasurementUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a measurement.
    
    Args:
        measurement_id: Measurement ID
        measurement_update: Measurement update data
        current_user: Current authenticated user
        
    Returns:
        Updated measurement
    """
    measurement = await get_measurement_by_id_db(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if measurement.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    updated_measurement = await update_measurement_db(measurement_id, measurement_update)
    return updated_measurement


@router.delete("/{measurement_id}", response_model=bool)
async def delete_measurement(
    measurement_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a measurement.
    
    Args:
        measurement_id: Measurement ID
        current_user: Current authenticated user
        
    Returns:
        True if measurement was deleted
    """
    measurement = await get_measurement_by_id_db(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if measurement.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_measurement_db(measurement_id)
    return result


@router.get("/", response_model=List[Measurement])
async def read_user_measurements(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's measurements with optional date range filter.
    
    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        
    Returns:
        List of measurements
    """
    return await get_user_measurements_db(str(current_user.id), start_date, end_date, skip=skip, limit=limit)


@router.get("/history", response_model=MeasurementHistory)
async def read_measurement_history(
    measurement_types: Optional[List[str]] = Query(None),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's measurement history for specified types.
    
    Args:
        measurement_types: Types of measurements to include (weight, body_fat, chest, waist, etc.)
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        current_user: Current authenticated user
        
    Returns:
        Measurement history with trends
    """
    return await get_measurement_history_db(str(current_user.id), measurement_types, start_date, end_date)


@router.get("/latest", response_model=Measurement)
async def read_latest_measurement(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's latest measurement.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Latest measurement or 404 if none found
    """
    # Get the latest measurement
    measurements = await get_user_measurements_db(str(current_user.id), limit=1)
    
    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No measurements found",
        )
    
    return measurements[0]

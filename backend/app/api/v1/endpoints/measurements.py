
from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from datetime import datetime, date

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.measurement import Measurement, MeasurementCreate, MeasurementUpdate, MeasurementHistory
from app.db.mongodb.measurements import (
    create_measurement,
    get_measurement_by_id,
    update_measurement,
    delete_measurement,
    get_user_measurements,
    get_measurement_history,
    get_latest_measurements
)


router = APIRouter()


@router.post("/", response_model=Measurement)
async def create_measurement_endpoint(
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
    return await create_measurement(measurement, str(current_user.id))


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
    measurement = await get_measurement_by_id(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if str(measurement.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return measurement


@router.put("/{measurement_id}", response_model=Measurement)
async def update_measurement_endpoint(
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
    measurement = await get_measurement_by_id(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if str(measurement.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    updated_measurement = await update_measurement(measurement_id, measurement_update)
    return updated_measurement


@router.delete("/{measurement_id}", response_model=bool)
async def delete_measurement_endpoint(
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
    measurement = await get_measurement_by_id(measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )
    
    # Check if the measurement belongs to the current user
    if str(measurement.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    result = await delete_measurement(measurement_id)
    return result


@router.get("/", response_model=List[Measurement])
async def read_user_measurements(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    measurement_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's measurements with optional date range and type filter.
    
    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        measurement_type: Optional measurement type filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        
    Returns:
        List of measurements
    """
    return await get_user_measurements(
        str(current_user.id), 
        start_date, 
        end_date, 
        measurement_type,
        skip=skip, 
        limit=limit
    )


@router.get("/history/{measurement_type}", response_model=List[Dict[str, Any]])
async def read_measurement_history_endpoint(
    measurement_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get history of a specific measurement type.
    
    Args:
        measurement_type: Type of measurement to track
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        limit: Maximum number of records to return
        current_user: Current authenticated user
        
    Returns:
        List of measurement history entries
    """
    return await get_measurement_history(
        str(current_user.id),
        measurement_type,
        start_date,
        end_date,
        limit
    )


@router.get("/latest", response_model=Dict[str, Dict[str, Any]])
async def read_latest_measurements(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user's latest measurement of each type.
    
    Args:
        current_user: Current authenticated user
        
    Returns:

        Dictionary of measurement types with latest values
    """
    return await get_latest_measurements(str(current_user.id))

    
    # Get the latest measurement
    measurements = await get_user_measurements_db(str(current_user.id), limit=1)
    
    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No measurements found",
        )
    
    return measurements[0]


from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_active_user
from app.models.user import User
from app.db.elasticsearch.indices import create_indices, delete_indices
from app.db.elasticsearch.sync import sync_all_data


router = APIRouter()


@router.post("/elasticsearch/reindex", response_model=Dict[str, Any])
async def reindex_elasticsearch(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Reindex all data from MongoDB to Elasticsearch.
    Admin only endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary with count of documents indexed for each entity type
    """
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this operation",
        )
    
    # Re-create indices
    await delete_indices()
    await create_indices()
    
    # Sync all data
    counts = await sync_all_data()
    
    return {
        "success": True,
        "message": "Elasticsearch indices recreated and data reindexed",
        "document_counts": counts
    }


@router.post("/elasticsearch/create-indices", response_model=Dict[str, Any])
async def create_elasticsearch_indices(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create Elasticsearch indices if they don't exist.
    Admin only endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this operation",
        )
    
    # Create indices
    await create_indices()
    
    return {
        "success": True,
        "message": "Elasticsearch indices created"
    }


@router.delete("/elasticsearch/indices", response_model=Dict[str, Any])
async def delete_elasticsearch_indices(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete all Elasticsearch indices.
    Admin only endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this operation",
        )
    
    # Delete indices
    await delete_indices()
    
    return {
        "success": True,
        "message": "Elasticsearch indices deleted"
    } 
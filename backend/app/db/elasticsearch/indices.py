from typing import Dict, List, Optional, Any
from elasticsearch import AsyncElasticsearch
from app.db.elasticsearch.elasticsearch import get_elasticsearch_client
from app.core.config import settings

# Define index names
WORKOUT_INDEX = "workouts"
USER_INDEX = "users"
FOOD_LOG_INDEX = "food_logs"
MEASUREMENT_INDEX = "measurements"
GOAL_INDEX = "goals"
SOCIAL_POST_INDEX = "social_posts"

# Define mappings for each index
INDEX_MAPPINGS = {
    WORKOUT_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                "description": {"type": "text", "analyzer": "english"},
                "duration": {"type": "integer"},
                "calories_burned": {"type": "integer"},
                "exercises": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                        "sets": {"type": "integer"},
                        "reps": {"type": "integer"},
                        "weight": {"type": "float"},
                        "notes": {"type": "text"}
                    }
                },
                "date": {"type": "date"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "is_public": {"type": "boolean"},
                "likes_count": {"type": "integer"},
                "comments_count": {"type": "integer"}
            }
        }
    },
    USER_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "email": {"type": "keyword"},
                "username": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "bio": {"type": "text"},
                "profile_picture": {"type": "keyword"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "date"},
                "following_count": {"type": "integer"},
                "followers_count": {"type": "integer"}
            }
        }
    },
    FOOD_LOG_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "date": {"type": "date"},
                "meals": {
                    "type": "nested",
                    "properties": {
                        "meal_type": {"type": "keyword"},
                        "foods": {
                            "type": "nested",
                            "properties": {
                                "name": {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                                "serving_size": {"type": "float"},
                                "serving_unit": {"type": "keyword"},
                                "calories": {"type": "integer"},
                                "protein": {"type": "float"},
                                "carbs": {"type": "float"},
                                "fat": {"type": "float"}
                            }
                        }
                    }
                },
                "total_calories": {"type": "integer"},
                "total_protein": {"type": "float"},
                "total_carbs": {"type": "float"},
                "total_fat": {"type": "float"},
                "water_intake": {"type": "integer"},
                "notes": {"type": "text"},
                "created_at": {"type": "date"}
            }
        }
    },
    MEASUREMENT_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "date": {"type": "date"},
                "weight": {"type": "float"},
                "height": {"type": "float"},
                "body_fat": {"type": "float"},
                "chest": {"type": "float"},
                "waist": {"type": "float"},
                "hips": {"type": "float"},
                "notes": {"type": "text"},
                "created_at": {"type": "date"}
            }
        }
    },
    GOAL_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "english", "fields": {"keyword": {"type": "keyword"}}},
                "description": {"type": "text", "analyzer": "english"},
                "goal_type": {"type": "keyword"},
                "target_value": {"type": "float"},
                "current_value": {"type": "float"},
                "start_value": {"type": "float"},
                "target_date": {"type": "date"},
                "status": {"type": "keyword"},
                "progress_percentage": {"type": "float"},
                "days_remaining": {"type": "integer"},
                "created_at": {"type": "date"}
            }
        }
    },
    SOCIAL_POST_INDEX: {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "user_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "content": {"type": "text", "analyzer": "english"},
                "workout_id": {"type": "keyword"},
                "media_urls": {"type": "keyword"},
                "created_at": {"type": "date"},
                "likes_count": {"type": "integer"},
                "comments_count": {"type": "integer"}
            }
        }
    }
}


async def create_indices() -> None:
    """
    Create all required Elasticsearch indices if they don't exist.
    """
    client = await get_elasticsearch_client()
    
    for index_name, index_config in INDEX_MAPPINGS.items():
        exists = await client.indices.exists(index=index_name)
        if not exists:
            await client.indices.create(index=index_name, body=index_config)
            print(f"Created Elasticsearch index: {index_name}")


async def delete_indices() -> None:
    """
    Delete all Elasticsearch indices. Use with caution!
    """
    client = await get_elasticsearch_client()
    
    for index_name in INDEX_MAPPINGS.keys():
        exists = await client.indices.exists(index=index_name)
        if exists:
            await client.indices.delete(index=index_name)
            print(f"Deleted Elasticsearch index: {index_name}")


async def index_document(index: str, doc_id: str, document: Dict[str, Any]) -> None:
    """
    Index a document in Elasticsearch.
    
    Args:
        index: The index name
        doc_id: The document ID
        document: The document to index
    """
    client = await get_elasticsearch_client()
    await client.index(index=index, id=doc_id, document=document, refresh=True)


async def delete_document(index: str, doc_id: str) -> None:
    """
    Delete a document from Elasticsearch.
    
    Args:
        index: The index name
        doc_id: The document ID to delete
    """
    client = await get_elasticsearch_client()
    await client.delete(index=index, id=doc_id, refresh=True)


async def update_document(index: str, doc_id: str, partial_document: Dict[str, Any]) -> None:
    """
    Update a document in Elasticsearch.
    
    Args:
        index: The index name
        doc_id: The document ID
        partial_document: The partial document for update
    """
    client = await get_elasticsearch_client()
    await client.update(index=index, id=doc_id, doc=partial_document, refresh=True)


async def bulk_index_documents(index: str, documents: List[Dict[str, Any]]) -> None:
    """
    Bulk index multiple documents in Elasticsearch.
    
    Args:
        index: The index name
        documents: List of documents with _id field
    """
    if not documents:
        return
        
    client = await get_elasticsearch_client()
    
    operations = []
    for doc in documents:
        # Extract the ID and remove from document
        doc_id = doc.pop("_id", None)
        if not doc_id:
            continue
            
        operations.append({"index": {"_index": index, "_id": doc_id}})
        operations.append(doc)
    
    if operations:
        await client.bulk(operations=operations, refresh=True) 
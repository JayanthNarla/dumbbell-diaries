from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from typing import Optional

async def connect_to_elasticsearch() -> AsyncElasticsearch:
    """
    Create an Elasticsearch connection.
    
    Returns:
        AsyncElasticsearch: Elasticsearch client instance
    """
    es_client = AsyncElasticsearch(settings.ELASTICSEARCH_URI)
    return es_client


async def close_elasticsearch_connection(client: Optional[AsyncElasticsearch]) -> None:
    """
    Close Elasticsearch connection.
    
    Args:
        client: Elasticsearch client instance to close
    """
    if client:
        await client.close()


async def get_elasticsearch_client():
    """
    Get Elasticsearch client instance.
    
    Returns:
        Elasticsearch client instance
    """
    from app.main import app
    return app.state.elasticsearch_client 
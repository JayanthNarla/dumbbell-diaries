from typing import Any, Annotated
from bson import ObjectId
from pydantic import BeforeValidator, ConfigDict

# Function for ObjectId validation
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        if not v:  # Handle empty string
            return None
        try:
            return ObjectId(v)
        except Exception:
            return None
    if v is None:
        return None
    raise ValueError(f"Cannot convert {v} to ObjectId")

# Type for ObjectId fields (Pydantic v2 style)
PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

# Base class for MongoDB models
class MongoBaseModel:
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str},
        from_attributes=True
    )
    
    # Handle conversion of ObjectId when using model_dump
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        return data 
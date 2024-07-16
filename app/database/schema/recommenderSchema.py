from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, constr, validator, Field
from bson.objectid import ObjectId
from datetime import datetime
import re

class content(BaseModel):
    planetId : str | None = None
    tribeId : str | None = None

class interaction(BaseModel):
    contentList : List[str] | None = None

class recommendationTraining(BaseModel):
    userId: str
    modelName: str
    filterType: str
    filterId: str
    amount: int
    
class ContentItem(BaseModel):
    eventStrength: float
    contentId: str
    content: str
    contentType: str

    @validator('contentId')
    def validate_objectid(cls, v):
        objectid_pattern = re.compile(r"^[0-9a-fA-F]{24}$")
        if not objectid_pattern.match(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return v
    
class PopularityContent(BaseModel):
    popularContentList: List[ContentItem]
    createdAt: datetime = Field(default_factory=datetime.utcnow)
from pydantic import BaseModel, EmailStr, Field
from datetime import date as d
from typing import Optional


class MetadataClass(BaseModel):
    title: str
    author: str
    date: d = Field(default_factory=d.today)
    description: Optional[str] = None
    author_email: Optional[EmailStr] = None
    avatar: Optional[str] = None

    class Config:
        validate_assignment = True

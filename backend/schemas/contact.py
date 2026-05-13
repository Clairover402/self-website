"""Contact Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime


class ContactCreate(BaseModel):
    name: str = Field(..., description="Sender name")
    email: str = Field(..., description="Sender email")
    message: str = Field(..., description="Message body")


class Contact(ContactCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

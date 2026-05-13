"""Contact router - handles visitor contact form submissions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.contact import ContactCreate, Contact
from models.contact import ContactModel
from utils.result import Result

router = APIRouter()


@router.post("/", response_model=Result[Contact])
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    """Submit a contact form message."""
    model = ContactModel(
        name=contact.name,
        email=contact.email,
        message=contact.message,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return Result.ok(data=Contact.model_validate(model))

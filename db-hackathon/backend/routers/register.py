from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer, SessionLocal
from backend.services.farmer_service import FarmerService
import os


router = APIRouter()


class FarmerRegister(BaseModel):
    aadhar_id: str
    name: str
    email: str
    phone: str
    password_hash: str
    state: str
    city: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register_farmer")
def register_farmer(farmer: FarmerRegister, db: Session = Depends(get_db)):
    repo = FarmerRepository()
    if db.query(Farmer).filter(Farmer.aadhar_id == farmer.aadhar_id).first():
        raise HTTPException(status_code=400, detail="Aadhar ID already registered")
    else:
        farmer_service = FarmerService()
        farmer_service.create_farmer(farmer.model_dump())
        return {"msg": "Registration successful"}


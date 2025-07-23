from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer, SessionLocal
import os

router = APIRouter()

class FarmerLogin(BaseModel):
    aadhar_id: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login_farmer")
def login_farmer(login: FarmerLogin, db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.aadhar_id == login.aadhar_id).filter(Farmer.password_hash == login.password).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful"}


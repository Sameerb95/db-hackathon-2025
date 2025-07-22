from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import Farmer, FarmerRepository, Investor, InvestorRepository, SessionLocal
from passlib.context import CryptContext
from jose import jwt
import os

SECRET_KEY = os.environ.get("JWT_SECRET", "k3J8n2kL9s8d7f6g5h4j3k2l1m0n9b8v7c6x5z4a3s2d1f0g")
ALGORITHM = "HS256"

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class FarmerRegister(BaseModel):
    aadhar_id: str
    name: str
    email: str
    phone: str
    password: str

class FarmerLogin(BaseModel):
    aadhar_id: str
    password: str

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
    hashed_password = pwd_context.hash(farmer.password)
    db_farmer = Farmer(
        aadhar_id=farmer.aadhar_id,
        name=farmer.name,
        email=farmer.email,
        phone=farmer.phone,
        password_hash=hashed_password,
    )
    db.add(db_farmer)
    db.commit()
    db.refresh(db_farmer)
    return {"msg": "Registration successful"}

@router.post("/login_farmer")
def login_farmer(login: FarmerLogin, db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.aadhar_id == login.aadhar_id).first()
    if not farmer or not pwd_context.verify(login.password, farmer.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": farmer.aadhar_id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

class InvestorRegister(BaseModel):
    aadhar_id: str
    name: str
    email: str
    phone: str
    password: str

class InvestorLogin(BaseModel):
    aadhar_id: str
    password: str

@router.post("/register_investor")
def register_investor(investor: InvestorRegister, db: Session = Depends(get_db)):
    if db.query(Investor).filter(Investor.aadhar_id == investor.aadhar_id).first():
        raise HTTPException(status_code=400, detail="Aadhar ID already registered")
    hashed_password = pwd_context.hash(investor.password)
    db_investor = Investor(
        aadhar_id=investor.aadhar_id,
        name=investor.name,
        email=investor.email,
        phone=investor.phone,
        password_hash=hashed_password,
    )
    db.add(db_investor)
    db.commit()
    db.refresh(db_investor)
    return {"msg": "Investor registration successful"}

@router.post("/login_investor")
def login_investor(login: InvestorLogin, db: Session = Depends(get_db)):
    investor = db.query(Investor).filter(Investor.aadhar_id == login.aadhar_id).first()
    if not investor or not pwd_context.verify(login.password, investor.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": investor.aadhar_id, "role": "investor"}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
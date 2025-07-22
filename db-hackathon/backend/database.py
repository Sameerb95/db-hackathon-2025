from sqlalchemy import Boolean, DateTime, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL
DATABASE_URL = "sqlite:///./database.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Define your schema (models) here
class Project(Base):
    __tablename__ = "projects"
    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    amount_needed = Column(Integer)
    interest_rate = Column(Integer)
    farmer_aadhar_id = Column(String, index=True)
    duration_in_months = Column(Integer)
    is_active = Column(Boolean)
    amount_repaid_yn = Column(Boolean)
    crop_type = Column(String)
    land_area = Column(Integer)
    

class Farmer(Base):
    __tablename__ = "farmers"
    aadhar_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    wallet_address = Column(String, index=True)
    contract_address = Column(String, index=True)
    total_loans = Column(Integer)
    total_loans_repaid = Column(Integer)
    total_on_time_loans_repaid = Column(Integer)
    total_loans_remaining = Column(Integer)
    total_loans_defaulted = Column(Integer)
    average_interest_rate = Column(Integer)
    confidence_score = Column(Integer)
    state = Column(String)
    city = Column(String)

class Investor(Base):
    __tablename__ = "investors"
    aadhar_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    wallet_address = Column(String, index=True)
    contract_address = Column(String, index=True)
    total_investments = Column(Integer)
    total_investments_repaid = Column(Integer)

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(Integer, primary_key=True, index=True)
    farmer_aadhar_id = Column(String, index=True)
    investor_aadhar_id = Column(String, index=True)
    amount = Column(Integer)
    project_id = Column(Integer, index=True)
    status = Column(String)
    timestamp = Column(DateTime)

# Create the tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)
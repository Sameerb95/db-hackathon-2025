from backend.database import Farmer, SessionLocal

class FarmerRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_farmer(self, farmer: Farmer):
        self.db.add(farmer)
        self.db.commit()
        self.db.refresh(farmer)
        return farmer
    
    def get_farmer_by_id(self, aadhar_id: str):
        return self.db.query(Farmer).filter(Farmer.aadhar_id == aadhar_id).first()
    
    def get_all_farmers(self):
        return self.db.query(Farmer).all() 
from backend.database import Investor, SessionLocal

class InvestorRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_investor(self, investor: Investor):
        self.db.add(investor)
        self.db.commit()
        self.db.refresh(investor)
        return investor
    
    def get_investor_by_id(self, aadhar_id: str):
        return self.db.query(Investor).filter(Investor.aadhar_id == aadhar_id).first()
    
    def get_all_investors(self):
        return self.db.query(Investor).all() 
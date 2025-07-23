from backend.repositories.investor_repository import InvestorRepository
from backend.database import Investor

class InvestorService:
    def __init__(self):
        self.investor_repository = InvestorRepository()

    def create_investor(self, data):
        investor = Investor(
            aadhar_id=data['aadhar_id'],
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            address=data['address'],
            amount_invested=data['amount_invested'],
            interest_rate=data['interest_rate'],
            duration_in_months=data['duration_in_months'],
            crop_type=data['crop_type'],
            land_area=data['land_area'],
            is_active=True,
            amount_repaid_yn=False
        )
        return self.investor_repository.add_investor(investor)
    
    def get_investor_by_id(self, aadhar_id: str):
        return self.investor_repository.get_investor_by_id(aadhar_id)
    
    def get_all_investors(self):
        return self.investor_repository.get_all_investors()
    
    def get_investor_by_name(self, name: str):
        return self.investor_repository.get_investor_by_name(name)
    
    def get_investor_by_email(self, email: str):
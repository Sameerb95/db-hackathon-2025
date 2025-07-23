from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer

class FarmerService:
    def __init__(self):
        self.farmer_repository = FarmerRepository()

    def create_farmer(self, data):
        farmer = Farmer(
            aadhar_id=data['aadhar_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            wallet_address=1234567890,
            contract_address=data['contract_address'],
            password_hash=data['password_hash'],
            total_loans=0,
            total_loans_repaid=0,
            total_on_time_loans_repaid=0,
            total_loans_remaining=0,
            total_loans_defaulted=0,
            average_interest_rate=0,
            confidence_score=0,
            state=data['state'],
            city=data['city']
        )
        return self.farmer_repository.add_farmer(farmer)
    
    def get_farmer_by_id(self, aadhar_id: str):
        return self.farmer_repository.get_farmer_by_id(aadhar_id)
    
    def get_all_farmers(self):
        return self.farmer_repository.get_all_farmers()

    
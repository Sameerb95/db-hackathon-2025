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
            phone=data['phone'],
            wallet_address=1234567890,
            contract_address=data['contract_address'],
            password_hash=data['password_hash']
        )
        return self.investor_repository.add_investor(investor)
    
    def get_investor_by_id(self, aadhar_id: str):
        return self.investor_repository.get_investor_by_id(aadhar_id)
    
    def get_all_investors(self):
        return self.investor_repository.get_all_investors()
    
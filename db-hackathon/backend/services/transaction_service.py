from backend.repositories.transaction_repository import TransactionRepository
from backend.database import Transaction
from datetime import datetime

class TransactionService:
    def __init__(self):
        self.transaction_repository = TransactionRepository()

    def create_transaction(self, data):
        transaction = Transaction(
            transaction_id=1,
            farmer_aadhar_id=data['farmer_aadhar_id'],
            investor_aadhar_id=data['investor_aadhar_id'],
            amount=data['amount'],
            project_id=data['project_id'],
            status="completed",
            timestamp=datetime.now()
        )
        return self.transaction_repository.add_transaction(transaction)

    def get_transactions_by_farmer_aadhar_id(self, farmer_aadhar_id: str):
        return self.transaction_repository.get_transactions_by_farmer_aadhar_id(farmer_aadhar_id)
    
    def get_transactions_by_investor_aadhar_id(self, investor_aadhar_id: str):
        return self.transaction_repository.get_transactions_by_investor_aadhar_id(investor_aadhar_id)
    
    def get_transactions_by_project_id(self, project_id: int):
        return self.transaction_repository.get_transactions_by_project_id(project_id)
    
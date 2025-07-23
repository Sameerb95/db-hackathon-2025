from backend.repositories.transaction_repository import TransactionRepository
from backend.database import Transaction
from datetime import datetime

class TransactionService:
    def __init__(self):
        self.transaction_repository = TransactionRepository()

    def create_transaction(self, transaction_id, farmer_aadhar_id, investor_aadhar_id, amount, project_id):
        transaction = Transaction(
            transaction_id=transaction_id,
            farmer_aadhar_id=farmer_aadhar_id,
            investor_aadhar_id=investor_aadhar_id,
            amount=amount,
            project_id=project_id,
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
    
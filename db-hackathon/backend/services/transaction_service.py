from backend.repositories.transaction_repository import TransactionRepository
from backend.database import Transaction

class TransactionService:
    def __init__(self):
        self.transaction_repository = TransactionRepository()

    def create_transaction(self, data):
        transaction = Transaction(
            project_id=data['project_id'],
            amount=data['amount'],
            transaction_type=data['transaction_type'],
            transaction_date=data['transaction_date']
        )
        return self.transaction_repository.add_transaction(transaction)
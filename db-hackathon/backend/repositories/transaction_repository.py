from backend.database import Transaction, SessionLocal

class TransactionRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_transaction(self, transaction: Transaction):
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transaction_by_id(self, transaction_id: int):
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_all_transactions(self):
        return self.db.query(Transaction).all() 
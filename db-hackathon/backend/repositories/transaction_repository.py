from backend.database import Transaction, SessionLocal,get_session

class TransactionRepository:
    def __init__(self):
        self.db = get_session()

    def add_transaction(self, transaction: Transaction):
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transaction_by_id(self, transaction_id: int):
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_all_transactions(self):
        return self.db.query(Transaction).all() 

    def get_transactions_by_farmer_aadhar_id(self, farmer_aadhar_id: str):
        return self.db.query(Transaction).filter(Transaction.farmer_aadhar_id == farmer_aadhar_id).order_by(Transaction.timestamp.desc()).all()
    
    
    def get_transactions_by_project_id(self, project_id: int):
        return self.db.query(Transaction).filter(Transaction.project_id == project_id).all()
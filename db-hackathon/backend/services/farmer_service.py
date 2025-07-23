from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer
import subprocess
import sys

class FarmerService:
    def __init__(self):
        self.farmer_repository = FarmerRepository()

    def create_farmer(self, data):
        self.contract_address, self.wallet_address = self.deploy_contract_and_get_address()
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
            confidence_score=40,
            state=data['state'],
            city=data['city']
        )
        return self.farmer_repository.add_farmer(farmer)
    
    def get_farmer_by_id(self, aadhar_id: str):
        return self.farmer_repository.get_farmer_by_id(aadhar_id)
    
    def get_all_farmers(self):
        return self.farmer_repository.get_all_farmers()


    def deploy_contract_and_get_address(self):
        """
        Deploys a new contract using deploy.py and returns the contract address.
        """
        idx = 0 
        command = [
            "brownie", "run", "scripts/deploy.py", "main",
            str(idx),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error deploying contract: {result.stderr.strip()}")
        output = result.stdout.strip()
        contract_address, wallet_address = output.split(",")
        return contract_address, wallet_address
        
    def update_confidence_score(self, aadhar_id: str):
        return self.farmer_repository.update_confidence_score(aadhar_id)
    
  
    
    
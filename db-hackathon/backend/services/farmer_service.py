import logging
from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer
import subprocess
import sys

class FarmerService:
    def __init__(self):
        self.farmer_repository = FarmerRepository()

    def create_farmer(self, data):
        self.contract_address, self.wallet_address,self.idx = self.deploy_contract_and_get_address()
        farmer = Farmer(
            ganache_idx=self.idx,
            aadhar_id=data['aadhar_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            wallet_address=self.wallet_address,
            contract_address=self.contract_address,
            password_hash=data['password_hash'],
            wallet_address=self.wallet_address,
            contract_address= self.contract_address,
            password_hash=data['password'],
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
        with open("ganache_users.txt", "a+") as f:
            f.seek(0)  # Move to the start before reading
            content = f.read().strip()
            print(f"Idx: {content}")
            if content == "":
                idx = 0
            else:
                idx = int(content) + 1

            f.seek(0)
            f.truncate()
            f.write(str(idx))
                
        command = [
            "brownie", "run", "scripts/deploy.py", "main",
            str(idx),
            "--network", "ganache"
        ]
        output = subprocess.check_output(command, text=True)
        lines = output.strip().splitlines()
        last_line = lines[-1]
        contract_address, wallet_address = last_line.split(",")
        return contract_address, wallet_address, idx

    def get_farmer_contract_address(self,aadhar_id:str):
        farmer = self.farmer_repository.get_farmer_by_id(aadhar_id)
        print(f"Farmer: {farmer.contract_address}")
        print(f"Farmer: {farmer.wallet_address}")
        if farmer:
            return (farmer.contract_address , farmer.wallet_address)
        else:
            return "Farmer not found"
        
    def update_confidence_score(self, aadhar_id: str):
        return self.farmer_repository.update_confidence_score(aadhar_id)
    
  
    
    
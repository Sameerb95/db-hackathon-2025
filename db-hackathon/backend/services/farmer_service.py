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
        )

    def generate_contract_address(self, account_index: int, aadhar_id: str):
        import subprocess
        try:
            command = [
                "brownie", "run", "scripts/deploy.py", "main", "--network", "ganache"
            ]
            # Provide the account index as input to the script
            result = subprocess.run(command, input=str(account_index), capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Error deploying contract: {result.stderr.strip()}")
            # Read the last line from deployed_contracts.txt to get the contract address
            with open("deployed_contracts.txt", "r") as f:
                lines = f.readlines()
                if not lines:
                    raise Exception("No contract address found in deployed_contracts.txt")
                last_line = lines[-1].strip()
                # Expected format: AgroFundConnect: <address> <account>
                parts = last_line.split()
                if len(parts) < 3:
                    raise Exception("Malformed contract address line in deployed_contracts.txt")
                contract_address = parts[1]
                main_account = parts[2]
            # Update the farmer's contract_address in the database
            farmer = self.farmer_repository.get_by_id(aadhar_id)
            if not farmer:
                raise Exception(f"Farmer with aadhar_id {aadhar_id} not found.")
            farmer.contract_address = contract_address
            self.farmer_repository.db.commit()
            self.farmer_repository.db.refresh(farmer)
            return {"message": "Contract deployed and address saved successfully!", "contract_address": contract_address, "main_account": main_account}
        except Exception as e:
            return {"error": str(e)}

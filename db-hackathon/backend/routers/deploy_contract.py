from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import sys
from backend.services.farmer_service import FarmerService

router = APIRouter()

class DeployContractRequest(BaseModel):
    in_contract: int
    aadhar_id: str
    name: str
    email: str
    phone: str
    password_hash: str
    state: str
    city: str

@router.post("/deploy_contract")
def deploy_contract(request: DeployContractRequest):
    try:
        # Call the deploy.py script using subprocess
        command = [sys.executable, "db-hackathon/scripts/deploy.py", str(request.in_contract)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error deploying contract: {result.stderr.strip()}")
        # Parse the deployed contract address from the output file
        with open("db-hackathon/deployed_contracts.txt", "r") as f:
            lines = f.readlines()
            last_line = lines[-1]
            contract_address = last_line.split(":")[1].strip().split()[0]
        # Create the farmer using FarmerService
        farmer_service = FarmerService()
        farmer_data = {
            'aadhar_id': request.aadhar_id,
            'name': request.name,
            'email': request.email,
            'phone': request.phone,
            'wallet_address': '1234567890',  # Placeholder, update as needed
            'contract_address': contract_address,
            'password_hash': request.password_hash,
            'state': request.state,
            'city': request.city
        }
        farmer_service.create_farmer(farmer_data)
        return {"message": "Contract deployed and farmer created successfully!", "contract_address": contract_address}
    except Exception as e:
        return {"error": str(e)} 
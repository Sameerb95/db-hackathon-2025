from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback
from backend.services.project_service import ProjectService
from backend.services.transaction_service import TransactionService
from backend.services.farmer_service import FarmerService

router = APIRouter()

class InvestProjectRequest(BaseModel):
    aadhar_id:str
    project_id: int
    amount: int
    investor_account: int 

@router.post("/")
def invest_in_project(request: InvestProjectRequest):
    try:
        project_service = ProjectService()
        transaction_service = TransactionService()
        farmer_service = FarmerService()


        contract_address, wallet_address = farmer_service.get_farmer_contract_address(request.aadhar_id)

        command = [
            "brownie", "run", "scripts/invest_in_project.py", "main",
            str(contract_address),
            str(wallet_address),
            str(request.project_id),
            str(request.amount),
            str(request.investor_account),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(traceback.format_exc())
            raise Exception(f"Error investing in project: {result}")
        transaction_id = result.stdout.split("Investment successful! Transaction hash:")[1].strip()   
        transaction_service.create_transaction(transaction_id,request.aadhar_id, request.investor_account, request.amount, request.project_id)

        project_service.invest_in_project(request.aadhar_id,request.project_id, request.amount)
        return {"message": "Investment successful!","transaction_hash":transaction_id}
    except Exception as e:
        return {"error": str(e)}

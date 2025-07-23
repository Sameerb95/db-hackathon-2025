from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback
from backend.services.project_service import ProjectService
from backend.services.transaction_service import TransactionService
router = APIRouter()

class InvestProjectRequest(BaseModel):
    farmer_aadhar_id: str
    project_id: int
    amount: int
    investor_account: int 

@router.post("/")
def invest_in_project(request: InvestProjectRequest):
    try:
        project_service = ProjectService()
        farmer_aadhar_id = project_service.get_farmer_aadhar_id_by_project_id(request.project_id)
        transaction_service = TransactionService()

        command = [
            "brownie", "run", "scripts/invest_in_project.py", "main",
            str(request.project_id),
            str(request.amount),
            str(request.investor_account),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(traceback.format_exc())
            raise Exception(f"Error investing in project: {result.stderr.strip()}")
        transaction_id = result.stdout.strip()    
        transaction_service.create_transaction(transaction_id,farmer_aadhar_id, request.investor_account, request.amount, request.project_id)
        project_service.invest_in_project(request.project_id, request.amount, farmer_aadhar_id)
        return {"message": "Investment successful!","transaction_hash": result.stdout.split("Investment successful! Transaction hash:")[1].strip()}
    except Exception as e:
        return {"error": str(e)}

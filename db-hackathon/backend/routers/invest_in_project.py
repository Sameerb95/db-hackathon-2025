from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback

router = APIRouter()

class InvestProjectRequest(BaseModel):
    project_id: int
    amount: int
    investor_account: int 

@router.post("/")
def invest_in_project(request: InvestProjectRequest):
    try:
        command = [
            "brownie", "run", "scripts/blockchain/invest_in_project.py", "main",
            str(request.project_id),
            str(request.amount),
            str(request.investor_account),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(traceback.format_exc())
            raise Exception(f"Error investing in project: {result.stderr.strip()}")
        return {"message": "Investment successful!","transaction_hash": result.stdout.split("Investment successful! Transaction hash:")[1].strip()}
    except Exception as e:
        return {"error": str(e)}

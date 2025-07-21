from fastapi import APIRouter
import subprocess
from pydantic import BaseModel

router = APIRouter()

class InvestProjectRequest(BaseModel):
    project_id: int
    amount: int  # Amount in INR

@router.post("/")
def invest_in_project(request: InvestProjectRequest):
    try:
        command = [
            "brownie", "run", "db-hackathon/scripts/invest_in_project.py",
            "--project_id", str(request.project_id),
            "--amount", str(request.amount)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error investing in project: {result.stderr.strip()}")
        return {"message": "Investment successful!", "transaction_hash": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}

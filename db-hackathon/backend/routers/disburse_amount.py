from fastapi import APIRouter
import subprocess
from pydantic import BaseModel

router = APIRouter()

class DisburseAmountRequest(BaseModel):
    project_id: int

@router.post("/")
def disburse_amount(request: DisburseAmountRequest):
    try:
        command = [
            "brownie", "run", "db-hackathon/scripts/disburse_amount.py",
            "--project_id", str(request.project_id)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error disbursing amount: {result.stderr.strip()}")
        return {"message": "Amount disbursed successfully!", "transaction_hash": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}
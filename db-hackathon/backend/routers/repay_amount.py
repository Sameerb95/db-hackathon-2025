from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
from backend.services.farmer_service import FarmerService
from backend.services.project_service import ProjectService

router = APIRouter()

class DisburseAmountRequest(BaseModel):
    project_id: int

@router.post("/")
def repay_amount(request: DisburseAmountRequest):
    try:
        command = [
            "brownie", "run", "scripts/disburse_amount.py", "main",
            str(request.project_id),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr.strip() )
            print(result.stdout.strip())
            raise Exception(f"Error disbursing amount: {result.stderr.strip()}")

        project_service = ProjectService()
        farmer_aadhar_id = project_service.get_farmer_aadhar_id_by_project_id(request.project_id)

        farmer_service = FarmerService()
        updated_score = farmer_service.update_confidence_score(farmer_aadhar_id, increment=5)

        return {"message": "Amount disbursed successfully!", "transaction_hash": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}
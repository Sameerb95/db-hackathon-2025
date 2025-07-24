from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
from backend.services.farmer_service import FarmerService

router = APIRouter()

class DisburseAmountRequest(BaseModel):
    project_id: int
    aadhar_id: str

@router.post("/")
def repay_amount(request: DisburseAmountRequest):

       
    farmer_service = FarmerService()


    contract_address, wallet_address = farmer_service.get_farmer_contract_address(request.aadhar_id)
    try:
        command = [
            "brownie", "run", "scripts/disburse_amount.py", "main",
            str(contract_address),
            str(wallet_address),
            str(request.project_id),
            "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr.strip() )
            print(result.stdout.strip())
            raise Exception(f"Error disbursing amount: {result}")


        from backend.services.project_service import ProjectService
        project_service = ProjectService()
        farmer_aadhar_id = project_service.get_farmer_aadhar_id_by_project_id(request.project_id)

        farmer_service = FarmerService()
        # updated_score = farmer_service.update_confidence_score(farmer_aadhar_id, increment=5)

        return {"message": result.stdout.strip(), "transaction_hash": "1122343434354"}
    except Exception as e:
        return {"error": str(e)}
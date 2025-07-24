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
            "brownie", "run", "scripts/blockchain/disburse_amount.py", "main",
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

        profit_amount = None
        for line in result.stdout.splitlines():
            if line.startswith("PROFIT_AMOUNT:"):
                profit_amount = line.split(":", 1)[1].strip()
                break


        from backend.services.project_service import ProjectService
        project_service = ProjectService()
        farmer_aadhar_id = project_service.get_farmer_aadhar_id_by_project_id(request.project_id)

        farmer_service = FarmerService()
        farmer_service.update_total_loans_repaid(farmer_aadhar_id,profit_amount)
        project_service.update_amount_repaid(request.aadhar_id,request.project_id)
        farmer_service.update_confidence_score(farmer_aadhar_id)

        return {"message": result.stdout.strip(), "transaction_hash": "1122343434354", "profit_amount": profit_amount}
    except Exception as e:
        return {"error": str(e)}
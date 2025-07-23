from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback
from backend.repositories.project_repository import ProjectRepository
from backend.database import Project
from backend.services.project_service import ProjectService
from backend.services.farmer_service import FarmerService
router = APIRouter()

class CreateProjectRequest(BaseModel):
    project_name: str
    project_description: str
    amount_needed: int
    profit_share: int
    farmer_aadhar_id: str
    duration_in_months: int
    crop_type: str
    land_area: int

@router.post("/")
def create_project(request: CreateProjectRequest):
    farmer_service = FarmerService()
    contract_address, wallet_address = farmer_service.get_farmer_contract_address(request.farmer_aadhar_id)

    try:
        command = [
            "brownie", "run", "scripts/create_project.py", "main",
                str(contract_address),
                str(wallet_address),
                str(request.project_name),
                str(request.project_description),
                str(request.amount_needed),
                str(request.profit_share),
                "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result}")
        else:
            project_service = ProjectService()
            project_data = {

                'name': request.project_name,
                'description': request.project_description,
                'amount_needed': request.amount_needed,
                'interest_rate': request.profit_share,
                'farmer_aadhar_id': request.farmer_aadhar_id,
                'duration_in_months': request.duration_in_months,
                'crop_type': request.crop_type,
                'land_area': request.land_area
            }
            project_service.create_project(project_data)
            return {"message": "Project created successfully!", "transaction_hash": result.stdout.split("Project created!")[1].strip()}
    except Exception as e:
        return {"error": str(e)}

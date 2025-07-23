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
                str(request.interest_rate),
                "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result.stderr.strip()}")
        # Parse project_id from result.stdout (should be just the project id)
        project_id = int(result.stdout.strip())
        project_service = ProjectService()
        project_data = {
            'project_id': project_id,
            'name': request.name,
            'description': request.description,
            'amount_needed': request.amount_needed,
            'interest_rate': request.interest_rate,
            'farmer_aadhar_id': request.farmer_aadhar_id,
            'duration_in_months': request.duration_in_months,
            'crop_type': request.crop_type,
            'land_area': request.land_area
        }
        project_service.create_project(project_data)
        return {"message": "Project created successfully!", "project_id": project_id}
    except Exception as e:
        return {"error": str(e)}

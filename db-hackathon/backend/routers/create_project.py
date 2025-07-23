from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback
from backend.repositories.project_repository import ProjectRepository
from backend.database import Project
from backend.services.project_service import ProjectService

router = APIRouter()

class CreateProjectRequest(BaseModel):
    name: str
    description: str
    amount_needed: int
    interest_rate: int
    farmer_aadhar_id: str
    duration_in_months: int
    crop_type: str
    land_area: int

@router.post("/")
def create_project(request: CreateProjectRequest):
    try:
        command = [
            "brownie", "run", "scripts/create_project.py", "main",
                request.project_name,
                request.project_description,
                str(request.amount_needed),
                str(request.profit_share),
                "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result.stderr.strip()}")
        # Use ProjectService to add the project to the database
        project_service = ProjectService()
        project_data = {
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
        return {"message": "Project created successfully!", "transaction_hash": result.stdout.split("Project created!")[1].strip()}
    except Exception as e:
        return {"error": str(e)}

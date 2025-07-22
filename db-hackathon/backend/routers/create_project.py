from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback
from backend.repositories.project_repository import ProjectRepository
from backend.database import Project

router = APIRouter()

class CreateProjectRequest(BaseModel):
    name: str
    description: str
    amount_needed: int
    interest_rate: int
    farmer_aadhar_id: str
    duration_in_months: int
    is_active: bool
    amount_repaid_yn: bool
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
        project_repository = ProjectRepository()
        project = Project(
            name=request.name,
            description=request.description,
            amount_needed=request.amount_needed,
            interest_rate=request.interest_rate,
            farmer_aadhar_id=request.farmer_aadhar_id,
            duration_in_months=request.duration_in_months,
            is_active=request.is_active,
            amount_repaid_yn=request.amount_repaid_yn,
            crop_type=request.crop_type,
            land_area=request.land_area
        )
        created_project = project_repository.add_project(project)
        return {
            "project_id": created_project.project_id,
            "is_active": created_project.is_active
        }
    except Exception as e:
        return {"error": str(e)}

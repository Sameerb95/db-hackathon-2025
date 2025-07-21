from fastapi import APIRouter
import subprocess
from pydantic import BaseModel

router = APIRouter()

class CreateProjectRequest(BaseModel):
    project_name: str
    project_description: str
    amount_needed: int
    profit_share: int

@router.post("/")
def create_project(request: CreateProjectRequest):
    try:
        command = [
            "brownie", "run", "db-hackathon/scripts/create_project.py",
            "--name", request.project_name,
            "--description", request.project_description,
            "--amount_needed", str(request.amount_needed),
            "--profit_share", str(request.profit_share)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result.stderr.strip()}")
        return {"message": "Project created successfully!", "transaction_hash": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}

from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import traceback

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
            "brownie", "run", "scripts/blockchain/create_project.py", "main",
                request.project_name,
                request.project_description,
                str(request.amount_needed),
                str(request.profit_share),
                "--network", "ganache"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result.stderr.strip()}")
        return {"message": "Project created successfully!", "transaction_hash": result.stdout.split("Project created!")[1].strip()}
    except Exception as e:
        return {"error": str(e)}

from fastapi import FastAPI
import subprocess
from pydantic import BaseModel

app = FastAPI()

class CreateProjectRequest(BaseModel):
    project_name: str
    project_description: str
    amount_needed: int
    profit_share: int

@app.post("/create_project/")
def create_project(request: CreateProjectRequest):
    try:
        # Prepare the command to run the create_project.py script
        command = [
            "brownie", "run", "db-hackathon/scripts/create_project.py",
            "--project_name", request.project_name,
            "--project_description", request.project_description,
            "--amount_needed", str(request.amount_needed),
            "--profit_share", str(request.profit_share)
        ]
        
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result.stderr.strip()}")
        
        return {"message": "Project created successfully!", "transaction_hash": result.stdout.strip()}
    
    except Exception as e:
        return {"error": str(e)}
    
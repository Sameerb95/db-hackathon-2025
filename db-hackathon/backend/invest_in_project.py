from fastapi import FastAPI
import subprocess
from pydantic import BaseModel

app = FastAPI()

class InvestProjectRequest(BaseModel):
    project_id: int
    amount: int  # Amount in INR

@app.post("/invest_in_project/")
def invest_in_project(request: InvestProjectRequest):
    try:
        # Prepare the command to run the invest_in_project.py script
        command = [
            "brownie", "run", "db-hackathon/scripts/invest_in_project.py",
            "--project_id", str(request.project_id),
            "--amount", str(request.amount)
        ]
        
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Error investing in project: {result.stderr.strip()}")
        
        return {"message": "Investment successful!", "transaction_hash": result.stdout.strip()}
    
    except Exception as e:
        return {"error": str(e)}
from fastapi import FastAPI
from backend.routers import (
    create_project,
    invest_in_project,
    disburse_amount,
    get_projects,
    deploy_contract,
)

app = FastAPI()

app.include_router(
    create_project.router, prefix="/create_project", tags=["create_project"]
)
app.include_router(
    invest_in_project.router, prefix="/invest_in_project", tags=["invest_in_project"]
)
app.include_router(
    disburse_amount.router, prefix="/disburse_amount", tags=["disburse_amount"]
)
app.include_router(get_projects.router, prefix="/get_projects", tags=["get_projects"])
app.include_router(deploy_contract.router, prefix="/deploy_contract", tags=["deploy_contract"])

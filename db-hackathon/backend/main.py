from fastapi import FastAPI
from backend.routers import (
    create_project,
    invest_in_project,
    repay_amount,
    get_projects,
)
from backend.database import create_tables

app = FastAPI()

create_tables()

app.include_router(
    create_project.router, prefix="/create_project", tags=["create_project"]
)
app.include_router(
    invest_in_project.router, prefix="/invest_in_project", tags=["invest_in_project"]
)
app.include_router(
    repay_amount.router, prefix="/disburse_amount", tags=["disburse_amount"]
)
app.include_router(get_projects.router, prefix="/get_projects", tags=["get_projects"])

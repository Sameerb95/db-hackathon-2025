from fastapi import FastAPI
from backend.routers import (
    create_project,
    invest_in_project,
    repay_amount,
    get_projects,
    login,
    register,
    dashboard,
    mcp_server
    )

from backend.database import create_tables

app = FastAPI()

import os
from brownie import project

loaded_projects = project.get_loaded_projects()

if loaded_projects:
    loaded_proj = loaded_projects[0]
else:
    loaded_proj = project.load(os.getcwd(), name="MyProject")

loaded_proj.load_config()




app.include_router(
    create_project.router, prefix="/create_project", tags=["create_project"]
)
app.include_router(
    invest_in_project.router, prefix="/invest_in_project", tags=["invest_in_project"]
)
app.include_router(
    repay_amount.router, prefix="/disburse_amount", tags=["disburse_amount"]
)
app.include_router(
    get_projects.router, prefix="/get_projects", tags=["get_projects"]
)

app.include_router(
    register.router, prefix="/register", tags=["register"]
)

app.include_router(
    login.router, prefix="/login", tags=["login"]
)

app.include_router(
    dashboard.router, prefix="/dashboard", tags=["dashboard"]
)
app.include_router(mcp_server.router, prefix="/mcp_server", tags=["mcp_server"])
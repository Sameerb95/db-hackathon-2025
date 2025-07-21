from fastapi import FastAPI
from backend.routers import create_project, invest_in_project

app = FastAPI()

app.include_router(create_project.router, prefix="/create_project", tags=["create_project"])
app.include_router(invest_in_project.router, prefix="/invest_in_project", tags=["invest_in_project"])

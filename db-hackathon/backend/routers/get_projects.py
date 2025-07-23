from fastapi import APIRouter
from backend.services.project_service import ProjectService


router = APIRouter()
project_service = ProjectService()

@router.get("/count")
def get_projects_count():
    try:
        count = get_count()
        return {"projects_count": count}
    except Exception as e:
        return {"error": str(e)}


@router.get("/list")
def get_projects_list(aadhar_id:str):
    try:
        projects = project_service.get_project_by_farmer_aadhar_id(aadhar_id)
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/{project_id}")
def get_project_details(project_id: int):   
    try:
        project_details = project_service.get_project_by_id(project_id)
        if project_details:
            return project_details
        else:
            return {"error": "Project not found"}
    except Exception as e:
        return {"error": str(e)}

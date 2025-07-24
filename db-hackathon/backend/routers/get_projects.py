from fastapi import APIRouter
from backend.services.project_service import ProjectService


router = APIRouter()
project_service = ProjectService()


@router.get("/all")
def get_all_projects():
    try:
        projects = project_service.get_all_active_projects()
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}
        
@router.get("/list")
def get_projects_list(aadhar_id:str):
    try:
        projects = project_service.get_project_by_farmer_aadhar_id(aadhar_id)
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/details")
def get_project_details(farmer_aadhar_id: str, project_id: int):   
    try:
        project_details = project_service.get_project_by_id(farmer_aadhar_id, project_id)
        if project_details:
            return project_details
        else:
            return {"error": "Project not found"}
    except Exception as e:
        return {"error": str(e)}

@router.get("/active_projects")
def get_active_projects(aadhar_id:str):
    try:
        projects = project_service.get_all_active_projects_by_aadhar_id(aadhar_id)
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}

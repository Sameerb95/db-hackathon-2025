from fastapi import APIRouter

from scripts.utils import get_projects_count, get_projects, get_project_details

router = APIRouter()


@router.get("/count")
def get_projects_count():
    return {"projects_count": get_projects_count()}


@router.get("/list")
def get_projects():
    try:
        projects = get_projects()
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/{project_id}")
def get_project_details(project_id: int):   
    try:
        project_details = get_project_details(project_id)
        if project_details:
            return project_details
        else:
            return {"error": "Project not found"}
    except Exception as e:
        return {"error": str(e)}

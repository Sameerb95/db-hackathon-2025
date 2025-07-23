from backend.repositories.project_repository import ProjectRepository
from backend.database import Project

class ProjectService:
    def __init__(self):
        self.project_repository = ProjectRepository()

    def create_project(self, data):
        project = Project(
            name=data['name'],
            description=data['description'],
            amount_needed=data['amount_needed'],
            interest_rate=data['interest_rate'],
            farmer_aadhar_id=data['farmer_aadhar_id'],
            duration_in_months=data['duration_in_months'],
            crop_type=data['crop_type'],
            land_area=data['land_area'],
            is_active=True,
            amount_repaid_yn=False
        )
        return self.project_repository.add_project(project)
    
    def get_all_active_projects(self):
        return self.project_repository.get_all_active_projects()
    
    def get_project_by_id(self, project_id: int):
        return self.project_repository.get_project_by_id(project_id)

    def get_farmer_aadhar_id_by_project_id(self, project_id: int):
        return self.project_repository.get_farmer_aadhar_id_by_project_id(project_id) 
    
    def get_project_by_farmer_aadhar_id(self, farmer_aadhar_id: str):
        return self.project_repository.get_project_by_farmer_aadhar_id(farmer_aadhar_id)
    
    def get_project_by_crop_type(self, crop_type: str):
        return self.project_repository.get_project_by_crop_type(crop_type)
    
    def mark_project_completed(self, project_id: int):
        return self.project_repository.update_project_completion(project_id)
    
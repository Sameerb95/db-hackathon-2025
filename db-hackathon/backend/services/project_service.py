from backend.repositories.project_repository import ProjectRepository
from backend.database import Project
from backend.repositories.farmer_repository import FarmerRepository
from backend.services.transaction_service import TransactionService

class ProjectService:
    def __init__(self):
        self.project_repository = ProjectRepository()
        self.transaction_service = TransactionService()
        self.farmer_repository = FarmerRepository()

    def create_project(self, data):
        project = Project(
            project_id=data['project_id'],
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
    
    def invest_in_project(self, project_id: int, amount: int):
        project = self.get_project_by_id(project_id)
        if project:
            if project.is_active:
                project.amount_needed -= amount
                self.project_repository.update_project(project_id, {'amount_needed': project.amount_needed})
                if project.amount_needed == 0:
                    project.is_active = False
                    project.amount_repaid_yn = True
                    farmer_aadhar_id = self.get_farmer_aadhar_id_by_project_id(project_id)
                    farmer = self.farmer_repository.get_farmer_by_id(farmer_aadhar_id)
                    farmer.total_loans += 1
                    farmer.total_loans_remaining += 1
                    self.farmer_repository.update_farmer(farmer_aadhar_id, {'total_loans': farmer.total_loans, 'total_loans_remaining': farmer.total_loans_remaining})
                    self.project_repository.update_project(project_id, {'is_active': project.is_active, 'amount_repaid_yn': project.amount_repaid_yn})
                    return True
            else:
                print("Project is not active")
                return False
        else:
            print("Project not found")
            return False


        

    def get_all_active_projects(self):
        return self.project_repository.get_all_active_projects()
    
    def get_project_by_id(self, project_id: int):
        return self.project_repository.get_project_by_id(project_id)

    def get_farmer_aadhar_id_by_project_id(self, project_id: int):
        return self.project_repository.get_farmer_aadhar_id_by_project_id(project_id) 
    
    def get_project_by_farmer_aadhar_id(self, farmer_aadhar_id: str):
        return self.project_repository.get_projects_by_farmer_aadhar_id(farmer_aadhar_id)
    
    def get_project_by_crop_type(self, crop_type: str):
        return self.project_repository.get_project_by_crop_type(crop_type)
    
    def mark_project_completed(self, project_id: int):
        return self.project_repository.update_project_completion(project_id)
    
    def get_next_project_id(self, farmer_aadhar_id: str):
        return self.project_repository.get_next_project_id(farmer_aadhar_id)
    
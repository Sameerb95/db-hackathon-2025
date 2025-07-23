from backend.database import Project, SessionLocal

class ProjectRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_project(self, project: Project):
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_project_by_id(self, project_id: int):
        return self.db.query(Project).filter(Project.project_id == project_id).first()
    
    def get_all_active_projects(self):
        return self.db.query(Project).filter(Project.is_active == True).order_by(Project.amount_needed.desc()).all()

    def get_projects_by_farmer_aadhar_id(self, farmer_aadhar_id: str):
        return self.db.query(Project).filter(Project.farmer_aadhar_id == farmer_aadhar_id).all()
    
    def get_project_by_crop_type(self, crop_type: str):
        return self.db.query(Project).filter(Project.crop_type == crop_type).all()
    
        
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

    def get_project_by_farmer_aadhar_id_and_project_id(self, farmer_aadhar_id: str, project_id: int):
        return self.db.query(Project).filter(Project.farmer_aadhar_id == farmer_aadhar_id, Project.project_id == project_id).first()
    
    def get_farmer_aadhar_id_by_project_id(self, project_id: int):
        return self.db.query(Project).filter(Project.project_id == project_id).first().farmer_aadhar_id
    
    def get_project_by_crop_type(self, crop_type: str):
        return self.db.query(Project).filter(Project.crop_type == crop_type).all()
    
    def update_project(self,project_id:int,data:dict):
        project = self.get_project_by_id(project_id)
        if project:
            for key, value in data.items():
                setattr(project, key, value)
            self.db.commit()
            self.db.refresh(project)
        return project

    def get_next_project_id(self, farmer_aadhar_id: str):
        last = self.db.query(Project).filter_by(farmer_aadhar_id=farmer_aadhar_id).order_by(Project.project_id.desc()).first()
        if last is None:
            return 0
        return last.project_id + 1
        
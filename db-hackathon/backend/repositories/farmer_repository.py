from backend.database import Farmer, SessionLocal, Project

class FarmerRepository:
    def __init__(self):
        self.db = SessionLocal()

    def add_farmer(self, farmer: Farmer):
        self.db.add(farmer)
        self.db.commit()
        self.db.refresh(farmer)
        return farmer
    
    def get_farmer_by_id(self, aadhar_id: str):
        return self.db.query(Farmer).filter(Farmer.aadhar_id == aadhar_id).first()
    
    def get_all_farmers(self):
        return self.db.query(Farmer).all()

    def update_farmer(self, aadhar_id: str, data: dict):
        farmer = self.get_farmer_by_id(aadhar_id)
        if farmer:
            for key, value in data.items():
                setattr(farmer, key, value)
            self.db.commit()
            self.db.refresh(farmer)
        return farmer

    def update_confidence_score(self, aadhar_id: str):
        """
        Updates the confidence score of the farmer
        """
        farmer = self.get_farmer_by_id(aadhar_id)
        if not farmer:
            return None

        total_projects = self.db.query(Project).filter(Project.farmer_aadhar_id == aadhar_id).count()
        projects_repaid = self.db.query(Project).filter(
                                    Project.farmer_aadhar_id == aadhar_id,
                                    Project.amount_repaid_yn == True,
                                    ).count()
#             on_time_loans = db.query(Loan).filter(Project.farmer_aadhar_id == aadhar_id, Loan.repaid_on <= Loan.due_date).count()
        avg_interest_rate = self.db.query(func.avg(Project.interest_rate)).filter(
                    Project.farmer_aadhar_id == aadhar_id,
                    Project.is_active == False,
                    Project.amount_repaid_yn == True
                ).scalar() or 0
        # Score computation
        total = projects_repaid + (total_projects - projects_repaid) + 1
        ratio_repaid = projects_repaid / total
#             timeliness = on_time_loans / (loans_repaid + 1)
        interest_factor = min(avg_interest_rate / 100, 1)

#             new_score = (ratio_repaid * 0.4 + timeliness * 0.4 + interest_factor * 0.2) * 100
        new_score = (ratio_repaid * 0.6 + interest_factor * 0.4) * 100
        farmer.score = round(new_score, 2)
        self.db.commit()
        self.db.refresh(farmer)
        return farmer.confidence_score
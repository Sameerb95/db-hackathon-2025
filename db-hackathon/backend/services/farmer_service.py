from backend.repositories.farmer_repository import FarmerRepository
from backend.database import Farmer

class FarmerService:
    def __init__(self):
        self.farmer_repository = FarmerRepository()

    def create_farmer(self, data):
        farmer = Farmer(
            aadhar_id=data['aadhar_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
        )


    
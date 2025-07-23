from backend.repositories.farmer_repository import FarmerRepository

class FarmerService:
    def __init__(self):
        self.farmer_repository = FarmerRepository()

    
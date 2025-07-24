from fastapi import APIRouter
from backend.services.project_service import ProjectService
from backend.services.transaction_service import TransactionService
from backend.services.farmer_service import FarmerService
from scripts.utils import get_farmer_wallet_balance


router = APIRouter()

project_service = ProjectService()
transaction_service = TransactionService()
farmer_service = FarmerService()


@router.get("/dashboard")
def get_dashboard(aadhar_id:str):
    try:
        farmer_data = farmer_service.get_farmer_by_aadhar_id(aadhar_id)
        projects = project_service.get_project_by_farmer_aadhar_id(aadhar_id)
        transactions = transaction_service.get_transactions_by_farmer_aadhar_id(aadhar_id)
        return {"farmer_data": farmer_data, "projects": projects, "transactions": transactions}
    except Exception as e:
        return {"error": str(e)}


@router.get("/wallet_balance")
def get_wallet_balance(aadhar_id:str):
    try:
        balance = get_farmer_wallet_balance(aadhar_id)
        return {"balance": f"₹{balance}"}
    except Exception as e:
        return {"error": str(e)}
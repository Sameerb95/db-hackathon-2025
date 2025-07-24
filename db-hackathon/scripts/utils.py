# # from brownie import AgroFundConnect, accounts
from brownie import project, network, accounts
import subprocess
import asyncio
from backend.services.farmer_service import FarmerService
from scripts.mcp.gemini_mcp_client.mcp_client import MCPClient

farmer_service = FarmerService()

def get_contract_address_from_file(contract_address,wallet_address):
        contract_name="AgroFundConnect"

        if project.get_loaded_projects():
            p = project.get_loaded_projects()[0]
        else:
            p = project.load('.', name="AgroFundProject")
            p.load_config()
        if not network.is_connected():
            network.connect('ganache') 
        

        ContractClass = getattr(p, contract_name)
        return ContractClass.at(contract_address),wallet_address

def get_farmer_wallet_balance(aadhar_id:str):
    contract, account = farmer_service.get_farmer_contract_address(aadhar_id)
    contract, account = get_contract_address_from_file(contract, account)
    acc=accounts.at(account, force=True)
    balance = acc.balance()
    balance_inr = contract.weiToINR(balance)
    return balance_inr
    

# def get_activeprojects(aadhar_id:str) -> list[dict]:
#     contract, _ = get_contract_address_from_file(aadhar_id)
#     print(contract)
#     # count = contract.getProjectsCount()
#     # projects = [contract.getProject(i) for i in range(count)]

#     # projects_details_list = []
#     # for i, details in enumerate(projects):
#     #     projects_details_list.append({
#     #         "project_id": i,
#     #         "name": details[1],
#     #         "farmer": details[0],
#     #         "needed": details[5],
#     #         "raised": details[6],
#     #         "completed": details[8]
#     #     })

#     return projects_details_list

# def get_details(project_id: int) -> dict:
#     contract, _ = get_contract_address_from_file()
#     details = contract.getProject(project_id)

#     return {
#         "farmer": details[0],
#         "name": details[1],
#         "description": details[2],
#         "amount_needed": details[3],
#         "amount_raised": details[4],
#         "profit_share": details[5],
#         "completed": details[6]
#     }



def get_count():
    contract, _ = get_contract_address_from_file()
    return contract.getProjectsCount()

def initialise_mcp_server():
    try:
        command = [
            "uv", "run", "scripts/mcp/gemini_mcp_client/mcp_client.py", "scripts/mcp/gemini_mcp_server/server.py"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result}")
    except Exception as e:
        print(str(e))
        raise e

def get_chat_response(query: str) -> str:
    """
    Get a response from the MCP server for a given query.
    
    Args:
        query (str): The query to send to the MCP server.
    
    Returns:
        str: The response from the MCP server.
    """
    initialise_mcp_server()
    client = MCPClient()
    response = asyncio.run(client.chat_query(query=query))
    return response

def get_project_score(project_details: dict) -> dict:   
    """
    Get a score for the project based on its details.
    Returns a dictionary with 'score' (int) and 'reasoning' (str).
    The score is out of 100, and reasoning is a brief explanation.
    
    Args:
        project_details (dict): The details of the project. Required details are : description, amount_needed, intrest_rate, duration_in_months, crop_type, land_area.
    
    Returns:
        dict: A dictionary containing the score and reasoning.
    """
    initialise_mcp_server()
    # Ensure the MCPClient is initialized and ready to use
    response = asyncio.run(MCPClient().get_project_score(project_details=project_details))
    return response
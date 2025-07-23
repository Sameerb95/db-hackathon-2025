from brownie import accounts, network

from scripts.utils import get_contract_address_from_file

def main(project_name, project_description, amount_needed, profit_share):
    contract, account = get_contract_address_from_file()
    tx = contract.createProject(project_name, project_description, amount_needed, profit_share, {"from": account})
    tx.wait(1)
    # Get the latest project ID (assuming it's count - 1)
    project_id = contract.getProjectsCount() - 1
    print(project_id)  # Print only the project ID
    return project_id


from brownie import AgroFundConnect, accounts, network
import argparse

from scripts.utils import get_contract_address_from_file

def create_project():
    parser = argparse.ArgumentParser(description="Create a new project on AgroFundConnect")
    parser.add_argument("--project_name", type=str, help="Project name", required=True)
    parser.add_argument("--project_description", type=str, help="Project description", required=True)
    parser.add_argument("--amount_needed", type=int, help="Amount needed (in INR)", required=True)
    parser.add_argument("--profit_share", type=int, help="Profit share percentage (1-100)", required=True)

    args = parser.parse_args()
    # Load the contract address from the file
    contract_address = get_contract_address_from_file()
    account = accounts[0]
    contract = AgroFundConnect.at(contract_address)

    project_name = args.project_name
    project_description = args.project_description
    amount_needed = args.amount_needed
    profit_share = args.profit_share

    tx = contract.createProject(project_name, project_description, amount_needed, profit_share, {"from": account})
    tx.wait(1)

    print("Project created! Transaction hash:", tx.txid)

if __name__ == "__main__":
    create_project()
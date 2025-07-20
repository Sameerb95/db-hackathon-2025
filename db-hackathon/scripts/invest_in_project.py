from brownie import AgroFundConnect, accounts
import argparse

from scripts.utils import get_contract_address_from_file

def invest_in_project():
    parser = argparse.ArgumentParser(description="Invest in a project on AgroFundConnect")
    parser.add_argument("--project_id", type=int, help="Project ID to invest in", required=True)
    parser.add_argument("--amount", type=int, help="Amount to invest (in INR)", required=True)

    args = parser.parse_args()
    # Load the contract address from the file
    contract_address = get_contract_address_from_file()

    account = accounts[5]
    contract = AgroFundConnect.at(contract_address)

    project_id = args.project_id
    amount_in_inr = args.amount # Amount in INR
    amount_in_wei = contract.inrToWei(amount_in_inr)

    tx = contract.invest(project_id, amount_in_wei, {"from": account, "value": amount_in_wei})
    tx.wait(1)
    print("Investment successful! Transaction hash:", tx.txid)

if __name__ == "__main__":
    invest_in_project()


    
from brownie import accounts, network

from scripts.utils import get_contract_address_from_file

def main(project_name, project_description, amount_needed, profit_share):

    contract_address,account_address = get_contract_address_from_file()
    print(contract_address)
    print(account_address)
    account = account_address
 

    print(project_name, project_description, amount_needed, profit_share)

    tx = contract_address.createProject(project_name, project_description, amount_needed, profit_share, {"from": account})
    print(tx)
    tx.wait(1)

    print("Project created! Transaction hash:", tx.txid)

    return tx.txid


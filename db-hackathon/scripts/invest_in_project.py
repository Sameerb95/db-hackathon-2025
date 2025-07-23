from brownie import accounts
from scripts.utils import get_contract_address_from_file

def main(project_id, amount_in_inr, investor_account):
    project_id = int(project_id)
    amount_in_inr = int(amount_in_inr)
    investor_account = int(investor_account)

    contract, _ = get_contract_address_from_file()  
    account = accounts[investor_account]
    amount_in_wei = contract.inrToWei(amount_in_inr)

    tx = contract.invest(project_id, amount_in_wei, {"from": account, "value": amount_in_wei})
    tx.wait(1)
    print(tx.txid)  # Print only the transaction id

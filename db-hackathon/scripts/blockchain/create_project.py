from brownie import accounts, network
import logging
from scripts.utils import get_contract_address_from_file

def main(contract_address,wallet_address,project_name, project_description, amount_needed, profit_share):

    contract, wallet_address = get_contract_address_from_file(contract_address,wallet_address)

    logging.info(f"Contract Address: {contract_address}")
    logging.info(f"Wallet Address: {wallet_address}")
    logging.info(f"Project Name: {project_name}")
    logging.info(f"Project Description: {project_description}")
    logging.info(f"Amount Needed: {amount_needed}")
    logging.info(f"Profit Share: {profit_share}")

    try:
        tx = contract.createProject(project_name, project_description, amount_needed, profit_share, {"from": wallet_address})
    except Exception as e:
        raise e

    tx.wait(1)
    # Get the latest project ID (assuming it's count - 1)
    print(tx)
    tx.wait(1)

    print("Project created! Transaction hash:", tx.txid)

    return tx.txid


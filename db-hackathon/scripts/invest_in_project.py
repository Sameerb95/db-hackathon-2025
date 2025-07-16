from brownie import AgroFundConnect, accounts

# Helper to get deployed contract address
with open("deployed_contracts.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("AgroFundConnect:"):
            contract_address = line.split(":")[1].strip()
            break
    else:
        raise Exception("AgroFundConnect address not found in deployed_contracts.txt")

def main():
    account = accounts[4]
    contract = AgroFundConnect.at(contract_address)

    print("--- Invest in a Project ---")
    project_id = int(input("Project ID: "))
    amount = int(input("Amount to invest (in wei): "))

    tx = contract.invest(project_id, amount, {"from": account, "value": amount})
    tx.wait(1)
    print("Investment successful! Transaction hash:", tx.txid)
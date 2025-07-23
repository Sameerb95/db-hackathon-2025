from brownie import AgroFundConnect, accounts, network

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
    account = accounts[0]
    contract = AgroFundConnect.at(contract_address)

    print("--- Create a New Project ---")
    name = input("Project name: ")
    description = input("Project description: ")
    amount_needed = int(input("Amount needed (in INR): "))
    profit_share = int(input("Profit share percentage (1-100): "))

    tx = contract.createProject(name, description, amount_needed, profit_share, {"from": account})
    tx.wait(1)
    print("Project created! Transaction hash:", tx.txid)



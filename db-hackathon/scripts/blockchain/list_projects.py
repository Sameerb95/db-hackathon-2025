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
    contract = AgroFundConnect.at(contract_address)
    count = contract.getProjectsCount()
    print(f"Total projects: {count}")
    for i in range(count):
        details = contract.getProject(i)
        print(details)
        print(f"\nProject ID: {i}\n  Name: {details[1]}\n  Farmer: {details[0]}\n  Needed: {details[5]}\n  Raised: {details[6]}\n  Completed: {details[8]}") 
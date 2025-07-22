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

    print("--- View Project Details ---")
    project_id = int(input("Project ID: "))
    details = contract.getProject(project_id)
    print(f"Farmer: {details[0]}\nName: {details[1]}\nDescription: {details[2]}\nAmount Needed: {details[3]}\nAmount Raised: {details[4]}\nProfit Share: {details[5]}%\nCompleted: {details[6]}") 
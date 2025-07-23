from brownie import AgroFundConnect, accounts

def main():
    account = accounts[0]
    with open("deployed_contracts.txt", "r") as f:
        contract_address = f.read().split(":")[1].strip()
    contract = AgroFundConnect.at(contract_address)

    # Now call functions as above
    count = contract.getProjectsCount()
    print("Projects:", count)
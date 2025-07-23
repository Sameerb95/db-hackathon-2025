from brownie import AgroFundConnect, accounts

def main():
    in_contract = int(input("Enter which account wants to create contract"))
    main_account = accounts[in_contract]

    ss = AgroFundConnect.deploy({
        "from" : main_account
    })

    with open("deployed_contracts.txt", "a") as f:
        f.write(f"AgroFundConnect: {ss.address} \t {main_account}\n")
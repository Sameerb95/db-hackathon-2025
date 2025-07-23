from brownie import AgroFundConnect, accounts

def main():
    main_account = accounts[0]

    ss = AgroFundConnect.deploy({
        "from" : main_account
    })

    with open("deployed_contracts.txt", "a") as f:
        f.write(f"AgroFundConnect: {ss.address}\n")
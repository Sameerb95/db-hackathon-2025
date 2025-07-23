from brownie import AgroFundConnect, accounts

def main():
    in_contract = int(input("Enter which account wants to create contract"))
    main_account = accounts[in_contract]

    ss = AgroFundConnect.deploy({
        "from" : main_account
    })

    print(f"Contract deployed to {ss.address}")
    print(f"Main account is {main_account}")

    return ss.address,main_account
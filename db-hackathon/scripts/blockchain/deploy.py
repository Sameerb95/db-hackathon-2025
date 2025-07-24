from brownie import AgroFundConnect, accounts

def main(in_contract):
    
    main_account = accounts[int(in_contract)]

    ss = AgroFundConnect.deploy({
        "from" : main_account
    })
    print(f"{ss.address},{main_account}")
import logging
from brownie import AgroFundConnect, accounts
import logging

def main(in_contract):
    
    main_account = accounts[int(in_contract)]
    logging.info(f"Main account: {main_account}")

    ss = AgroFundConnect.deploy({
        "from" : main_account
    })
    print(f"{ss.address},{main_account}")
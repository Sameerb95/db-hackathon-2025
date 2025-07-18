from brownie import AgroFundConnect, accounts

def main():
    account = accounts[0]
    with open("deployed_contracts.txt", "r") as f:
        contract_address = f.read().split(":")[1].strip()
    contract = AgroFundConnect.at(contract_address)


    project = contract.getProject(0)

    wallet_balance = account.balance()
    balance_in_inr = contract.weiToINR(wallet_balance)
    print(f"Wallet balance: {balance_in_inr}")



    amount_raised=project[6]

    profit_share_percentage = project[7]

    profit = (amount_raised * profit_share_percentage) / 100

    print(f"Profit to be disbursed: {profit}")

    # tx = contract.disburseProfits(0, {"from": account, "value": wallet_balance})
    # tx.wait(1)
    # print("Amount disbursed successfully! Transaction hash:", tx.txid)


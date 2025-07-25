from brownie import accounts

from scripts.utils import get_contract_address_from_file

def get_investors_for_project(contract, project_id):  
    
    investors = []
    index = 0
    
    while True:
        try:
            investor_address = contract.investorAddresses(project_id, index)
            investors.append(investor_address)
            index += 1
        except Exception as e:
            break
    
    print(f"Found {len(investors)} investors for project {project_id}")
    return investors

def get_investors_with_amounts(contract, project_id):

    investors = get_investors_for_project(contract, project_id)
    investor_data = []
    
    for investor in investors:
        amount = contract.getInvestorAmountInProject(project_id, investor)
        if amount > 0:
            investor_data.append({
                'address': investor,
                'amount_wei': amount,
                'amount_inr': contract.weiToINR(amount)
            })
    
    return investor_data


def disburse_profits_to_investors(contract, project_id, total_profit_inr, amount_raised_inr, account):

    account_address = accounts.at(account, force=True)

    investor_data = get_investors_with_amounts(contract, project_id)
    
    if not investor_data:
        print("No investors found for this project")
        return
    
    print(f"Found {len(investor_data)} investors with investments for project {project_id}")
    
    for i, data in enumerate(investor_data):
        investor = data['address']
        investor_amount_inr = data['amount_inr']
        
        investor_profit = investor_amount_inr+(investor_amount_inr * total_profit_inr) // amount_raised_inr
        investor_profit_wei = contract.inrToWei(investor_profit)

        if investor_profit > 0:
            print(f"Investor {i+1}: {investor}")
            print(f"  Investment: {data['amount_inr']} INR")
            print(f"  Profit Share:  {investor_profit} INR")
                
            try:
                account_address.transfer(investor, investor_profit_wei)
                print(f"  ✅ Profit disbursed ")
            except Exception as e2:
                print(f"  ❌ transfer failed: {e2}")
            
            print()  

def get_account_balance(contract, account):
    acc=accounts.at(account, force=True)
    balance = acc.balance()
    balance_inr = contract.weiToINR(balance)
    return balance_inr

def main(contract_address, wallet_address, project_id):
    
    contract, account = get_contract_address_from_file(contract_address, wallet_address)
    print(contract)
    print(account)
    project = contract.getProject(project_id)

    farmer = project[0]
    amount_raised_inr = project[6] 
    profit_share_percentage = project[7]
    completed = project[8]

    total_profit_inr = (amount_raised_inr * profit_share_percentage) / 100
    
    print(f"Total Profit to be distributed: {total_profit_inr} INR ")

    wallet_balance = get_account_balance(contract, account)


    if wallet_balance < total_profit_inr:
        print(f"Not enough balance to disburse profits. Need {total_profit_inr} wei, have {wallet_balance} wei")
        raise Exception("Strike: Not enough balance to disburse profits")

    if not completed:
        print("❌ Project is not yet completed")
        print("❌ Cannot disburse profits until project is funded")
        raise Exception("Strike: Project is not yet completed")

    print("\n=== Starting Profit Disbursement ===")
    
    disburse_profits_to_investors(contract, project_id, total_profit_inr, amount_raised_inr, account)
    
    print("\n=== Disbursement Complete ===")
    print("✅ All profits have been disbursed to investors")
    
    final_balance = get_account_balance(contract, account)
    print(f"PROFIT_AMOUNT:{wallet_balance - final_balance}")


from brownie import AgroFundConnect, accounts


def get_investors_for_project(contract, project_id):
    """
    Get all investors for a project by accessing the public investorAddresses mapping.
    Since the mapping is public, we can access it directly, but we need to know the array length.
    """
    # Try to access the investorAddresses mapping directly
    # In Brownie, public mappings can be accessed like: contract.investorAddresses(project_id, index)
    
    investors = []
    index = 0
    
    # Keep trying to access the array until we get an error (indicating end of array)
    while True:
        try:
            investor_address = contract.investorAddresses(project_id, index)
            investors.append(investor_address)
            index += 1
        except Exception as e:
            # This means we've reached the end of the array
            break
    
    print(f"Found {len(investors)} investors for project {project_id}")
    return investors

def get_investors_with_amounts(contract, project_id):
    """
    Get all investors and their investment amounts for a project.
    """
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
    """
    Disburse profits to all investors for a project.
    """
    investor_data = get_investors_with_amounts(contract, project_id)
    
    if not investor_data:
        print("No investors found for this project")
        return
    
    print(f"Found {len(investor_data)} investors with investments for project {project_id}")
    
    for i, data in enumerate(investor_data):
        investor = data['address']
        investor_amount_inr = data['amount_inr']
        
        investor_profit = investor_amount_inr+(investor_amount_inr * total_profit_inr) // amount_raised_inr
        
        if investor_profit > 0:
            print(f"Investor {i+1}: {investor}")
            print(f"  Investment: {data['amount_inr']} INR")
            print(f"  Profit Share:  {investor_profit} INR")
                
            try:
                account.transfer(investor, investor_profit)
                print(f"  ✅ Profit disbursed ")
            except Exception as e2:
                print(f"  ❌ transfer failed: {e2}")
            
            print()  

def main():
    account = accounts[0]
    
    # Read contract address from deployed_contracts.txt
    with open("deployed_contracts.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("AgroFundConnect:"):
                contract_address = line.split(":")[1].strip()
                break
        else:
            raise Exception("AgroFundConnect address not found in deployed_contracts.txt")
    
    contract = AgroFundConnect.at(contract_address)

    project_id = 0
    project = contract.getProject(project_id)

    farmer = project[0]
    amount_raised_inr = project[6] 
    profit_share_percentage = project[7]
    completed = project[8]

    print(f"Project ID: {project_id}")
    print(f"Farmer: {farmer}")
    print(f"Amount Raised: {amount_raised_inr} INR ")
    print(f"Profit Share Percentage: {profit_share_percentage}%")
    print(f"Project Completed: {completed}")

    total_profit_inr = (amount_raised_inr * profit_share_percentage) / 100
    
    print(f"Total Profit to be distributed: {total_profit_inr} INR ")

    wallet_balance = account.balance()
    balance_in_inr = contract.weiToINR(wallet_balance)
    print(f"Wallet balance: {balance_in_inr} INR ")

    if balance_in_inr < total_profit_inr:
        print(f"Not enough balance to disburse profits. Need {total_profit_inr} wei, have {wallet_balance} wei")
        raise Exception("Strike: Not enough balance to disburse profits")

    if not completed:
        print("❌ Project is not yet completed")
        print("❌ Cannot disburse profits until project is funded")
        return

    print("\n=== Starting Profit Disbursement ===")
    
    # Disburse profits to all investors
    disburse_profits_to_investors(contract, project_id, total_profit_inr, amount_raised_inr, account)
    
    print("\n=== Disbursement Complete ===")
    print("✅ All profits have been disbursed to investors")
    
    # Show final balance
    final_balance = account.balance()
    final_balance_inr = contract.weiToINR(final_balance)
    print(f"Final wallet balance: {final_balance_inr} INR ({final_balance} wei)")
    print(f"Amount spent on profits: {contract.weiToINR(wallet_balance - final_balance)} INR")

if __name__ == "__main__":
    main()


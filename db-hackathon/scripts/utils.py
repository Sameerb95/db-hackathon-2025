from brownie import AgroFundConnect, accounts

def get_contract_address_from_file(filename = "deployed_contracts.txt"):
     # Helper to get deployed contract address
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("AgroFundConnect:"):
                contract_address = line.split(":")[1].strip()
                return contract_address
        else:
            raise Exception("AgroFundConnect address not found in deployed_contracts.txt")
        
def get_projects_count():
    # Helper to get the count of projects
    account = accounts[0]
    with open("deployed_contracts.txt", "r") as f:
        contract_address = f.read().split(":")[1].strip()
    contract = AgroFundConnect.at(contract_address)

    # Now call functions as above
    count = contract.getProjectsCount()
    return count

def get_projects() -> list[dict]:
    contract_address = get_contract_address_from_file()
    contract = AgroFundConnect.at(contract_address)
    count = contract.getProjectsCount()
    projects = [contract.getProject(i) for i in range(count)]

    projects_details_list = []
    for i, details in enumerate(projects):
        projects_details_list.append({
            "project_id": i,
            "name": details[1],
            "farmer": details[0],
            "needed": details[5],
            "raised": details[6],
            "completed": details[8]
        })

    return projects_details_list

def get_project_details(project_id: int) -> dict:
    contract_address = get_contract_address_from_file()
    contract = AgroFundConnect.at(contract_address)
    details = contract.getProject(project_id)

    return {
        "farmer": details[0],
        "name": details[1],
        "description": details[2],
        "amount_needed": details[3],
        "amount_raised": details[4],
        "profit_share": details[5],
        "completed": details[6]
    }



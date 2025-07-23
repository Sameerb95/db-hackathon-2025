# # from brownie import AgroFundConnect, accounts
from brownie import project, network, accounts
# from backend.services.

def get_contract_address_from_file(contract_address,wallet_address):
        contract_name="AgroFundConnect"

        if project.get_loaded_projects():
            p = project.get_loaded_projects()[0]
        else:
            p = project.load('.', name="AgroFundProject")
            p.load_config()
        if not network.is_connected():
            network.connect('ganache') 
        

        ContractClass = getattr(p, contract_name)
        return ContractClass.at(contract_address),wallet_address
    

# def get_activeprojects(aadhar_id:str) -> list[dict]:
#     contract, _ = get_contract_address_from_file(aadhar_id)
#     print(contract)
#     # count = contract.getProjectsCount()
#     # projects = [contract.getProject(i) for i in range(count)]

#     # projects_details_list = []
#     # for i, details in enumerate(projects):
#     #     projects_details_list.append({
#     #         "project_id": i,
#     #         "name": details[1],
#     #         "farmer": details[0],
#     #         "needed": details[5],
#     #         "raised": details[6],
#     #         "completed": details[8]
#     #     })

#     return projects_details_list

# def get_details(project_id: int) -> dict:
#     contract, _ = get_contract_address_from_file()
#     details = contract.getProject(project_id)

#     return {
#         "farmer": details[0],
#         "name": details[1],
#         "description": details[2],
#         "amount_needed": details[3],
#         "amount_raised": details[4],
#         "profit_share": details[5],
#         "completed": details[6]
#     }



def get_count():
    contract, _ = get_contract_address_from_file()
    return contract.getProjectsCount()
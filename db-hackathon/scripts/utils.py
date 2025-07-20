# db-hackathon/scripts/utils.py
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
        

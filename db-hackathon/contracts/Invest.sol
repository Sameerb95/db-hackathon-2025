// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AgroFundConnect {
    // Structure to hold details of a funding project
    struct Project {
        address payable farmer;        // Address of the farmer requesting funds
        string name;                   // Name of the project (e.g., "Organic Wheat Harvest")
        string description;            // Detailed description of the project
        uint256 amountNeeded;          // Total amount of Ether needed for the project
        uint256 amountRaised;          // Current amount of Ether raised
        uint256 profitSharePercentage; // Percentage of profit promised to investors (e.g., 10 for 10%)
        bool completed;                // True if project has reached its funding goal
        mapping(address => uint256) investors; // Mapping of investor address to their invested amount
        address[] investorAddresses;   // Array to keep track of unique investor addresses
    }

    Project[] public projects; // Array of all funding projects

    event ProjectCreated(
        uint256 indexed projectId,
        address indexed farmer,
        string name,
        uint256 amountNeeded
    );
    event FundsInvested(
        uint256 indexed projectId,
        address indexed investor,
        uint256 amount
    );
    event ProjectFunded(uint256 indexed projectId);

    /**
     * @dev Creates a new funding project request.
     * @param _name Name of the project.
     * @param _description Description of the project.
     * @param _amountNeeded Amount of wei needed for the project.
     * @param _profitSharePercentage Percentage of profit to be shared with investors.
     */
    function createProject(
        string memory _name,
        string memory _description,
        uint256 _amountNeeded,
        uint256 _profitSharePercentage
    ) public {
        require(_amountNeeded > 0, "Amount needed must be greater than zero.");
        require(_profitSharePercentage > 0 && _profitSharePercentage <= 100, "Profit share must be between 1 and 100.");

        // Directly create a new Project struct in storage by pushing to the array
        uint256 projectId = projects.length; // Get the ID for the new project
        projects.push(); // Add a new empty element to the storage array
        Project storage newProject = projects[projectId]; // Get a reference to the newly created storage struct

        newProject.farmer = payable(msg.sender);
        newProject.name = _name;
        newProject.description = _description;
        newProject.amountNeeded = _amountNeeded;
        newProject.amountRaised = 0;
        newProject.profitSharePercentage = _profitSharePercentage;
        newProject.completed = false;
        // Mapping 'investors' is implicitly initialized in storage.
        newProject.investorAddresses = new address[](0); // Initialize empty array

        emit ProjectCreated(
            projectId,
            msg.sender,
            _name,
            _amountNeeded
        );
    }

    /**
     * @dev Allows users to invest in a project.
     * @param _projectId The ID of the project to invest in.
     */
    function invest(uint256 _projectId , uint256 _amount) public payable {
        require(_projectId < projects.length, "Project does not exist.");
        Project storage project = projects[_projectId];
        require(!project.completed, "Project is already funded.");
        require(_amount > 0, "Investment amount must be greater than zero.");
        // require(msg.sender != project.farmer, "Farmer cannot invest in their own project.");

        // Record the investment
        if (project.investors[msg.sender] == 0) {
            project.investorAddresses.push(msg.sender); // Add investor to the list if new
        }
        project.investors[msg.sender] += _amount;
        project.amountRaised += _amount;

        emit FundsInvested(_projectId, msg.sender, msg.value);

        // Check if project is funded
        if (project.amountRaised >= project.amountNeeded) {
            project.completed = true;
            emit ProjectFunded(_projectId);
            // In a real app, funds would be transferred to the farmer here.
            // For simplicity, we'll just mark it funded.
            // project.farmer.transfer(project.amountRaised); // This would send all collected funds
        }
    }

/**
 * @dev Retrieves details of a specific project.
 * @param _projectId The ID of the project.
 * @return farmer - Address of the farmer requesting funds,
                    name - Name of the project (e.g., "Organic Wheat Harvest"),
                    description - Detailed description of the project,
                    amountNeeded - Total amount of Ether needed for the project,
                    amountRaised - Current amount of Ether raised,
                    profitSharePercentage - Percentage of profit promised to investors (e.g., 10),
                    completed - True if project has reached its funding goal.
 */

    function getProject(uint256 _projectId)
        public
        view
        returns (
            address farmer,
            string memory name,
            string memory description,
            uint256 amountNeeded,
            uint256 amountRaised,
            uint256 profitSharePercentage,
            bool completed
        )
    {
        require(_projectId < projects.length, "Project does not exist.");
        Project storage project = projects[_projectId];
        return (
            project.farmer,
            project.name,
            project.description,
            project.amountNeeded,
            project.amountRaised,
            project.profitSharePercentage,
            project.completed
        );
    }

    /**
     * @dev Retrieves the total number of projects.
     * @return The count of projects.
     */
    function getProjectsCount() public view returns (uint256) {
        return projects.length;
    }

    /**
     * @dev Retrieves the amount invested by a specific investor in a project.
     * @param _projectId The ID of the project.
     * @param _investor The address of the investor.
     * @return The amount invested by the investor in wei.
     */
    function getInvestorAmountInProject(uint256 _projectId, address _investor) public view returns (uint256) {
        require(_projectId < projects.length, "Project does not exist.");
        Project storage project = projects[_projectId];
        return project.investors[_investor];
    }
}

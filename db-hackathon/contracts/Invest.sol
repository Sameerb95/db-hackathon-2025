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
    }

    Project[] public projects; // Array of all funding projects

    // Mapping from projectId => investor address => invested amount
    mapping(uint256 => mapping(address => uint256)) public investorAmounts;
    // Mapping from projectId => array of investor addresses
    mapping(uint256 => address[]) public investorAddresses;
    // Mapping to check if an address is already an investor for a project
    mapping(uint256 => mapping(address => bool)) public isInvestor;

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
    event ProfitsDisbursed(uint256 indexed projectId, uint256 totalProfit);

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
        require(_amountNeeded > 0, "Amount needed in INR must be greater than zero.");
        require(_profitSharePercentage > 0 && _profitSharePercentage <= 100, "Profit share must be between 1 and 100.");

        _amountNeeded = inrToWei(_amountNeeded);

        uint256 projectId = projects.length;
        projects.push(Project({
            farmer: payable(msg.sender),
            name: _name,
            description: _description,
            amountNeeded: _amountNeeded,
            amountRaised: 0,
            profitSharePercentage: _profitSharePercentage,
            completed: false
        }));

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
        require(msg.sender != project.farmer, "Farmer cannot invest in their own project.");

        require(msg.value == _amount, "Sent Ether must match the investment amount.");

        // Record the investment
        if (!isInvestor[_projectId][msg.sender]) {
            investorAddresses[_projectId].push(msg.sender);
            isInvestor[_projectId][msg.sender] = true;
        }
        investorAmounts[_projectId][msg.sender] += _amount;
        project.amountRaised += _amount;

        emit FundsInvested(_projectId, msg.sender, msg.value);

        // Check if project is funded
        if (project.amountRaised >= project.amountNeeded) {
            project.completed = true;
            emit ProjectFunded(_projectId);
            // Transfer funds to the farmer
            project.farmer.transfer(project.amountRaised);
        }
    }

    /*
     * @dev Disburses profits to all investors based on their share and the project's profit share percentage.
     * The farmer must send the total profit amount as msg.value.
     */
    function disburseProfits(address investor , uint256 investorProfit) public payable {
            {
                    payable(investor).transfer(investorProfit);
            }
            
        emit ProfitsDisbursed(0, investorProfit);
    }

    /**
     * @dev Retrieves details of a specific project.
     * @param _projectId The ID of the project.
     * @return farmer - Address of the farmer requesting funds,
                        name - Name of the project (e.g., "Organic Wheat Harvest"),
                        description - Detailed description of the project,
                        amountNeeded - Total amount of Ether needed for the project,
                        amountRaised - Current amount of Ether raised,
                        amountNeeded_INR - Total amount of INR needed for the project,
                        amountRaised_INR - Current amount of INR raised,
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
            uint256 amountNeeded_INR,
            uint256 amountRaised_INR,
            uint256 profitSharePercentage,
            bool completed
        )
    {
        require(_projectId < projects.length, "Project does not exist.");
        Project storage project = projects[_projectId];
        amountNeeded_INR = weiToINR(project.amountNeeded);
        amountRaised_INR = weiToINR(project.amountRaised);

        return (
            project.farmer,         // 0
            project.name,           // 1
            project.description,    // 2
            project.amountNeeded,   // 3
            project.amountRaised,   // 4
            amountNeeded_INR,       // 5
            amountRaised_INR,       // 6
            project.profitSharePercentage, // 7
            project.completed        // 8
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
        return investorAmounts[_projectId][_investor];
    }

    /**
     * @dev Converts an INR amount to WEI using the fixed rate: 1 ETH = 1000 INR.
     * @param inrAmount The amount in INR.
     * @return weiAmount The equivalent amount in WEI.
     */
    function inrToWei(uint256 inrAmount) public pure returns (uint256 weiAmount) {
        // 1 ETH = 1e18 WEI = 1000 INR
        // So, WEI = (inrAmount * 1e18) / 1000
        return (inrAmount * 1e18) / 1000;
    }

    /**
     * @dev Converts a WEI amount to INR using the fixed rate: 1 ETH = 1000 INR.
     * @param weiAmount The amount in WEI.
     * @return inrAmount The equivalent amount in INR.
     */
    function weiToINR(uint256 weiAmount) public pure returns (uint256 inrAmount) {
        // 1 ETH = 1e18 WEI = 1000 INR
        // So, INR = (weiAmount * 1000) / 1e18
        return (weiAmount * 1000) / 1e18;
    }   
}

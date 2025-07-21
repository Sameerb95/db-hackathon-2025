# Backend API Documentation

This document provides details about the API endpoints available in the backend service, including the expected request data, response data, and a short summary of each endpoint.

---

## Endpoints

### 1. Create Project

- **URL:** `/create_project/`
- **Method:** POST
- **Description:** Creates a new project by providing project details. This endpoint triggers a Brownie script to create the project on the blockchain.
- **Request Body:**
```json
{
  "project_name": "string",
  "project_description": "string",
  "amount_needed": 1000,
  "profit_share": 10
}
```
- **Response:**
  - Success:
  ```json
  {
    "message": "Project created successfully!",
    "transaction_hash": "string"
  }
  ```
  - Error:
  ```json
  {
    "error": "string"
  }
  ```

---

### 2. Invest in Project

- **URL:** `/invest_in_project/`
- **Method:** POST
- **Description:** Invests a specified amount in a project by project ID. This endpoint triggers a Brownie script to process the investment.
- **Request Body:**
```json
{
  "project_id": 1,
  "amount": 500
}
```
- **Response:**
  - Success:
  ```json
  {
    "message": "Investment successful!",
    "transaction_hash": "string"
  }
  ```
  - Error:
  ```json
  {
    "error": "string"
  }
  ```

---

### 3. Disburse Amount

- **URL:** `/disburse_amount/`
- **Method:** POST
- **Description:** Disburses the amount for a given project ID. This endpoint triggers a Brownie script to disburse funds.
- **Request Body:**
```json
{
  "project_id": 1
}
```
- **Response:**
  - Success:
  ```json
  {
    "message": "Amount disbursed successfully!",
    "transaction_hash": "string"
  }
  ```
  - Error:
  ```json
  {
    "error": "string"
  }
  ```

---

### 4. Get Projects Count

- **URL:** `/get_projects/count`
- **Method:** GET
- **Description:** Returns the total number of projects.
- **Response:**
```json
{
  "projects_count": 10
}
```

---

### 5. Get Projects List

- **URL:** `/get_projects/list`
- **Method:** GET
- **Description:** Returns a list of all projects.
- **Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Project 1",
      "description": "Description of project 1",
      "amount_needed": 1000,
      "profit_share": 10
    },
    {
      "id": 2,
      "name": "Project 2",
      "description": "Description of project 2",
      "amount_needed": 2000,
      "profit_share": 15
    }
  ]
}
```

---

### 6. Get Project Details

- **URL:** `/get_projects/{project_id}`
- **Method:** GET
- **Description:** Returns detailed information about a specific project by its ID.
- **Response:**
  - Success:
  ```json
  {
    "id": 1,
    "name": "Project 1",
    "description": "Description of project 1",
    "amount_needed": 1000,
    "profit_share": 10,
    "other_details": "..."
  }
  ```
  - Error:
  ```json
  {
    "error": "Project not found"
  }
  ```

---

# Notes

- All POST endpoints expect JSON bodies with the specified fields.
- The `transaction_hash` in responses is a string representing the blockchain transaction hash for the operation.
- Error responses contain an `error` field with a descriptive message.

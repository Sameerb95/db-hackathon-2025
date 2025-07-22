import os
from dotenv import load_dotenv
import requests
import json
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP
from collections import defaultdict

# Create MCP server instance
mcp = FastMCP("JiraIntegrationServer")


# --- Configuration for Jira API ---
# It is highly recommended to store sensitive information like API tokens
# in environment variables and not hardcode them.

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


# Basic validation for configuration
if not all([JIRA_BASE_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
    print("Warning: Jira API credentials are not fully configured. Please set the following environment variables:")
    print("  JIRA_BASE_URL (e.g., https://your-domain.atlassian.net)")
    print("  JIRA_USERNAME (your Atlassian email)")
    print("  JIRA_API_TOKEN (your generated API token)")
    # Exit or handle this more gracefully in a production environment
    # For this example, we'll allow it to proceed but API calls will fail.

# Headers for Jira API requests (Basic Authentication)
JIRA_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Add Basic Authentication to headers if credentials are provided
if JIRA_USERNAME and JIRA_API_TOKEN:
    JIRA_AUTH = (JIRA_USERNAME, JIRA_API_TOKEN)
else:
    JIRA_AUTH = None # No authentication if credentials are missing

# --- Helper function for making Jira API requests ---
def _make_jira_request(method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict[str, Any]:
    """
    Helper function to make authenticated requests to the Jira API.
    :param method: HTTP method (e.g., "GET", "POST").
    :param endpoint: The API endpoint relative to the base URL (e.g., "/rest/api/3/issue/").
    :param params: Dictionary of query parameters for GET requests.
    :param data: Dictionary of data to send as JSON in the request body.
    :return: Parsed JSON response as a dictionary, or an error dictionary.
    """
    if not JIRA_AUTH:
        return {"error": "Jira API credentials are not set up. Cannot make requests."}

    url = f"{JIRA_BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=JIRA_HEADERS, auth=JIRA_AUTH, params=params, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=JIRA_HEADERS, auth=JIRA_AUTH, data=json.dumps(data), timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=JIRA_HEADERS, auth=JIRA_AUTH, data=json.dumps(data), timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=JIRA_HEADERS, auth=JIRA_AUTH, timeout=10)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        # Some successful responses (like 204 No Content) might not have JSON
        if response.status_code == 204:
            return {"message": "Operation successful, no content returned."}
            
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {http_err.response.text}")
        return {"error": f"Jira API HTTP error: {http_err}", "details": http_err.response.text}
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return {"error": f"Jira API connection error: {conn_err}"}
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return {"error": f"Jira API timeout: {timeout_err}"}
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return {"error": f"Jira API request error: {req_err}"}
    except json.JSONDecodeError as json_err:
        # Sometimes, non-204 but successful responses might return empty or non-JSON content
        if response.status_code >= 200 and response.status_code < 300:
            return {"message": "Operation successful, but response was not JSON.", "raw_response": response.text}
        print(f"JSON decode error: {json_err} - Response: {response.text}")
        return {"error": f"Jira API JSON parsing error: {json_err}", "raw_response": response.text}
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        return {"error": f"An unknown error occurred: {e}"}

# --- MCP Tools for Jira Integration ---

@mcp.tool()
def get_all_jira_issue(project_name: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Fetches the details of a specific Jira issue.
    Args:
        issue_key (str): The key of the Jira issue (e.g., "PROJ-123").
    Returns:
        Dict: A dictionary containing the issue details or an error message.
    """
    print(f"Fetching Jira issue: {project_name}")  
    endpoint = f"/rest/api/3/search"
    params = {
        "jql": f"project = {project_name}",
        "maxResults": max_results
    }
    result = _make_jira_request("GET", endpoint, params=params)
    
    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    # Extract relevant fields for a cleaner response
    if "fields" in result:
        return {
            "status": "success",
            "issue_key": result.get("key"),
            "summary": result["fields"].get("summary"),
            "description": result["fields"].get("description", {}).get("content", [{"content":[{"text":"N/A"}]}])[0].get("content", [{"text":"N/A"}])[0].get("text"), # Extract text from rich text format
            "status_name": result["fields"].get("status", {}).get("name"),
            "assignee_name": result["fields"].get("assignee", {}).get("displayName"),
            "reporter_name": result["fields"].get("reporter", {}).get("displayName"),
            "issue_type": result["fields"].get("issuetype", {}).get("name"),
            "priority": result["fields"].get("priority", {}).get("name"),
            "created": result["fields"].get("created"),
            "updated": result["fields"].get("updated"),
            "url": f"{JIRA_BASE_URL}/browse/{result.get('key')}"
        }
    return {"status": "success", "message": "Issue found, but fields structure unexpected.", "raw_response": result}


@mcp.tool()
def get_jira_issue(issue_key: str) -> Dict[str, Any]:
    """
    Fetches the details of a specific Jira issue.
    Args:
        issue_key (str): The key of the Jira issue (e.g., "PROJ-123").
    Returns:
        Dict: A dictionary containing the issue details or an error message.
    """
    print(f"Fetching Jira issue: {issue_key}")
    endpoint = f"/rest/api/3/issue/{issue_key}"
    result = _make_jira_request("GET", endpoint)
    
    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    # Extract relevant fields for a cleaner response
    if "fields" in result:
        return {
            "status": "success",
            "issue_key": result.get("key"),
            "summary": result["fields"].get("summary"),
            "description": result["fields"].get("description", {}).get("content", [{"content":[{"text":"N/A"}]}])[0].get("content", [{"text":"N/A"}])[0].get("text"), # Extract text from rich text format
            "status_name": result["fields"].get("status", {}).get("name"),
            "assignee_name": result["fields"].get("assignee", {}).get("displayName"),
            "reporter_name": result["fields"].get("reporter", {}).get("displayName"),
            "issue_type": result["fields"].get("issuetype", {}).get("name"),
            "priority": result["fields"].get("priority", {}).get("name"),
            "created": result["fields"].get("created"),
            "updated": result["fields"].get("updated"),
            "url": f"{JIRA_BASE_URL}/browse/{issue_key}"
        }
    return {"status": "success", "message": "Issue found, but fields structure unexpected.", "raw_response": result}

@mcp.tool()
def get_all_jira_issue(project_name: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Fetches the details of a specific Jira issue.
    Args:
        issue_key (str): The key of the Jira issue (e.g., "PROJ-123").
    Returns:
        Dict: A dictionary containing the issue details or an error message.
    """
    print(f"Fetching Jira issue: {project_name}")  
    endpoint = f"/rest/api/3/search"
    params = {
        "jql": f"project = {project_name}",
        "maxResults": max_results
    }
    result = _make_jira_request("GET", endpoint, params=params)
    
    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    # Extract relevant fields for a cleaner response
    if "fields" in result:
        return {
            "status": "success",
            "issue_key": result.get("key"),
            "summary": result["fields"].get("summary"),
            "description": result["fields"].get("description", {}).get("content", [{"content":[{"text":"N/A"}]}])[0].get("content", [{"text":"N/A"}])[0].get("text"), # Extract text from rich text format
            "status_name": result["fields"].get("status", {}).get("name"),
            "assignee_name": result["fields"].get("assignee", {}).get("displayName"),
            "reporter_name": result["fields"].get("reporter", {}).get("displayName"),
            "issue_type": result["fields"].get("issuetype", {}).get("name"),
            "priority": result["fields"].get("priority", {}).get("name"),
            "created": result["fields"].get("created"),
            "updated": result["fields"].get("updated"),
            "url": f"{JIRA_BASE_URL}/browse/{result.get('key')}"
        }
    return {"status": "success", "message": "Issue found, but fields structure unexpected.", "raw_response": result}

@mcp.tool()
def create_jira_issue(project_key: str, summary: str, description: str = None, issue_type_name: str = "Task", assignee_id: str = None, priority_name: str = None) -> Dict[str, Any]:
    """
    Creates a new Jira issue.
    Args:
        project_key (str): The key of the project where the issue will be created (e.g., "PROJ").
        summary (str): The summary/title of the new issue.
        description (str, optional): The detailed description of the issue. Defaults to None.
        issue_type_name (str, optional): The type of issue (e.g., "Task", "Bug", "Story"). Defaults to "Task".
        assignee_id (str, optional): The account ID of the assignee. Defaults to None.
        priority_name (str, optional): The name of the priority (e.g., "High", "Medium"). Defaults to None.
    Returns:
        Dict: A dictionary with the created issue's key and URL, or an error message.
    """
    print(f"Creating Jira issue in project {project_key} with summary: {summary}")
    endpoint = "/rest/api/3/issue"
    
    issue_payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "issuetype": {
                "name": issue_type_name
            }
        }
    }

    if description:
        # Jira v3 API uses Atlassian Document Format for rich text fields
        issue_payload["fields"]["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]
        }
    
    if assignee_id:
        issue_payload["fields"]["assignee"] = {"accountId": assignee_id}

    if priority_name:
        issue_payload["fields"]["priority"] = {"name": priority_name}

    result = _make_jira_request("POST", endpoint, data=issue_payload)

    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    return {
        "status": "success",
        "message": "Jira issue created successfully.",
        "issue_key": result.get("key"),
        "issue_id": result.get("id"),
        "issue_url": f"{JIRA_BASE_URL}/browse/{result.get('key')}"
    }

@mcp.tool()
def add_jira_comment(issue_key: str, comment_body: str) -> Dict[str, Any]:
    """
    Adds a comment to an existing Jira issue.
    Args:
        issue_key (str): The key of the Jira issue (e.g., "PROJ-123").
        comment_body (str): The content of the comment.
    Returns:
        Dict: A dictionary confirming the comment addition or an error message.
    """
    print(f"Adding comment to Jira issue {issue_key}")
    endpoint = f"/rest/api/3/issue/{issue_key}/comment"
    
    # Comments also use Atlassian Document Format
    comment_payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_body
                        }
                    ]
                }
            ]
        }
    }

    result = _make_jira_request("POST", endpoint, data=comment_payload)

    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    return {
        "status": "success",
        "message": "Comment added successfully.",
        "comment_id": result.get("id"),
        "issue_key": issue_key
    }

@mcp.tool()
def get_jira_projects() -> Dict[str, Any]:
    """
    Fetches a list of all accessible Jira projects.
    Returns:
        Dict: A dictionary containing a list of projects or an error message.
    """
    print("Fetching all Jira projects...")
    endpoint = "/rest/api/3/project/search"
    result = _make_jira_request("GET", endpoint)

    if "error" in result:
        return {"status": "error", "message": result["error"], "details": result.get("details")}
    
    projects_list = []
    for project in result.get("values", []):
        projects_list.append({
            "id": project.get("id"),
            "key": project.get("key"),
            "name": project.get("name"),
            "projectTypeKey": project.get("projectTypeKey"),
            "category": project.get("projectCategory", {}).get("name")
        })
    
    return {
        "status": "success",
        "message": f"Found {len(projects_list)} projects.",
        "projects": projects_list
    }

@mcp.tool()
def transition_jira_issue_status(issue_key: str, target_status_name: str) -> Dict[str, Any]:
    """
    Transitions the status of a Jira issue to a new status.
    This tool first fetches available transitions for the issue and then attempts
    to find a transition that leads to the specified target status name.
    Args:
        issue_key (str): The key of the Jira issue (e.g., "PROJ-123").
        target_status_name (str): The name of the status to transition to (e.g., "In Progress", "Done").
    Returns:
        Dict: A dictionary confirming the status change or an error message.
    """
    print(f"Attempting to transition status for issue {issue_key} to '{target_status_name}'")
    
    # Step 1: Get available transitions for the issue
    transitions_endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
    transitions_response = _make_jira_request("GET", transitions_endpoint)

    if "error" in transitions_response:
        return {"status": "error", "message": f"Could not fetch transitions for issue {issue_key}: {transitions_response['error']}", "details": transitions_response.get("details")}
    
    available_transitions = transitions_response.get("transitions", [])
    
    transition_id = None
    for transition in available_transitions:
        if transition.get("to", {}).get("name", "").lower() == target_status_name.lower():
            transition_id = transition.get("id")
            break
    
    if not transition_id:
        return {
            "status": "error",
            "message": f"No valid transition found for issue {issue_key} to status '{target_status_name}'.",
            "available_transitions": [{"id": t.get("id"), "name": t.get("name"), "to_status": t.get("to",{}).get("name")} for t in available_transitions]
        }

    # Step 2: Execute the transition
    execute_transition_endpoint = f"/rest/api/3/issue/{issue_key}/transitions"
    transition_payload = {
        "transition": {
            "id": transition_id
        }
    }
    
    # A successful transition typically returns a 204 No Content response
    result = _make_jira_request("POST", execute_transition_endpoint, data=transition_payload)

    if "error" in result:
        return {"status": "error", "message": f"Failed to transition issue {issue_key}: {result['error']}", "details": result.get("details")}
    
    return {
        "status": "success",
        "message": f"Issue {issue_key} successfully transitioned to '{target_status_name}'.",
        "old_status": transitions_response.get("issue", {}).get("fields", {}).get("status", {}).get("name"), # Attempt to get old status, might not be reliable here
        "new_status": target_status_name
    }

@mcp.tool()
def search_jira_users(query: str, max_results: int = 50) -> Dict[str, Any]:
    """
    Searches for Jira users matching a given query string.
    This uses the /user/search (singular) endpoint which is more flexible for finding users.
    Args:
        query (str): The search string for user display names, email addresses, or account IDs.
                     An empty string might return some default users or no users depending on Jira config.
        max_results (int, optional): The maximum number of users to return. Defaults to 50.
    Returns:
        Dict: A dictionary containing a list of found users or an error message.
    """
    print(f"Searching for Jira users with query: '{query}'")
    endpoint = "/rest/api/3/user/search" # Use singular 'user' for search
    params = {
        "query": query,
        "maxResults": max_results
    }
    
    users_response = _make_jira_request("GET", endpoint, params=params)

    if "error" in users_response:
        return {"status": "error", "message": f"Could not search users: {users_response['error']}", "details": users_response.get("details")}

    # The API returns a list of user objects directly
    users_list = []
    for user_data in users_response: # users_response is expected to be a list here
        users_list.append({
            "displayName": user_data.get("displayName"),
            "accountId": user_data.get("accountId"),
            "emailAddress": user_data.get("emailAddress"),
            "active": user_data.get("active")
        })

    return {
        "status": "success",
        "message": f"Found {len(users_list)} users for query '{query}'.",
        "users": users_list
    }

@mcp.tool()
def get_jira_user_by_account_id(account_id: str) -> Dict[str, Any]:
    """
    Gets a single Jira user by their account ID.
    Args:
        account_id (str): The unique account ID of the user.
    Returns:
        Dict: A dictionary containing the user's information or an error message.
    """
    print(f"Attempting to get user by account ID: {account_id}")

    # Note: The /rest/api/3/user endpoint works for getting a single user by accountId
    endpoint = "/rest/api/3/user" 
    params = {"accountId": account_id}
    
    user_response = _make_jira_request("GET", endpoint, params=params)

    if "error" in user_response:
        return {"status": "error", "message": f"Could not fetch user for account ID {account_id}: {user_response['error']}", "details": user_response.get("details")}

    # user_response should be a single user object (dict), not a list
    return {
        "status": "success",
        "message": f"Found user with account ID {account_id}.",
        "user": {
            "displayName": user_response.get("displayName"),
            "accountId": user_response.get("accountId"),
            "emailAddress": user_response.get("emailAddress"),
            "active": user_response.get("active")
        }
    }


@mcp.tool()
def get_jira_user_by_name(name: str) -> Dict[str, Any]:
    """
    Gets a Jira user by their display name.
    This tool first searches for users matching the name and then returns the account ID
    if a unique match is found. If multiple matches, it lists them.
    Args:
        name (str): The display name or part of the display name of the user to find.
    Returns:
        Dict: A dictionary with the user's account ID if a unique match,
              a list of matching users if multiple, or an error message.
    """
    print(f"Attempting to get user by name: '{name}'")

    # Step 1: Search for users by the provided name
    # We leverage the search_jira_users tool for this.
    search_result = search_jira_users(query=name, max_results=50) 
    
    if search_result["status"] == "error":
        return search_result # Propagate the error from search_jira_users

    found_users = search_result.get("users", [])

    if len(found_users) == 1:
        # Exactly one user found, return their account ID
        user = found_users[0]
        return {
            "status": "success",
            "message": f"Found unique user with name '{name}'.",
            "user_info": {
                "displayName": user.get("displayName"),
                "accountId": user.get("accountId"),
                "emailAddress": user.get("emailAddress")
            }
        }
    elif len(found_users) > 1:
        # Multiple users found, list them for disambiguation
        return {
            "status": "ambiguous_results",
            "message": f"Multiple users found matching '{name}'. Please be more specific or use an account ID.",
            "matching_users": [
                {"displayName": u.get("displayName"), "accountId": u.get("accountId"), "emailAddress": u.get("emailAddress")}
                for u in found_users
            ]
        }
    else:
        # No users found
        return {
            "status": "not_found",
            "message": f"No user found matching '{name}'.",
            "query": name
        }

# --- Main execution block ---
if __name__ == "__main__":
    print("Starting Jira Integration MCP Server...")
    print("Ensure JIRA_BASE_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables are set.")
    mcp.run()

from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import asyncio

from scripts.mcp.gemini_mcp_client.mcp_client import MCPClient

router = APIRouter()

class MCPServerRequest(BaseModel):
    query: str

class MCPServerResponse(BaseModel):
    result: str

@router.get("/get_response")
def get_mcp_server_response(request: MCPServerRequest) -> MCPServerResponse:
    try:
        command = [
            "uv", "run", "scripts/mcp/gemini_mcp_client/mcp_client.py", "scripts/mcp/gemini_mcp_server/server.py"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Error creating project: {result}")
    except Exception as e:
        return MCPServerResponse(result=str(e))
    client = MCPClient()
    response = asyncio.run(client.chat_query(query=request.query))
    return MCPServerResponse(result=response)
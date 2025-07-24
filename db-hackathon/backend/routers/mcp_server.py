# from fastapi import APIRouter
# import subprocess
# from pydantic import BaseModel
# import asyncio

# from scripts.mcp.gemini_mcp_client.mcp_client import MCPClient
# from scripts.utils import get_chat_response

# router = APIRouter()

# class MCPServerRequest(BaseModel):
#     query: str

# class MCPServerResponse(BaseModel):
#     result: str

# @router.post("/get_response")
# def get_mcp_server_response(request: MCPServerRequest) -> MCPServerResponse:
#     return MCPServerResponse(result=get_chat_response(request.query))


from fastapi import APIRouter
from pydantic import BaseModel
import os

from scripts.mcp.gemini_mcp_client.mcp_client import MCPClient

router = APIRouter()

class MCPServerRequest(BaseModel):
    query: str

class MCPServerResponse(BaseModel):
    result: str

@router.post("/get_response")
async def get_mcp_server_response(request: MCPServerRequest) -> MCPServerResponse:
    server_script_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../scripts/mcp/gemini_mcp_server/server.py"
        )
    )

    client = MCPClient()
    await client.connect_to_server(server_script_path)
    response = await client.chat_query(request.query)
    await client.cleanup()
    return MCPServerResponse(result=response)
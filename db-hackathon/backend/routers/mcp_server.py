from fastapi import APIRouter
import subprocess
from pydantic import BaseModel
import asyncio

from scripts.mcp.gemini_mcp_client.mcp_client import MCPClient
from scripts.utils import get_chat_response

router = APIRouter()

class MCPServerRequest(BaseModel):
    query: str

class MCPServerResponse(BaseModel):
    result: str

@router.get("/get_response")
def get_mcp_server_response(request: MCPServerRequest) -> MCPServerResponse:
    return MCPServerResponse(result=get_chat_response(request.query))
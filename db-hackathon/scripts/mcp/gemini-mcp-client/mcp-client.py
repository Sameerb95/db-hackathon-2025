from dotenv import load_dotenv
from contextlib import AsyncExitStack
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from gemini_tool_agent.agent import Agent
import os
from typing import Optional

load_dotenv()


key = str(os.getenv("GEMINI_API_KEY"))
model = str(os.getenv("GEMINI_MODEL"))

class GeminiMCPClient:
    def __init__(self):
        self.session : Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.agent = Agent(key=key,model=model)


    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        if not tools:
            print("No tools found from the server.")
            tools = []
        else:
            print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def get_response(self,input:str):
        try:
            response=self.agent.process_query(input)
            
            self.agent.history.append({"role": "user", "content": input})
            
            
            if isinstance(response, dict) and response.get("needs_tool", False):
                tool_name = response.get("tool_name", None)
                if tool_name:
                    
                    tool_response=self.agent.process_use_tool(tool_name)
                    
                    self.agent.history.append({"role": "assistant", "content": tool_response})
                    
                    tool=tool_response["tool_name"]
                    
                    call_tool=self.agent.process_use_tool(tool)
                    
                    self.agent.history.append({"role": "process_tool_call", "content": call_tool})
                    
                    result=await self.session.call_tool(tool,call_tool["input"]) 
                    
                    self.agent.history.append({"role": "tool_call_result", "content": result})
         
            if isinstance(response, dict) and response.get("needs_direct_response", False):
                self.agent.history.append({"role": "direct_response", "content": response["direct_response"]})
      
                return response["direct_response"]
            else:
                conversation_context = self.agent.history[-5:] if len(self.agent.history) >= 5 else self.agent.history
                response_text = self.agent.generate_response(f"""
                You are a helpful assistant responding to the following query:
                QUERY: {input}
                
                CONVERSATION HISTORY: {conversation_context}
                
                Please provide a comprehensive and accurate response that considers the conversation history.
                """)
                self.agent.history.append({"role": "assistant", "content": response_text})
                return response_text
                
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}"

    async def chat_loop(self):
        """Main chat loop for interacting with the MCP server"""
        print("Chat session started. Type 'exit' to quit.")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Ending chat session...")
                    break
                
                if not user_input:
                    continue
                try:
                 response = await self.get_response(user_input)
                except Exception as e:
                    print(f"\nError occurred: {str(e)}")
                    continue
                if response:
                    print("\nAssistant:", response)
                    
            except Exception as e:
                print(f"\nError occurred: {str(e)}")
                continue

    async def close(self):
        await self.exit_stack.aclose()


async def main():
    mcp_client = GeminiMCPClient()
    server_path = input("Enter the path to the server script: ")
    try:
        await mcp_client.connect_to_server(server_path)
        await mcp_client.chat_loop()
    finally:
        await mcp_client.close()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


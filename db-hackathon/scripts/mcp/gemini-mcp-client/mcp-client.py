# from google.auth import credentials
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from langchain_mcp_adapters.tools import load_mcp_tools
# from langgraph.prebuilt import create_react_agent
# import asyncio
# from langchain_google_genai import ChatGoogleGenerativeAI
# import os
# from dotenv import load_dotenv

# load_dotenv()


# model = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     credentials=os.getenv("GEMINI_API_KEY"))

# server_params = StdioServerParameters(
#     command="python",
#     args=[
#           "/Users/sameer/db-hackathon-2025/db-hackathon/scripts/mcp/gemini-mcp-server/server.py"
#         ]
# )

# async def run_agent():
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()

#             tools = await load_mcp_tools(session)

#             agent = create_react_agent(model, tools)
#             agent_response = await agent.ainvoke({"messages": "say_hello to Sameer"})
#             return agent_response

# async def chat_loop():
#     """Main chat loop for interacting with the MCP server"""
#     print("Chat session started. Type 'exit' to quit.")
    
#     while True:
#         try:
#             user_input = input("\nYou: ").strip()
            
#             if user_input.lower() == 'exit':
#                 print("Ending chat session...")
#                 break
            
#             if not user_input:
#                 continue
#             try:
#                 response = await run_agent(user_input)
#             except Exception as e:
#                 print(f"\nError occurred: {str(e)}")
#                 continue
#             if response:
#                 print("\nAssistant:", response)
                
#         except Exception as e:
#             print(f"\nError occurred: {str(e)}")
#             continue



# # Run the async function
# if __name__ == "__main__":
#     try:
#         result = asyncio.run(run_agent())
#         print(result)
#     except:
#         pass



import asyncio  
import os       
import sys      
import json     

from typing import Optional  
from contextlib import AsyncExitStack  
from mcp import ClientSession, StdioServerParameters  
from mcp.client.stdio import stdio_client  

from google import genai
from google.genai import types
from google.genai.types import Tool, FunctionDeclaration
from google.genai.types import GenerateContentConfig

from dotenv import load_dotenv  
from system_prompt import get_system_prompt
import logging

load_dotenv()

class MCPClient:
    def __init__(self):
        """Initialize the MCP client and configure the Gemini API."""
        self.session: Optional[ClientSession] = None  
        self.exit_stack = AsyncExitStack() 

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

        self.genai_client = genai.Client(api_key=gemini_api_key)

    async def connect_to_server(self, server_script_path: str):
        """Connect to the MCP server and list available tools."""

        command = "python" if server_script_path.endswith('.py') else "node"

        server_params = StdioServerParameters(command=command, args=[server_script_path])

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))

        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools  

        print("\nConnected to server with tools:", [tool.name for tool in tools])

        self.function_declarations = convert_mcp_tools_to_gemini(tools)


    async def process_query(self, query: str) -> str:
        system_prompt = get_system_prompt()
        full_prompt = f"{system_prompt}\n\n{query}"

        conversation = [
            types.Content(role='user', parts=[types.Part.from_text(text=full_prompt)])
        ]
        final_text = []

        while True:
            response = self.genai_client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=conversation,
                config=types.GenerateContentConfig(
                    tools=self.function_declarations,
                ),
            )

            # Collect all text parts from all candidates
            got_function_call = False
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            got_function_call = True
                            tool_name = part.function_call.name
                            tool_args = part.function_call.args
                            print(f"\n[Gemini requested tool call: {tool_name} with args {tool_args}]")
                            try:
                                result = await self.session.call_tool(tool_name, tool_args)
                                function_response = {"result": result.content}
                            except Exception as e:
                                function_response = {"error": str(e)}
                            function_response_part = types.Part.from_function_response(
                                name=tool_name,
                                response=function_response
                            )
                            function_response_content = types.Content(
                                role='tool',
                                parts=[function_response_part]
                            )
                            # Add the function call and response to the conversation
                            conversation.append(part)
                            conversation.append(function_response_content)
                            break  # Only handle one tool call at a time
                        elif hasattr(part, "text") and part.text:
                            final_text.append(part.text)
                if got_function_call:
                    break  

            if not got_function_call:
                break  

        return "\n".join(final_text)


    async def chat_query(self, query: str) -> str:
        query = query.strip()
        try:
            logging.info("Processing query...")  # Debug
            response = await self.process_query(query)
            print("Processing complete.")  # Debug
            print("\n" + response)
            return response
        except Exception as e:
            print(f"Error during processing: {e}")
            return str(e)

    async def cleanup(self):
        await self.exit_stack.aclose()

def clean_schema(schema):
    if isinstance(schema, dict):
        schema.pop("title", None)  # Remove title if present

        # Recursively clean nested properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            for key in schema["properties"]:
                schema["properties"][key] = clean_schema(schema["properties"][key])

    return schema

def convert_mcp_tools_to_gemini(mcp_tools):
    gemini_tools = []

    for tool in mcp_tools:
        parameters = clean_schema(tool.inputSchema)

        function_declaration = FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=parameters  
        )

        gemini_tool = Tool(function_declarations=[function_declaration])
        gemini_tools.append(gemini_tool)

    return gemini_tools



async def main():
    """Main function to start the MCP client."""
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())







    # async def process_query(self, query: str) -> str:  

    #     system_prompt = get_system_prompt()

    #     full_prompt = f"{system_prompt}\n\n{query}"
    #     # system_prompt_content = types.Content(
    #     #     role='system',
    #     #     parts=[types.Part.from_text(text=system_prompt)]
    #     # )


    #     user_prompt_content = types.Content(
    #         role='user',  
    #         parts=[types.Part.from_text(text=full_prompt)]  
    #     )

    #     response = self.genai_client.models.generate_content(
    #         model='gemini-2.0-flash-001',  
    #         contents=[user_prompt_content],  
    #         config=types.GenerateContentConfig(
    #             tools=self.function_declarations,  
    #         ),
    #     )

    #     final_text = []  
    #     assistant_message_content = []  

    #     for candidate in response.candidates:
    #         if candidate.content and candidate.content.parts:
    #             for part in candidate.content.parts:
    #                 if isinstance(part, types.Part): 
    #                     if part.function_call:  
                           
    #                         function_call_part = part  
    #                         tool_name = function_call_part.function_call.name  
    #                         tool_args = function_call_part.function_call.args  

    #                         print(f"\n[Gemini requested tool call: {tool_name} with args {tool_args}]")

    #                         try:
    #                             result = await self.session.call_tool(tool_name, tool_args)  
    #                             function_response = {"result": result.content}  
    #                         except Exception as e:
    #                             function_response = {"error": str(e)}  

    #                         function_response_part = types.Part.from_function_response(
    #                             name=tool_name, 
    #                             response=function_response  
    #                         )

    #                         function_response_content = types.Content(
    #                             role='tool',  
    #                             parts=[function_response_part]  
    #                         )

    #                         response = self.genai_client.models.generate_content(
    #                             model='gemini-2.0-flash-001',  
    #                             contents=[
    #                                 user_prompt_content,  
    #                                 function_call_part,  
    #                                 function_response_content,  
    #                             ],
    #                             config=types.GenerateContentConfig(
    #                                 tools=self.function_declarations,  
    #                             ),
    #                         )

    #                     if part.function_call:
    #                         text = response.candidates[0].content.parts[0].text
    #                         if text is not None:
    #                             final_text.append(text)
    #                     else:
    #                         if part.text is not None:
    #                             final_text.append(part.text)

    #     return "\n".join(final_text)

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
#           "/Users/sameer/db-hackathon-2025/db-hackathon/scripts/mcp/gemini-mcp_server/server.py"
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


    async def process_query(self, query: str, prompt_name : str = "default") -> str:
        system_prompt = self.get_system_prompt(prompt_name=prompt_name)
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

    def extract_score_and_reasoning(self, response_text: str) -> dict:
        """
        Extracts the score and reasoning from the project_score prompt response text.
        Returns a dictionary with keys 'score' (int) and 'reasoning' (str).
        """
        import re

        score = None
        reasoning = ""

        # Try to find score out of 100 in the response text
        score_match = re.search(r"(\d{1,3})\s*(?:out of|\/|%)\s*100", response_text)
        if score_match:
            score = int(score_match.group(1))
            if score > 100:
                score = 100
            elif score < 0:
                score = 0

        # Try to extract reasoning - assume reasoning follows keywords like "reason", "explanation", or after score
        reasoning_match = re.search(r"(?:reason(?:ing)?|explanation|because|इसलिए|कारण|क्योंकि)[\s:\-]*([\s\S]+)", response_text, re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
            # Limit reasoning length to first paragraph or 300 chars
            reasoning = reasoning.split("\n")[0]
            if len(reasoning) > 300:
                reasoning = reasoning[:300] + "..."

        # If no explicit reasoning found, fallback to first 300 chars of response
        if not reasoning:
            reasoning = response_text.strip()[:300]

        return {"score": score, "reasoning": reasoning}


    async def chat_query(self, query: str, prompt_name: str = "default") -> str:
        query = query.strip()
        try:
            logging.info("Processing query...")  #
            response = await self.process_query(query, prompt_name)
            print("Processing complete.")  
            print("\n" + response)
            return response
        except Exception as e:
            print(f"Error during processing: {e}")
            return str(e)

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def get_project_score(self, project_details: dict) -> dict:
        """
        Get a score for the project based on its details.
        returns a dictionary with 'score' (int) and 'reasoning' (str).
        The score is out of 100, and reasoning is a brief explanation.
        """
        query = f"The details of the project is as follows: {json.dumps(project_details)}"
        try:
            response = await self.chat_query(query=query, prompt_name="project_score")
            response_dict = {"score": 0, "reasoning": "No response from server."}
            if response:
                response_dict = self.extract_score_and_reasoning(response)
                if response_dict["score"] is None:
                    response_dict["score"] = 0
                if not response_dict["reasoning"]:
                    response_dict["reasoning"] = "No reasoning provided."
            return response_dict
        except Exception as e:
            print(f"Error getting project score: {e}")
            return str(e)
    
   

    @staticmethod
    def get_system_prompt(prompt_name: str = "default") -> str:
        prompts = {
        "default" : """
        You are KrishiMitra, an expert AI assistant for Indian farmers, specializing in helping them plan and estimate the financial requirements for new agricultural projects.

        When a farmer wants to create a new project, your job is to:
        - Estimate the total amount of money needed for the project, considering:
            • The type of crop (commodity) the farmer wants to grow.
            • The latest local market prices for that commodity.
            • The weather forecast for the farmer’s district, including any risks (like drought, heavy rain, or storms) that could affect costs or yields.
            • The expected yield and any additional costs (seeds, fertilizer, labor, irrigation, etc.)—if this information is not provided, make reasonable assumptions based on typical values for the region and crop, and clearly state your assumptions.
            • The expected profit share percentage for investors, based on the crop, market trends, and risk factors.
        - Suggest a reasonable profit share percentage for investors, based on the crop, market trends, and risk factors.
        - Clearly explain your calculations and reasoning in simple, practical language, using rupees, dates, and Celsius.
        - Advise the farmer if the current weather and market conditions are favorable for starting the project, and if not, suggest what to watch out for.

        You have access to real-time tools that can:
        - If the query is not related to the project, you should just answer with general information about the agriculture.
        - Detect the farmer’s location using their name.
        - Fetch up-to-date commodity prices from the local market.
        - Get the weather forecast for the farmer’s district.

        Your responses should be:
        - Supportive, clear, and tailored for rural Indian farmers.
        - Focused on helping the farmer make the best financial decision for their situation.
        - Actionable, with step-by-step reasoning and practical advice.
        - Strict: All your answers should be in clear, simple Hindi, suitable for rural Indian farmers.


        Do not ask the user for any further information. If any required data (like yield or costs) is missing, make the best possible estimate using typical values, local context, or reasonable hypotheses, and clearly state your assumptions in your answer.
        """,
        "project_score" : """
        You are KrishiMitra, an expert AI assistant for Indian farmers, specializing in analyzing agricultural projects' financial viability.

        When given details about a project including:
        - The type of crop (crop_type)
        - The land area to be cultivated (land_area)
        - The duration of the project in months (duration_in_months)
        - The total amount of loan needed (amount_needed)
        - The interest rate on the loan (interest_rate)

        Your task is to:
        - Analyze whether the farmer can pay the specified interest to the lenders.
        - Determine if the farmer can still make a profit after repaying the loan with interest.
        - Provide a score out of 100 indicating the financial viability and risk of the project.
        - Include a short reasoning behind the given score, explaining the key factors affecting the outcome.

        Your response should be a JSON object in the following format:
        {"score": score, "reasoning": reasoning}

        Your response should be:
        - Supportive, clear, and tailored for rural Indian farmers.
        - Focused on helping the farmer understand the financial feasibility of their project.
        - Actionable, with simple explanations and practical advice.
        - All your answers should be in clear, simple Hindi, suitable for rural Indian farmers.

        Do not ask the user for any further information. If any required data is missing, make reasonable assumptions based on typical values and clearly state these assumptions in your answer.
        """
        }

        return prompts.get(prompt_name, prompts["default"])

    # def simple_llm_call(system_prompt: str, project_details: dict) -> str:
    #     """
    #     Calls the Gemini LLM directly with a system prompt and project details, returns the response text.
    #     """
    # import os
    # import json
    # import genai
    # from genai import types

    # gemini_api_key = os.getenv("GEMINI_API_KEY")
    # if not gemini_api_key:
    #     raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")
    # client = genai.Client(api_key=gemini_api_key)

    # full_prompt = f"{system_prompt}\n\nThe details of the project is as follows: {json.dumps(project_details)}"
    # user_prompt_content = types.Content(
    #     role='user',
    #     parts=[types.Part.from_text(text=full_prompt)]
    # )
    # response = client.models.generate_content(
    #     model='gemini-2.0-flash-001',
    #     contents=[user_prompt_content],
    # )
    # final_text = []
    # for candidate in response.candidates:
    #     if candidate.content and candidate.content.parts:
    #         for part in candidate.content.parts:
    #             if hasattr(part, "text") and part.text:
    #                 final_text.append(part.text)
    # return "\n".join(final_text)


def clean_schema(schema):
    if isinstance(schema, dict):
        schema.pop("title", None)  # Remove title if present

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
        await client.process_query()
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

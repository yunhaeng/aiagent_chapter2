import sys
import asyncio
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import logging
from langchain.agents import AgentExecutor
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 로거 설정
logger = logging.getLogger('agent_langchain')
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

model = ChatOpenAI(model="gpt-4.1-nano")

async def chat(message: str):
    try:
        logger.info(f"Starting chat with message: {message}")
        async with MultiServerMCPClient(
            {
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"],
                },
                # "filesystem":{
                # "command": "npx",
                # "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
                # },
                # "sequential-thinking": {
                # "command": "npx",
                # "args": [
                #     "-y",
                #     "@modelcontextprotocol/server-sequential-thinking"
                # ]
                # },
                # "brave-search": {
                # "command": "npx",
                # "args": [
                #     "-y",
                #     "@modelcontextprotocol/server-brave-search"
                # ],
                # "env": {
                #     "BRAVE_API_KEY": "BSAAvbM4tzJZv2wMYX1JxwSn_EJNQBJ"
                # }
                # },
            }
        ) as client:
            logger.debug("MCP client initialized")
            
            agent = create_react_agent(model, client.get_tools())
            logger.debug("Agent created successfully")
            total_message = f"""
            질문: {message}
            """
            response = await agent.ainvoke({"messages": total_message})
            print(response)
            # Extract final text response
            if isinstance(response, dict) and 'messages' in response:
                messages = response['messages']
                # Get the last AIMessage content
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and msg.content:
                        print(msg.content)
                        return str(msg.content)
            
            # Fallback to original response handling
            if isinstance(response, dict):
                return response.get('output', str(response))
            return str(response)

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise e

if __name__ == "__main__":
    asyncio.run(chat(""""""))
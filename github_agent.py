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
                "filesystem":{
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
                },
                "github": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-github"
                    ],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
                    }
                }
            }
        ) as client:
            logger.debug("MCP client initialized")
            
            agent = create_react_agent(model, client.get_tools())
            logger.debug("Agent created successfully")
            total_message = f"""
            질문: {message}
            """
            #response = await agent.ainvoke({"messages": total_message})
            stream = agent.astream({"messages": total_message})
            async for response in stream:
                print(response)

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise e

if __name__ == "__main__":
    #asyncio.run(chat("""sample.py 파일에 들어있는 message가 뭐야?"""))
    asyncio.run(chat("""만약 aiagent_chapter2라는 이름의 레포지토리가 없으면 생성하고 지금 파일 디렉토리를 push 해줄래? commit message는 first commit으로 해줘"""))
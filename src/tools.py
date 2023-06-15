from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage
from langchain.tools import (format_tool_to_openai_function, YouTubeSearchTool, MoveFileTool)
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", client=any)
tools = [YouTubeSearchTool(), MoveFileTool()]
functions = [format_tool_to_openai_function(tool) for tool in tools]

message = llm.predict_messages([HumanMessage(content="move file foo to bar")], functions=functions)
print(f"message: {message}")
print(f"additional kwargs: {message.additional_kwargs['function_call']}")
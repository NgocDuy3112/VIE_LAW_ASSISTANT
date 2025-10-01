from langchain_ollama import ChatOllama
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

from langchain_core.messages import (
    SystemMessage, 
    AIMessage, 
    ToolMessage, 
)

from uuid import uuid4

from workflow.llm import get_llm
from config import settings


plan_llm = get_llm(model_name="ollama/qwen3:1.7b", temperature=0.1)
tool_llm = get_llm(model_name="ollama/qwen2.5:0.5b", temperature=0.1).bind_tools()
chat_llm = get_llm(model_name="lmstudio/seallms-v3-1.5b-chat", temperature=0.1)



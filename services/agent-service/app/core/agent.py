from datetime import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from graph.state import AgentState
from graph.llm import ChatModel
from graph.nodes import *
from graph.stream import *

from config import settings



supervisor_llm = ChatModel("ollama/qwen3:1.7b", temperature=0.1)
rag_llm = ChatModel("ollama/qwen2.5:0.5b", temperature=0)
respone_llm = ChatModel("lmstudio/seallms-v3-1.5b-chat", temperature=0.1)




async def graph_ainvoke(messages: list[HumanMessage]):
    async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_CHECKPOINTS_URI) as checkpointer:
        config = RunnableConfig(
            recursion_limit=25,
            configurable={
                "thread_id": hash(datetime.datetime.today().isoformat())
            }
        )
        mcp_client = MultiServerMCPClient(
            {
                "document": {
                    "url": "http://document-service:8002/mcp",
                    "transport": "streamable_http"
                },
                # "web-crawler": {
                #     "url": "http://web-crawler-service:8003/mcp",
                #     "transport": "streamable_http"
                # }
            }
        )
        tools = await mcp_client.get_tools()
        builder = StateGraph(AgentState)
        builder.add_node("supervisor", make_supervisor_node(llm=supervisor_llm, members=['response', 'supervisor', 'rag']))
        builder.add_node("rag", make_rag_agent(llm=rag_llm, tools=tools))
        builder.add_node("response", make_response_node(llm=respone_llm))
        builder.add_edge(START, "supervisor")
        graph = builder.compile(checkpointer=checkpointer)
        messages = {'messages': messages}
        response = await graph.ainvoke(input=messages)
        return response
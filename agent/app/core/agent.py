from langgraph.graph import END, START, StateGraph

from graph.llm import ChatMessage, ChatModel
from graph.nodes import make_rag_node, make_response_node, route_node
from graph.state import AgentState
from modules.documents.tools import retrieve_document
from config import settings


supervisor_llm = ChatModel(f"vllm/{settings.LLM_MODEL}", temperature=0.1)
response_llm = ChatModel(f"vllm/{settings.LLM_MODEL}", temperature=0.1)


def build_agent_graph():
    builder = StateGraph(AgentState)
    async def route(state: AgentState) -> AgentState:
        return await route_node(state, supervisor_llm)

    builder.add_node("route", route)
    builder.add_node("retrieve", make_rag_node(retrieve_document))
    builder.add_node("respond", make_response_node(response_llm))

    builder.add_edge(START, "route")
    builder.add_conditional_edges(
        "route",
        lambda state: state.get("route", "response"),
        {"rag": "retrieve", "response": "respond"},
    )
    builder.add_edge("retrieve", "respond")
    builder.add_edge("respond", END)
    return builder.compile()


agent_graph = build_agent_graph()


async def agent_invoke(messages: list[ChatMessage]) -> ChatMessage:
    result = await agent_graph.ainvoke({"messages": messages})
    return result["answer"]

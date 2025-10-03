from typing import Literal
from typing_extensions import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    SystemMessage, 
    HumanMessage
)
from langchain_core.tools.base import BaseTool

from langgraph.types import Command
from langgraph.graph import END
from langgraph.prebuilt import create_react_agent

from graph.state import AgentState




def make_supervisor_node(llm: BaseChatModel, members: list[str]):
    options = ["END"] + members
    class Router(TypedDict):
        next: Literal[*options] # type: ignore

    def supervisor_node(state: AgentState) -> Command[Literal[members, END]]: # type: ignore
        messages = [
            SystemMessage(
                content=f"""
                You are a supervisor tasked with managing a conversation between the following workers: {members}. Given the following user request, respond with the worker to act next. Each worker will perform a task and respond with their results and status. When finished, respond with END.
                """
            )
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke({'messages': messages})
        goto = response["next"]
        if goto == 'END': 
            goto = END
        return Command(goto=goto, update={"next": goto})
    return supervisor_node



def make_rag_agent(llm: BaseChatModel, tools: list[BaseTool]):
    class DocumentsList(TypedDict):
        documents: list[str]

    def rag_agent(state: AgentState) -> Command[Literal["supervisor"]]:
        tool_agent = create_react_agent(llm, tools, state_schema=AgentState, response_format=DocumentsList)
        messages = [
            SystemMessage(
                content=f"""
                You are an AI agent tasked with retrieving documents from various sources. You are given those tools:
                - retrieve_document: Use this tool when the user's question requires information that cannot be answered from general knowledge. It performs a semantic search to find the most relevant documents.
                
                Use only those tools to retrieve the documents.
                """
            )
        ]
        response = tool_agent.invoke({'messages': messages})
        documents = response["documents"]
        return Command(
            update={
                'documents': documents,
            },
            goto='supervisor'
        )
    return rag_agent



def make_response_node(llm: BaseChatModel):
    def response_node(state: AgentState) -> Command[Literal["supervisor"]]: # type: ignore
        messages = [
            SystemMessage(
                content=f"""
                Bạn là một trợ lý AI có nhiệm vụ tóm tắt lại tất cả các thông tin dựa trên các tài liệu đã được cung cấp. Bạn hãy tóm gọn lại tất cả các thông tin của các tài liệu đó bằng một đoạn văn không quá 1000 từ. Đây là các tài liệu được cung cấp:
                """
            )
        ] + state['documents']
        response = llm.invoke({'messages': messages})
        return Command(
            update={
                'messages': HumanMessage(
                    content=response['messages'][-1].content
                )
            },
            goto='supervisor'
        )
    return response_node




from operator import add
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from uuid import uuid4

from langchain_core.messages import BaseMessage


def create_uuid_string():
    return str(uuid4())


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add]
    next: Literal['response', 'supervisor', 'rag']
    documents: list[str]
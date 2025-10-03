from typing import Any
from collections.abc import AsyncGenerator

from langchain_core.messages import ToolCallChunk, AIMessageChunk

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command



async def process_tool_call_chunk(chunk: ToolCallChunk):
    """Process a tool call chunk and return a formatted string."""
    tool_call_str = ""

    tool_name = chunk.get("name", "")
    args = chunk.get("args", "")

    if tool_name:
        tool_call_str += f"\n\n< TOOL CALL: {tool_name} >\n\n"
    if args:
        tool_call_str += args
    return tool_call_str



async def stream_graph_responses(
    input: dict[str, Any] | Command,
    graph: CompiledStateGraph,
    **kwargs
) -> AsyncGenerator[str, None]:
    """Asynchronously stream the result of the graph run.

    Args:
        input: The input to the graph.
        graph: The compiled graph.
        **kwargs: Additional keyword arguments.

    Returns:
        str: The final LLM or tool call response
    """
    async for message_chunk, _ in graph.astream(
        input=input,
        stream_mode="messages",
        **kwargs
        ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.response_metadata:
                finish_reason = message_chunk.response_metadata.get("finish_reason", "")
                if finish_reason == "tool_calls":
                    yield "\n\n"

            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]
                tool_call_str = await process_tool_call_chunk(tool_chunk)
                yield tool_call_str
                
            else:
                # Ensure content is always a string
                content = message_chunk.content
                if isinstance(content, str):
                    yield content
                elif isinstance(content, list):
                    # Convert list content to string representation
                    yield str(content)
                else:
                    # Fallback for any other type
                    yield str(content)
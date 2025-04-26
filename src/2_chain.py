from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
import random
from typing import Literal
import os
from IPython.display import Image
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage

os.environ["AZURE_OPENAI_API_KEY"]="api_key"
os.environ["AZURE_OPENAI_ENDPOINT"]="endpoint"

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

def draw_graph(graph):
    try:
        img = Image(graph.get_graph().draw_mermaid_png())
        with open("2_chain.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)

# This is a Node
# Nodes take current graph state as input and operate on the state
def tool_calling_llm(state: State):
    print('At llm with tools node')
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_version="2025-03-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    tools = [multiply]
    llm_with_tools = llm.bind_tools(tools)
    # Messages are appended instead of overwritten 
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


if __name__ == '__main__':
    # Build graph
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_edge(START, "tool_calling_llm")
    builder.add_edge("tool_calling_llm", END)
    graph = builder.compile()

    # Draw graph
    draw_graph(graph)

    # Run graph with a non-tool input
    messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
    for m in messages['messages']:
        m.pretty_print()

    # Run graph with a tool input
    # Note that the output messages don't contain the result of the tool 6.
    # The LLM creates a ToolMessage for calling the Tool with the right parameters
    # However, there is no Node in the graph where the tool is called and the result is added to the messages state.
    messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
    for m in messages['messages']:
        m.pretty_print()




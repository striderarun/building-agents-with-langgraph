from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
import os
from IPython.display import Image
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage

os.environ["AZURE_OPENAI_API_KEY"]="api_key"
os.environ["AZURE_OPENAI_ENDPOINT"]="endpoint"

def draw_graph(graph):
    try:
        img = Image(graph.get_graph().draw_mermaid_png())
        with open("4_agent.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)

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

@tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

@tool
def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [add, multiply, divide]

# The Assistant node is just our model with bound tools.
# Nodes take current graph state as input and operate on the state
def assistant(state: State):
    # System message
    sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_version="2025-03-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )
    llm_with_tools = llm.bind_tools(tools)
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


if __name__ == '__main__':
    # Graph for a basic ReAct agent
    builder = StateGraph(State)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    # Add an edge from the tools node back to the LLM, forming a cycle.
    # After the assistant node executes, tools_condition checks if the model's output is a tool call.
    # If it is a tool call, the flow is directed to the tools node.
    # The tools node connects back to assistant.
    # This loop continues as long as the model decides to call tools.
    # If the model response is not a tool call, the flow is directed to END, terminating the process.
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()

    # Draw
    draw_graph(react_graph)

    # Invoke graph for input
    messages = [HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5")]
    messages = react_graph.invoke({"messages": messages})

    for m in messages['messages']:
        m.pretty_print()




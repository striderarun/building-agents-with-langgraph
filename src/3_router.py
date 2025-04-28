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
        with open("3_router.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)

# This is a Node
# Nodes take current graph state as input and operate on the state
def tool_calling_llm(state: State):
    print('At tool_calling_llm node')
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
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


if __name__ == '__main__':
    # Build graph
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode([multiply]))
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges(
        "tool_calling_llm",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools node
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", END)
    graph = builder.compile()

    # Draw graph
    # draw_graph(graph)

    from langchain_core.messages import HumanMessage
    # Run graph with a tool input
    # Note that the output messages contains the result of the tool 4. 
    # The LLM in the "tool_calling_llm" node creates a ToolMessage for calling the Tool with the right parameters
    # The conditional edge between "tool_calling_llm" and "tools" sees that the LLM created a ToolMessage.
    # The ToolMessage flows through the conditional edge and is processed in the ToolNode "tools" where the tool is actually invoked.
    # The Tool Node appends the result of the tool call in the messages state.
    # Now, the last message in the messages state is just the number "4".

    # However, What if you want the LLM to process the tool output and take an appropriate response? 
    # For example, if you want to present a nice response to the user like "Sure, the result of multiplying 2 and 2 is 4", then you can feed the result of the tool call back to the LLM node.
    # Congratulations, you just built an agent! Check 4_agent.py
    messages = [HumanMessage(content="Hello, what is 2 multiplied by 2?")]
    messages = graph.invoke({"messages": messages})
    for m in messages['messages']:
        m.pretty_print()




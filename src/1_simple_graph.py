from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
import random
from typing import Literal
import os
from IPython.display import Image

os.environ["AZURE_OPENAI_API_KEY"]="openai_key"
os.environ["AZURE_OPENAI_ENDPOINT"]="endpoint"

def draw_graph(graph):
    try:
        img = Image(graph.get_graph().draw_mermaid_png())
        with open("1_simple_graph.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)

# This class holds the graph state
class State(TypedDict):
    # A single string as the graph state
    graph_state: str

# Nodes
# Nodes accept the graph state as input and operate on the state
def node_1(state):
    print("---Node 1---")
    return {"graph_state": state['graph_state'] +" I am"}

def node_2(state):
    print("---Node 2---")
    return {"graph_state": state['graph_state'] +" happy!"}

def node_3(state):
    print("---Node 3---")
    return {"graph_state": state['graph_state'] +" sad!"}

# Conditional edge. This function decides which branch to run.
# Edges also accept the graph state as input and operate on the state to make routing decisions 
# The state operated on by a node is passed down to the downstream nodes
def decide_mood(state) -> Literal["node_2", "node_3"]:
    
    # Often, we will use state to decide on the next node to visit
    print('In conditional edge')
    print(state['graph_state'])
    user_input = state['graph_state'] 

    # Here, let's just do a random 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


# Build graph
# The graph state is passed down the graph between nodes
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mood)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# Draw graph
# draw_graph(graph)

# Invoke
result = graph.invoke({"graph_state" : "Hi, this is Lance."})
print(result)
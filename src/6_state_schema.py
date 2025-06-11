from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
import random
from typing import Literal
import os
from IPython.display import Image
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ValidationError

os.environ["AZURE_OPENAI_API_KEY"]="api_key"
os.environ["AZURE_OPENAI_ENDPOINT"]="endpoint"

def draw_graph(graph):
    try:
        img = Image(graph.get_graph().draw_mermaid_png())
        with open("1_simple_graph.png", "wb") as fout:
            fout.write(img.data)
    except Exception as e:
        print(e)

# This class holds the graph state
# TypedDict allows you to specify keys and their value types
# But these are not enforced at runtime!
class State(TypedDict):
    name: str
    mood: Literal["happy","sad"]

# As mentioned, `TypedDict` and `dataclasses` provide type hints but they don't enforce types at runtime. 
# This means you could potentially assign invalid values without raising an error!
# For example, we can set `mood` to `mad` even though our type hint specifies `mood: list[Literal["happy","sad"]]`
@dataclass
class DataclassState:
    name: str
    mood: Literal["happy","sad"]

# [Pydantic](https://docs.pydantic.dev/latest/api/base_model/) is a data validation and settings management library using Python type annotations. 
# Pydantic can perform validation to check whether data conforms to the specified types and constraints at runtime.
class PydanticState(BaseModel):
    name: str
    mood: str # "happy" or "sad" 

    @field_validator('mood')
    @classmethod
    def validate_mood(cls, value):
        # Ensure the mood is either "happy" or "sad"
        if value not in ["happy", "sad"]:
            raise ValueError("Each mood must be either 'happy' or 'sad'")
        return value
    
# Nodes
# Nodes accept the graph state as input and operate on the state
def node_1(state):
    print("---Node 1---")
    return {"name": state['name'] + " is ... "}

def node_2(state):
    print("---Node 2---")
    # Update state['mood'] by returning a dict
    return {"mood": "happy"}

def node_3(state):
    print("---Node 3---")
    # Update state['mood'] by returning a dict
    return {"mood": "sad"}

def decide_mood(state) -> Literal["node_2", "node_3"]:
        
    # Here, let's just do a 50 / 50 split between nodes 2, 3
    if random.random() < 0.5:

        # 50% of the time, we return Node 2
        return "node_2"
    
    # 50% of the time, we return Node 3
    return "node_3"

if __name__=='__main__':
    # Build graph with TypedDict state
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

    # Invoke
    result = graph.invoke({"name" : "Lance"})

    # This works even though 'mad' is not allowed
    dataclass_instance = DataclassState(name="Lance", mood="mad")

    # Pydantic adds validation to types
    try:
        state = PydanticState(name="John Doe", mood="mad")
    except ValidationError as e:
        print("Validation Error:", e)

    # Build graph with PydanticState
    pydantic_builder = StateGraph(PydanticState)
    pydantic_builder.add_node("node_1", node_1)
    pydantic_builder.add_node("node_2", node_2)
    pydantic_builder.add_node("node_3", node_3)

    # Logic
    pydantic_builder.add_edge(START, "node_1")
    pydantic_builder.add_conditional_edges("node_1", decide_mood)
    pydantic_builder.add_edge("node_2", END)
    pydantic_builder.add_edge("node_3", END)

    # Add
    pydantic_graph = pydantic_builder.compile()

    # Wrong mood value
    result = graph.invoke(PydanticState(name="Lance",mood="sad"))
    print(result)
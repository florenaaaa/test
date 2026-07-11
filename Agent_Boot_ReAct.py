import os
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages # reduce函数。允许将内容追加到状态中，而不会发生覆盖
from langgraph.graph import StateGraph, START,END
from dotenv import load_dotenv # 存储敏感信息，如API密钥或配置信息
from langgraph.prebuilt import ToolNode

load_dotenv()

# Annotated
# email = Annotated[str, "This has to be a valid email format!"]
# print(email.__metadata__)
# ('This has to be a valid email format!',)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def add(a: int, b: int):
    """This is an addition function that adds 2 numbers together"""

    return a + b

@tool
def subtract(a: int, b: int):
    """Subtraction function"""
    return a- b

@tool
def multiple(a: int, b: int):
    """Multiplication function"""
    return a * b

tools = [add, subtract, multiple]

model = ChatOpenAI(model="qwen3.5-plus").bind_tools(tools)

def model_call(state: AgentState) -> AgentState:
    sysyem_prompt = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your ability"
    )
    response = model.invoke([sysyem_prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state:AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

graph.add_edge("tools", "our_agent")
app = graph.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 40 + 12 and then multiply the result by 6.Also tell me a joke")]}
print_stream(app.stream(inputs, stream_mode="values"))



import operator
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    requirement: str
    current_code: str
    excution_status: str
    reviewer_feedback: str
    iterations: Annotated[int, operator.add]
    stdout: str  # 运行的标准输出
    stderr: str  # 运行报错信息
    target_file: str # 目标文件名

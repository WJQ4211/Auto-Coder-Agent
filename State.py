import operator
from typing import TypedDict, Annotated
import subprocess
import tempfile
import os

class GraphState(TypedDict):
    requirement: str
    current_code: str
    excution_status: str
    reviewer_feedback: str
    iterations: Annotated[int, operator.add]
    stdout: str  # 运行的标准输出
    stderr: str  # 运行报错信息

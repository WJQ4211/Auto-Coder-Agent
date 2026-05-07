import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from State import GraphState
import os


deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    api_key=deepseek_api_key, 
    base_url="https://api.deepseek.com", 
    model="deepseek-v4-flash",  
    max_retries=3        
)

def extract_python_code(text: str) -> str:
    """"
    从文本中提取Python代码块,如果没有找到代码块,则返回原始文本。"""
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def coder_node(state: GraphState) -> dict:
    print("Coder正在编写代码...")
    req = state["requirement"]
    feedback = state.get("reviewer_feedback", "")

    if not feedback:
        prompt = f"你是一个优秀的python工程师, 请根据以下要求编写代码. 只需要输出代码, 必须使用python代码块格式. \n\n要求: {req}"
    else:
        old_code = state.get("current_code", "")
        prompt = f"""之前你的代码运行失败了.原始需求:{req}.错误代码:\n```python\n{old_code}\n```
        修改意见:\n{feedback}
        请根据意见修复代码. 只需要输出代码, 必须使用python代码块格式."""
    response = llm.invoke([HumanMessage(content=prompt)])
    print(f"[测试代码]Coder的回复:\n{response.content}")
    code = extract_python_code(response.content)
    print(f"[测试代码]Coder写的代码:\n{code}")
    return {"current_code": code, "iterations": 1}


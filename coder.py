import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from State import GraphState
import os
from dotenv import load_dotenv


load_dotenv()
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
    messages = state["messages"]

    feedback = state.get("reviewer_feedback", "")

    if not feedback:
        pass
    else:
        messages = messages + [HumanMessage(content=f"之前你的代码报错了, 请修复.错误代码:\n修改意见:\n{feedback}\n请根据意见修复代码. 只需要输出代码, 必须使用python代码块格式.")]
    
    
    response = llm.invoke(messages)
    print(f"[测试代码]Coder的回复:\n{response.content}")
    code = extract_python_code(response.content)
    print(f"[测试代码]Coder写的代码:\n{code}")
    return {"current_code": code, "iterations": 1, "messages": [response]}


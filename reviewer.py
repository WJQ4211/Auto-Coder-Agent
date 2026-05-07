from State import GraphState
from coder import llm
from langchain_core.messages import HumanMessage, SystemMessage

def reviewer_node(state: GraphState) -> dict:
    print("Reviewer正在分析报错并形成修改建议...")
    req = state["requirement"]
    code = state.get("current_code", "")
    stderr = state.get("stderr", "")

    system_prompt = f"你是一个经验丰富的python架构师.你的任务是分析这段运行失败的代码及其报错日志.请指出导致stderr中出错的根本原因.\
        不要直接写出完整代码, 而是告诉Coder应该怎样去改"
    user_prompt = f"原始需求:{req}\n报错代码:\n```python\n{code}\n```\n错误信息:\n{stderr}"
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
    )

    print(f"[测试代码]Review的反馈意见:{response.content}")

    return {"reviewer_feedback": response.content}
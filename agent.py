from langgraph.graph import StateGraph, START, END
from coder import coder_node
from reviewer import reviewer_node
from sandbox import sandbox_node
from State import GraphState

def router_after_sandbox(state) -> str:
    status = state.get("excution_status", "")
    iterations = state.get("iterations", 0)

    if status == "success":
        return "END"
    elif iterations >= 5:
        print("达到最大迭代次数")
        return "END"
    else:
        return "REVIEWER"
    
workflow = StateGraph(GraphState)
workflow.add_node("CODER", coder_node)
workflow.add_node("REVIEWER", reviewer_node)
workflow.add_node("SANDBOX", sandbox_node)

workflow.add_edge(START, "CODER")
workflow.add_edge("CODER", "SANDBOX")
workflow.add_conditional_edges(
    "SANDBOX",
    router_after_sandbox,
    {
        "END": END,
        "REVIEWER": "REVIEWER"
    }
)
workflow.add_edge("REVIEWER", "CODER")
app = workflow.compile()

# 测试运行
if __name__ == "__main__":
    requirement = "定义一个字典包含 {'a': 1}，然后打印出键为 'b' 的值。"
    print("=== 开始执行 Auto-Coder 任务 ===")
    print(f"需求: {requirement}\n")
    
    initial_state = {
        "requirement": requirement, 
        "iterations": 0
    }
    final_state = app.invoke(initial_state)

    print("总重试次数:", final_state["iterations"])
    print("最终状态:", final_state["excution_status"])
    print("最终可用代码:\n", final_state["current_code"])




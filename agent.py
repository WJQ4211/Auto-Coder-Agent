from langgraph.graph import StateGraph, START, END
from coder import coder_node
from reviewer import reviewer_node
from sandbox import sandbox_node
from State import GraphState
from langgraph.checkpoint.sqlite import SqliteSaver
import os
from langchain_core.messages import HumanMessage, SystemMessage

def router_after_sandbox(state) -> str:
    status = state.get("excution_status", "")
    iterations = state.get("iterations", 0)

    if status == "success":
        return "WRITER"
    elif iterations >= 5:
        print("达到最大迭代次数")
        return "END"
    else:
        return "REVIEWER"
    
def file_writer_node(state: GraphState) -> dict:
    code = state["current_code"]
    filename = state.get("target_file", "output.py")
    os.makedirs("./generated_code", exist_ok=True)
    full_path = os.path.join("./generated_code", filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"代码已写入{full_path}")
    return {}

    
def create_agent(memory):   
    workflow = StateGraph(GraphState)
    workflow.add_node("CODER", coder_node)
    workflow.add_node("REVIEWER", reviewer_node)
    workflow.add_node("SANDBOX", sandbox_node)
    workflow.add_node("WRITER", file_writer_node)

    workflow.add_edge(START, "CODER")
    workflow.add_edge("CODER", "SANDBOX")
    workflow.add_conditional_edges(
        "SANDBOX",
        router_after_sandbox,
        {
            "WRITER": "WRITER",
            "END": END,
            "REVIEWER": "REVIEWER"
        }
    )
    workflow.add_edge("REVIEWER", "CODER")
    workflow.add_edge("WRITER", END)
    # 编写记忆功能
    app = workflow.compile(checkpointer=memory, interrupt_before=["WRITER"])
    return app
# 测试运行
if __name__ == "__main__":
    
    file_path = "./checkpoint.db"
    # 如果文件不存在（not exists），才去创建和写入
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass
    else:
        # 如果文件已经存在，直接 pass（无事发生）
        pass
    # 后续的代码必须全在with下包裹
    with SqliteSaver.from_conn_string("./checkpoint.db") as memory:
        app = create_agent(memory)
        thread_id = input("请输入线程ID, 输入旧ID则恢复进度:")
        config = {"configurable": {"thread_id": thread_id}}


        while True:
            state = app.get_state(config=config)
            # 如果当前的情况是挂起了
            if state.next:
                print("\n[系统提示]检测到审批任务.输入'y'确认写入文件, 'n'取消, 也可以直接输入修改意见让我继续修改. 按回车键继续")
                user_input = input(">>")
                if user_input.lower() == 'y':
                    app.invoke(None, config=config)
                else:
                    # 如果不同意写入, 则用户可以写出自己的意见, 让agent自己去跑
                    app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
            else:
                user_input = input("请随时告诉我你的需求:")
                if user_input == "exit":
                    break
                app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)




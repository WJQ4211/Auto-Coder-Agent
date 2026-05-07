from State import GraphState
from excute_code_sandbox import excute_code_sandbox

def sandbox_node(state: GraphState) -> dict:
    print("Sandbox正在执行代码...")
    code = state.get("current_code", "")
    result = excute_code_sandbox(code)
    if result["status"] == "success":
        print(f"Sandbox执行成功,输出:{result['stdout'].strip()}")
    else:
        print(f"Sandbox执行失败, 错误信息:{result['stderr'].strip()}")
    return {
        "excution_status": result["status"],
        "stdout": result["stdout"],
        "stderr": result["stderr"]
    }



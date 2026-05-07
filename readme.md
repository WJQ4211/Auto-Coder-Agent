这是一份为你量身定制的《自动化代码生成与修复智能体 (Auto-Coder Agent) 开发文档》。这份文档采用了标准的大厂技术文档结构，你可以直接将其作为你周末开发的蓝图，后续也可以提取其中的核心术语写进简历。

------

# 自动化代码生成与修复智能体 (Auto-Coder Agent) 开发文档 v1.0

## 1. 项目概述

### 1.1 项目背景

当前大型语言模型（LLM）在代码生成任务中表现优异，但生成的代码常伴随语法错误、未定义变量或逻辑缺陷（Bug）。传统依靠人类开发者手动测试和微调的方式效率低下。

### 1.2 项目目标

构建一个基于“Actor-Evaluator”（执行者-评估者）架构的多智能体（Multi-Agent）系统。该系统能够根据自然语言需求自动生成代码，在隔离的沙盒环境中自动执行并捕获日志，进而基于报错信息进行自我反思（Reflection）与迭代修复，最终输出可稳定运行的代码。

## 2. 系统架构设计

系统整体采用闭环反馈机制（Closed-loop Feedback），核心由三大模块与一个主控循环构成：

1. **Coder Agent（代码生成节点）：** 负责将自然语言需求转化为初始代码，或根据修改建议输出迭代后的代码。
2. **Execution Sandbox（安全执行沙盒）：** 负责在一个受限、隔离的环境中执行生成的代码，并精准捕获标准输出（stdout）和标准错误（stderr）。
3. **Reviewer Agent（反思与评估节点）：** 担任“代码审查员”，接收沙盒传回的报错日志，结合原始需求进行根因分析，生成带有明确修改指令的 Prompt 喂回给 Coder Agent。

## 3. 技术选型

- **开发语言：** Python 3.10+
- **LLM 交互框架：** LangChain 或 AutoGen（推荐使用纯原生 Prompt 配合简单控制流，降低框架黑盒带来的调试负担）。
- **大模型支持：**
    - Coder/Reviewer 引擎：调用 DeepSeek-Coder API 或 Qwen-Coder API（成本极低且代码能力强）。
- **沙盒技术（分阶段实施）：**
    - ** Docker Engine API for Python (`docker-py`)，实现容器级隔离。
- **代码分析工具：** Python 内置 `ast` 模块（用于初步检查语法树是否完整）。

## 4. 核心模块详细设计

### 4.1 主控状态机 (Main Control Loop)

- **逻辑流转：** `User Prompt` -> `Coder` -> `Sandbox` -> `Reviewer` -> `Coder`
- **终止条件：**
    1. 沙盒执行返回状态码 `0`（Success，无报错）。
    2. 达到最大重试次数上限（`MAX_RETRIES = 5`），抛出 `MaxRetriesExceeded` 异常并输出最后一次尝试的代码。

### 4.2 Coder Agent (代码生成器)

- **输入：**
    - 首次：用户自然语言需求。
    - 迭代：用户需求 + 历史错误代码 + Reviewer 提供的修改建议。
- **输出格式约束：** 强制要求模型使用 Markdown 格式（````python ... ````）输出纯净代码，避免输出无关的解释性文字，方便下游正则提取。

### 4.3 Execution Sandbox (执行沙盒) - 核心难点

- **安全机制：**
    - 必须设置超时时间（例如 `timeout=10` 秒），防止模型写出死循环代码（如 `while True:`）耗尽宿主机资源。
- **执行与捕获逻辑：**
    1. 将 Coder 生成的代码落盘为临时文件 `temp_script.py`。
    2. 通过 `subprocess.run()` 执行该文件。
    3. 捕获 `returncode`、`stdout`（打印信息）和 `stderr`（Traceback 报错）。

### 4.4 Reviewer Agent (反思器)

- **系统提示词 (System Prompt) 设计要点：**

    > "你是一个资深的Python架构师。你的任务是分析这段运行失败的代码及其报错日志。请指出导致 `stderr` 中错误的根本原因，并给出具体的代码修改建议。不要直接写出完整代码，而是告诉 Coder 应该怎么改。"

- **输入封装：** `[原始需求] + [崩溃的代码] + [Traceback 报错信息]`。

## 5. 核心代码伪代码 (Demo 级架构)

Python

```
import subprocess
import re

# 1. 提取代码的工具函数
def extract_code(llm_response: str) -> str:
    match = re.search(r'```python\n(.*?)\n```', llm_response, re.DOTALL)
    return match.group(1) if match else ""

# 2. 沙盒执行函数
def run_in_sandbox(code: str, timeout_sec: int = 5) -> dict:
    with open("temp_script.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    try:
        # 使用 subprocess 捕获输出，并设置超时
        result = subprocess.run(
            ["python", "temp_script.py"],
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "Timeout Exception: Code execution exceeded limit."}

# 3. 主循环逻辑 (Main Workflow)
def auto_coder_pipeline(user_prompt: str, max_retries: int = 5):
    history_context = ""
    
    for attempt in range(max_retries):
        print(f"--- Attempt {attempt + 1} ---")
        
        # 步骤 1: Coder 生成代码
        coder_prompt = build_coder_prompt(user_prompt, history_context)
        coder_response = call_llm(coder_prompt)
        current_code = extract_code(coder_response)
        
        # 步骤 2: 沙盒运行测试
        execution_result = run_in_sandbox(current_code)
        
        # 步骤 3: 检查是否成功
        if execution_result["success"]:
            print("代码执行成功！")
            return current_code
            
        # 步骤 4: Reviewer 生成反思建议
        print(f"执行失败，报错: {execution_result['error'][:100]}...")
        reviewer_prompt = build_reviewer_prompt(current_code, execution_result['error'])
        reviewer_feedback = call_llm(reviewer_prompt)
        
        # 将反馈加入上下文，进入下一次循环
        history_context = f"前次代码:\n{current_code}\n报错:\n{execution_result['error']}\n修改建议:\n{reviewer_feedback}"
        
    print("达到最大重试次数，任务失败。")
    return None
```

## 6. 面试防坑与亮点包装指北

当你完成上述基础版本后，在简历和面试中，你需要着重强调以下几个“护城河”级别的工程思考：

1. **关于沙盒安全（防删库跑路）：**
    - *面试官可能会问：* “如果模型写了 `os.system('rm -rf /')` 怎么办？”
    - *标准回答：* “在基础架构中，我会覆写内置的 `__builtins__` 并在 AST 层面拦截危险的 `import os/sys`。在最终演进版中，我接入了 Docker API，挂载只读文件系统，并限制了容器的 CPU 和 RAM 使用率。”
2. **关于幻觉死循环：**
    - *面试官可能会问：* “如果 Reviewer 和 Coder 在两个错误之间来回横跳怎么办？”
    - *标准回答：* “我在状态机中加入了温度衰减（Temperature Decay）策略，并保存了前几次尝试的 Hash 值，一旦发现代码生成重复，系统会强制拉高模型的 Temperature 值以探索新的解空间。”

------

**开发建议：** 周末可以直接使用 Python 标准库先把 `subprocess` 的核心逻辑跑通，不用着急上 LangChain 等重型框架。用原生代码把状态流转跑通，会让你对 Agent 的底层逻辑有极深的理解！
import subprocess
import tempfile
import os

def excute_code_sandbox(code:str) -> dict:
    """
    将代码写入沙盒中执行, 并且返回执行结果字典.
    """
    # 清理可能会出现的markdown字符
    clean_code = code.replace("```python", "").replace("```", "").strip()
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py", encoding="utf-8") as f:
        f.write(clean_code)
        temp_file_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_file_path], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout, 
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "TimeoutExpired: Code execution exceeded 10 seconds timeout. Check for infinite loops."
        }
    except Exception as e:
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Exception during code execution: {str(e)}"
        }
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    test_code_success = "print('Hello, World')"
    test_code_error = "print(1/0)"
    text_code_timeout = "while 1: pass"
    
    print(excute_code_sandbox(test_code_success))
    print(excute_code_sandbox(test_code_error))
    print(excute_code_sandbox(text_code_timeout))

import subprocess
import tempfile
import os
import docker 
from docker.errors import DockerException
from requests.exceptions import ReadTimeout

def excute_code_sandbox(code:str) -> dict:
    """
    将代码写入沙盒中执行, 并且返回执行结果字典.
    """
    # 清理可能会出现的markdown字符
    clean_code = code.replace("```python", "").replace("```", "").strip()
    try:
        client = docker.from_env()
    except DockerException:
        return {
            "status": "error",
            "stdout": "",
            "stderr": "SystemError: 无法连接到Docker. 请确保Docker Desktop已启动."
        }
    container = None
    try:
        container = client.containers.run(
            image="python:3.9-slim",
            command=["python", "-c", clean_code],
            detach=True,
            mem_limit="100m",
            network_disabled=True,
        )
        result = container.wait(timeout=10)
        logs = container.logs().decode("utf-8")
        if result["StatusCode"] == 0:
            return {"status": "success", "stdout": logs, "stderr": ""}
        else: 
            return {"status": "failed", "stdout": "", "stderr":logs}
    except ReadTimeout:
        if container:
            container.kill()
        return {"status": "error", "stdout": "", "stderr": "TimeoutError: 代码执行超过10s, 可能存在死循环."}
    except Exception as e:
        return {"status": "error", "stdout": "", "stderr": f"DockerError: {str(e)}"}
    finally:
        if container:
            try:
                container.remove(force=True)
            except:
                pass

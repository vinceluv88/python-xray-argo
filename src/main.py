# main.py
import os
import requests
import stat
import platform
import subprocess
import time

# 全局变量保存最新上报状态
status_message = "⏳ Komari Agent 初始化中..."

def run_agent():
    global status_message

    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "aYKWDxXsqjGjzbowTGq7Jm"
    AGENT_PATH = "/tmp/komari-agent"

    arch = platform.machine().lower()
    if "arm" in arch or "aarch64" in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-amd64"

    try:
        # 下载 agent（如未存在）
        if not os.path.exists(AGENT_PATH):
            r = requests.get(AGENT_URL, stream=True, timeout=30)
            r.raise_for_status()
            with open(AGENT_PATH, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            os.chmod(AGENT_PATH, stat.S_IRWXU)

        # 执行一次上报
        subprocess.run(
            [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        status_message = "✅ Komari Agent 上報成功（持續執行中）"
    except subprocess.CalledProcessError:
        status_message = "❌ 上報失敗：Agent 返回錯誤"
    except Exception as e:
        status_message = f"❌ 上報出錯：{e}"

def main(context):
    global status_message

    # 如果访问路径是 /status，就显示网页
    if context.req.path == "/" or context.req.path == "/status":
        return context.res.html(f"""
            <html><body style='font-family:sans-serif;text-align:center;margin-top:50px'>
                <h2>{status_message}</h2>
                <p>Appwrite Function 正在運行持續上報任務</p>
            </body></html>
        """)

    # 启动持续上报循环
    if context.req.path == "/run":
        status_message = "⏳ Komari Agent 啟動中..."
        run_agent()
        return context.res.text(status_message)

    # 默认返回
    return context.res.text("Appwrite Komari Function Ready ✅")

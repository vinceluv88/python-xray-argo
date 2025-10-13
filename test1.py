# choreo_persistent.py
import os
import requests
import stat
import platform
import subprocess
import threading
from flask import Flask

# -----------------------------
# Flask 部分：显示部署成功页面
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>✅ Choreo 部署成功！Komari Agent 正在持续上报中。</h2>"

def run_flask():
    # Flask 服务常驻
    app.run(host="0.0.0.0", port=9977)

# -----------------------------
# Komari Agent 持续运行部分
# -----------------------------
def start_komari_agent():
    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "0FdRLrSAJKUWrrj67lsHD2"
    AGENT_PATH = "/tmp/komari-agent"

    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.11/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.11/komari-agent-linux-amd64"

    # 下载 Agent（如果不存在）
    if not os.path.exists(AGENT_PATH):
        print(f"Downloading Komari Agent for {arch}...")
        r = requests.get(AGENT_URL, stream=True)
        r.raise_for_status()
        with open(AGENT_PATH, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        os.chmod(AGENT_PATH, stat.S_IRWXU)
        print("Download complete.")

    print(f"Starting Komari Agent at {AGENT_PATH}...")
    # 使用 Popen 启动后台进程，不阻塞 Flask
    subprocess.Popen([AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN])

# -----------------------------
# 程序入口
# -----------------------------
if __name__ == "__main__":
    # 在独立线程启动 Flask
    threading.Thread(target=run_flask, daemon=True).start()
    # 启动 Komari Agent
    start_komari_agent()
    # 主线程保持存活，防止 Python 退出
    threading.Event().wait()

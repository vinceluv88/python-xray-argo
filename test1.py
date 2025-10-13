import os
import requests
import stat
import platform
import subprocess
from flask import Flask, request

app = Flask(__name__)

KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "0FdRLrSAJKUWrrj67lsHD2"
AGENT_PATH = "/tmp/komari-agent"

arch = platform.machine().lower()
if 'arm' in arch or 'aarch64' in arch:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.11/komari-agent-linux-arm64"
else:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.11/komari-agent-linux-amd64"

# 下载 Agent（如果不存在）
def download_agent():
    if not os.path.exists(AGENT_PATH):
        r = requests.get(AGENT_URL, stream=True)
        r.raise_for_status()
        with open(AGENT_PATH, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        os.chmod(AGENT_PATH, stat.S_IRWXU)
        return "✅ Agent 下载完成"
    return "✅ Agent 已存在"

# 执行单次上报
def run_agent_once():
    try:
        output = subprocess.check_output(
            [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
            stderr=subprocess.STDOUT,
            timeout=15
        ).decode()
        return f"✅ 上报成功\n{output}"
    except subprocess.TimeoutExpired:
        return "⚠️ 上报超时"
    except subprocess.CalledProcessError as e:
        return f"❌ 上报失败:\n{e.output.decode()}"
    except Exception as e:
        return f"❌ 执行出错:\n{e}"

@app.route("/")
def home():
    msg = [download_agent()]
    msg.append("⚡ 伪持续上报（Serverless 每次访问触发一次）")
    if request.args.get("trigger") == "1":
        msg.append("手动触发单次上报：")
        msg.append(run_agent_once())
    return "<br>".join(msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9977)

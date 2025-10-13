# choreo_app.py
import os
import requests
import stat
import platform
import threading
from flask import Flask

# === Flask 部分：顯示部署成功頁面 ===
app = Flask(__name__)

@app.route("/")
def home():
    return "<h2>✅ Choreo 部署成功！Komari Agent 已啟動中。</h2>"

def run_flask():
    # 使用非預設端口防止 scale-to-zero（例如 5051）
    app.run(host="0.0.0.0", port=9977)

# === Komari Agent 啟動部分 ===
def start_komari_agent():
    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "0FdRLrSAJKUWrrj67lsHD2"
    AGENT_PATH = "/app/komari-agent"

    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.0.72/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.0.72/komari-agent-linux-amd64"

    if not os.path.exists(AGENT_PATH):
        print(f"Downloading Komari Agent for architecture {arch}...")
        r = requests.get(AGENT_URL, stream=True)
        r.raise_for_status()
        with open(AGENT_PATH, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        print("Download complete.")

    os.chmod(AGENT_PATH, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    print(f"Permission granted, starting Komari Agent at {AGENT_PATH}...")

    # 使用子進程啟動 agent，不阻塞 Flask
    os.system(f"{AGENT_PATH} -e {KOMARI_SERVER} -t {KOMARI_TOKEN}")

if __name__ == "__main__":
    # 在另一個執行緒啟動 Flask
    threading.Thread(target=run_flask, daemon=True).start()
    # 同時執行 Komari Agent
    start_komari_agent()

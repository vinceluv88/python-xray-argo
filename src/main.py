#appwrite.io
import os
import time
import requests
import stat
import platform
import subprocess

KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "eoyW2KW0hd9yvcRqdhFfaA"
AGENT_PATH = "/tmp/komari-agent"

arch = platform.machine().lower()
if "arm" in arch or "aarch64" in arch:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-arm64"
else:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-amd64"

if not os.path.exists(AGENT_PATH):
    print(f"Downloading Komari Agent for {arch}...")
    r = requests.get(AGENT_URL, stream=True)
    with open(AGENT_PATH, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    os.chmod(AGENT_PATH, stat.S_IRWXU)

print("✅ Komari Agent 持續上報中（後台執行）")

# 无限循环持续上报
while True:
    try:
        subprocess.run(
            [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(5)  # 每 30 秒上报一次
    except Exception as e:
        print(f"❌ 上報出錯: {e}")
        time.sleep(60)

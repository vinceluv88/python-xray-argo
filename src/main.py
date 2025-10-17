import threading
import time
import os
import requests
import stat
import platform
import subprocess

def run_agent_loop():
    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "rjhF4asVr2ODACpFCdWzGt"
    AGENT_PATH = "/tmp/komari-agent"

    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-amd64"

    if not os.path.exists(AGENT_PATH):
        r = requests.get(AGENT_URL, stream=True)
        r.raise_for_status()
        with open(AGENT_PATH, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        os.chmod(AGENT_PATH, stat.S_IRWXU)

    while True:
        try:
            subprocess.run([AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN], timeout=30)
        except Exception:
            pass
        time.sleep(60)

def main(context):
    threading.Thread(target=run_agent_loop, daemon=True).start()
    return context.res.text("✅ Komari Agent 持續上報中（後台執行）")

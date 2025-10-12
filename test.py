import os
import requests
import stat
import subprocess
import platform

# 配置
KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "kIxx77rbotRSbHR9B0abxf"
AGENT_PATH = "/tmp"

# 根据架构选择下载链接
arch = platform.machine().lower()
if 'arm' in arch or 'aarch64' in arch:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.0.72/komari-agent-linux-arm64"
else:
    AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.0.72/komari-agent-linux-amd64"

# 下载 Komari Agent
if not os.path.exists(AGENT_PATH):
    print(f"Downloading Komari Agent for architecture {arch}...")
    r = requests.get(AGENT_URL, stream=True)
    with open(AGENT_PATH, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    print("Download complete.")

# 授权可执行
os.chmod(AGENT_PATH, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
print("Permission granted, starting Komari Agent in background...")

# 后台运行 Komari Agent，不阻塞后续脚本
with open(os.devnull, "wb") as devnull:
    subprocess.Popen(
        [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
        stdout=devnull,
        stderr=devnull,
        stdin=devnull,
        close_fds=True
    )

print("Komari Agent is running in the background.")

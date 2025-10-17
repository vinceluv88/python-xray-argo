#!/usr/bin/env python3
import os
import platform
import requests
import stat
import subprocess
import traceback

KOMARI_SERVER = os.environ.get("KOMARI_SERVER", "https://komari.vinceluv.nyc.mn")
KOMARI_TOKEN = os.environ.get("KOMARI_TOKEN", "rjhF4asVr2ODACpFCdWzGt")
AGENT_PATH = "/tmp/komari-agent"
AGENT_VERSION = "1.0.72"

def choose_agent_url(version):
    arch = platform.machine().lower()
    if "arm" in arch or "aarch64" in arch:
        return f"https://github.com/komari-monitor/komari-agent/releases/download/{version}/komari-agent-linux-arm64"
    return f"https://github.com/komari-monitor/komari-agent/releases/download/{version}/komari-agent-linux-amd64"

def download_agent(url, path):
    try:
        r = requests.get(url, stream=True, timeout=20)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        return None
    except Exception:
        return traceback.format_exc()

def run_agent(path):
    try:
        proc = subprocess.Popen(
            [path, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        output = ""
        for line in proc.stdout:
            output += line
        proc.wait(timeout=20)
        return output
    except Exception:
        return traceback.format_exc()

def main():
    print("Content-Type: text/html\n")  # HTTP 响应头

    if not os.path.exists(AGENT_PATH):
        err = download_agent(choose_agent_url(AGENT_VERSION), AGENT_PATH)
        if err:
            print(f"<pre>❌ Download error:\n{err}</pre>")
            return

    output = run_agent(AGENT_PATH)
    print(f"<pre>✅ Komari Agent output:\n{output}</pre>")

if __name__ == "__main__":
    main()

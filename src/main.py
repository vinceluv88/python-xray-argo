import os, time, requests, stat, platform, subprocess

def start_komari_agent(context):
    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "aYKWDxXsqjGjzbowTGq7Jm"
    AGENT_PATH = "/tmp/komari-agent"

    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-amd64"

    if not os.path.exists(AGENT_PATH):
        context.log(f"⬇️ 下載 {arch} 版本 Agent...")
        r = requests.get(AGENT_URL, stream=True, timeout=30)
        r.raise_for_status()
        with open(AGENT_PATH, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        os.chmod(AGENT_PATH, stat.S_IRWXU)
        context.log("✅ Agent 已下載完成")

    context.log("🚀 Komari Agent 持續上報中（後台執行）")

    while True:
        try:
            output = subprocess.check_output(
                [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
                stderr=subprocess.STDOUT,
                timeout=25
            ).decode()
            context.log(f"📡 Agent輸出: {output.strip()}")
        except subprocess.TimeoutExpired:
            context.error("⚠️ 上報逾時")
        except subprocess.CalledProcessError as e:
            context.error(f"❌ 執行錯誤: {e.output.decode()}")
        except Exception as e:
            context.error(f"❌ 其他錯誤: {e}")

        time.sleep(60)

def main(context):
    context.log("🟢 Komari Function 啟動")
    start_komari_agent(context)

#leapcell
import os
import requests
import stat
import platform
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
    KOMARI_TOKEN = "aYKWDxXsqjGjzbowTGq7Jm"
    AGENT_PATH = "/tmp/komari-agent"

    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-arm64"
    else:
        AGENT_URL = "https://github.com/komari-monitor/komari-agent/releases/download/1.1.12/komari-agent-linux-amd64"

    try:
        # 只在不存在时下载，节省启动时间
        if not os.path.exists(AGENT_PATH):
            r = requests.get(AGENT_URL, stream=True, timeout=20)
            r.raise_for_status()
            with open(AGENT_PATH, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            os.chmod(AGENT_PATH, stat.S_IRWXU)
    except Exception as e:
        return f"<h3>❌ 無法下載 Komari Agent：</h3><pre>{e}</pre>"

    # 執行 agent，單次上報
    try:
        output = subprocess.check_output(
            [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN],
            stderr=subprocess.STDOUT,
            timeout=20
        ).decode()
        result = f"<h2>✅ Komari 單次上報成功</h2><pre>{output}</pre>"
    except subprocess.TimeoutExpired:
        result = "<h3>⚠️ 上報逾時（Serverless 最長 9 分鐘限制內）</h3>"
    except subprocess.CalledProcessError as e:
        result = f"<h3>❌ 上報失敗：</h3><pre>{e.output.decode()}</pre>"
    except Exception as e:
        result = f"<h3>❌ 執行出錯：</h3><pre>{e}</pre>"

    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9977)

import subprocess
import sys

# ------------------------------
# 安装依赖函数
# ------------------------------
def install(package):
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found, installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 安装 psutil 和 websockets
install("psutil")
install("websockets")

# ------------------------------
# 导入已安装依赖
# ------------------------------
import os
import asyncio
import json
import platform
import psutil
import websockets

# ------------------------------
# 配置环境变量
# ------------------------------
KOMARI_TOKEN = os.environ.get("KOMARI_TOKEN")
KOMARI_SERVER = os.environ.get("KOMARI_SERVER")

if not KOMARI_TOKEN or not KOMARI_SERVER:
    raise ValueError("KOMARI_SERVER and KOMARI_TOKEN must be set in environment variables.")

WS_URL = f"{KOMARI_SERVER}/api/clients/report?token={KOMARI_TOKEN}"

# ------------------------------
# 收集监控数据函数
# ------------------------------
def collect_metrics():
    cpu_percent = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    metrics = {
        "cpu": cpu_percent,
        "memory": round(mem.used / 1024 / 1024, 2),
        "disk": round(disk.used / 1024 / 1024, 2),
        "arch": platform.machine()
    }
    return metrics

# ------------------------------
# WebSocket 上报协程
# ------------------------------
async def send_metrics():
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                print("Connected to Komari WebSocket server.")
                while True:
                    data = collect_metrics()
                    await ws.send(json.dumps(data))
                    print(f"Sent metrics: {data}")
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"WebSocket connection error: {e}, retrying in 5s...")
            await asyncio.sleep(5)

# ------------------------------
# 主程序
# ------------------------------
if __name__ == "__main__":
    print("Python Komari Agent started...Main app continues running...")
    try:
        asyncio.run(send_metrics())
    except KeyboardInterrupt:
        print("Komari Agent stopped manually.")

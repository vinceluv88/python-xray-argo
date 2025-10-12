import os
import threading
import time
import requests

# ========================
# 配置
# ========================
KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "kIxx77rbotRSbHR9B0abxf"

# ========================
# 模拟 Komari Agent 功能
# ========================
def komari_agent_loop():
    """
    模拟 Komari Agent 的后台运行
    这里可以定时上报数据到 KOMARI_SERVER
    """
    print("Python Komari Agent started...")
    while True:
        try:
            # 示例：发送心跳
            resp = requests.post(
                f"{KOMARI_SERVER}/heartbeat",
                json={"token": KOMARI_TOKEN, "status": "alive"}
            )
            if resp.status_code == 200:
                print("Heartbeat sent successfully.")
            else:
                print(f"Heartbeat failed: {resp.status_code}")
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
        
        time.sleep(10)  # 每 10 秒发送一次

# ========================
# 启动后台线程
# ========================
agent_thread = threading.Thread(target=komari_agent_loop, daemon=True)
agent_thread.start()

# ========================
# 主线程继续执行其他逻辑
# ========================
print("Main app continues running...")

# 示例：保持主线程不退出
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Exiting app.")

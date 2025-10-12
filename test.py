#!/usr/bin/env python3
import os
import platform
import requests
import time
import socket
import uuid

# =============================
# 配置：从环境变量读取
# =============================
KOMARI_SERVER = os.environ.get("KOMARI_SERVER")  # e.g., https://komari.vinceluv.nyc.mn
KOMARI_TOKEN = os.environ.get("KOMARI_TOKEN")    # Agent token

if not KOMARI_SERVER or not KOMARI_TOKEN:
    raise ValueError("KOMARI_SERVER and KOMARI_TOKEN must be set in environment variables.")

# =============================
# Agent 信息
# =============================
HOSTNAME = socket.gethostname()
ARCH = platform.machine().lower()
VERSION = "python-agent-1.0"
AGENT_ID = str(uuid.uuid4())  # 模拟官方 Agent 的唯一 ID

# =============================
# Agent 注册函数
# =============================
def register_agent():
    url = f"{KOMARI_SERVER}/agent/register"
    data = {
        "token": KOMARI_TOKEN,
        "agent_id": AGENT_ID,
        "hostname": HOSTNAME,
        "architecture": ARCH,
        "version": VERSION
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"[Register] Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print(f"[Register] Error: {e}")

# =============================
# 发送 Heartbeat
# =============================
def send_heartbeat():
    url = f"{KOMARI_SERVER}/agent/heartbeat"
    data = {
        "token": KOMARI_TOKEN,
        "agent_id": AGENT_ID,
        "hostname": HOSTNAME,
        "architecture": ARCH,
        "version": VERSION,
        "status": "alive"
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"[Heartbeat] Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        print(f"[Heartbeat] Error: {e}")

# =============================
# 主循环
# =============================
def main():
    print("Python Komari Agent started...")
    # 注册 Agent（官方 Agent 也会先注册一次）
    register_agent()
    print("Agent registration complete. Starting heartbeat loop...")

    while True:
        send_heartbeat()
        time.sleep(10)  # 每 10 秒发送一次心跳

if __name__ == "__main__":
    main()

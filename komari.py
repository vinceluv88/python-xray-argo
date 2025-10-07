import os

# -----------------------------
# 配置
# -----------------------------
KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "BarHhvaDyGX9Y0fW"
AGENT_PATH = "./komari-agent"  # 已经存在的路径

# -----------------------------
# 替换 Python 进程，前台运行 Komari Agent
# -----------------------------
os.execv(AGENT_PATH, [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN])

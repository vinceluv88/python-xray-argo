import os
import stat

# -----------------------------
# 配置
# -----------------------------
KOMARI_SERVER = "https://komari.vinceluv.nyc.mn"
KOMARI_TOKEN = "BarHhvaDyGX9Y0fW"
AGENT_PATH = "./komari-agent"  # 已经存在的路径

# -----------------------------
# 确保二进制有执行权限
# -----------------------------
st = os.stat(AGENT_PATH)
os.chmod(AGENT_PATH, st.st_mode | stat.S_IEXEC)  # 添加可执行权限

# -----------------------------
# 替换 Python 进程，前台运行 Komari Agent
# -----------------------------
os.execv(AGENT_PATH, [AGENT_PATH, "-e", KOMARI_SERVER, "-t", KOMARI_TOKEN])

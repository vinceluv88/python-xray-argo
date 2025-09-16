#!/bin/bash
# 非 root 用户一键运行 python-xray-argo 和 Komari Agent，后台静默，Komari 配置隐秘

# =========================
# 配置变量
# =========================
WORKDIR="$HOME/python-xray-argo"
KOMARI_DIR="$HOME/komari"

# KOMARI_SERVER 和 KOMARI_TOKEN 从环境变量获取
: "${KOMARI_SERVER:?请先设置环境变量 KOMARI_SERVER}"
: "${KOMARI_TOKEN:?请先设置环境变量 KOMARI_TOKEN}"

# =========================
# 12. Komari Agent 部分
# =========================
mkdir -p "$KOMARI_DIR"
cd "$KOMARI_DIR" || exit

# 下载 Komari Agent 二进制（静默）
curl -s -LO https://github.com/komari-monitor/komari-agent/releases/latest/download/komari-agent-linux-amd64

# 赋予执行权限
chmod +x komari-agent-linux-amd64
mv komari-agent-linux-amd64 komari-agent

# 后台启动 Komari Agent（静默）
nohup ./komari-agent -e "$KOMARI_SERVER" -t "$KOMARI_TOKEN" > /dev/null 2>&1 &


# =========================
# 2. python-xray-argo 部分
# =========================
mkdir -p "$WORKDIR"
cd "$WORKDIR" || exit

# 下载 app.py（静默）
curl -s -O https://raw.githubusercontent.com/vinceluv88/python-xray-argo/refs/heads/main/app.py

# 安装依赖 Flask 和 requests（静默）
pip3 install --user Flask requests -q > /dev/null 2>&1


sleep 10
# 后台运行 app.py（静默）
nohup python3 app.py > /dev/null 2>&1 &

sleep 10

# 打印 sub.txt
if [ -f ./.cache/sub.txt ]; then
    cat ./.cache/sub.txt
fi


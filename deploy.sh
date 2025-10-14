#!/bin/bash
# 停掉旧的 Streamlit
pkill -f streamlit || true

# 启动新的 Streamlit
nohup streamlit run test.py --server.enableCORS false --server.enableXsrfProtection false &

echo "✅ Streamlit 部署完成"

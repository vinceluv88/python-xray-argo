import subprocess
import os
import re
import json
import time
import base64
import shutil
import asyncio
import requests
import platform
import threading
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---- 在脚本最开始运行 komari ----
try:
    os.chdir("/home/container")  # 切换到指定目录
    subprocess.Popen(
        ["./komari", "-e", "https://komari.vinceluv.nyc.mn", "-t", "igCUqeSh6o5yJR69"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Komari started successfully")
except Exception as e:
    print(f"Failed to start Komari: {e}")

# ======================= 原脚本内容 =======================
# Environment variables
UPLOAD_URL = os.environ.get('UPLOAD_URL', '')          
PROJECT_URL = os.environ.get('PROJECT_URL', '')        
AUTO_ACCESS = os.environ.get('AUTO_ACCESS', 'false').lower() == 'true'  
FILE_PATH = os.environ.get('FILE_PATH', './.cache')    
SUB_PATH = os.environ.get('SUB_PATH', 'sub')           
UUID = os.environ.get('UUID', 'f3ba3187-d633-44c1-8f6b-267500945bf1')  
NEZHA_SERVER = os.environ.get('NEZHA_SERVER', '')      
NEZHA_PORT = os.environ.get('NEZHA_PORT', '')          
NEZHA_KEY = os.environ.get('NEZHA_KEY', '')            
ARGO_DOMAIN = os.environ.get('ARGO_DOMAIN', '')        
ARGO_AUTH = os.environ.get('ARGO_AUTH', '')            
ARGO_PORT = int(os.environ.get('ARGO_PORT', '8001'))   
CFIP = os.environ.get('CFIP', 'www.visa.com.sg')       
CFPORT = int(os.environ.get('CFPORT', '443'))          
NAME = os.environ.get('NAME', 'Vls')                   
CHAT_ID = os.environ.get('CHAT_ID', '')                
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')            
PORT = int(os.environ.get('SERVER_PORT') or os.environ.get('PORT') or 3000) 

# Create running folder
def create_directory():
    print('\033c', end='')
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
        print(f"{FILE_PATH} is created")
    else:
        print(f"{FILE_PATH} already exists")

# Global variables
npm_path = os.path.join(FILE_PATH, 'npm')
php_path = os.path.join(FILE_PATH, 'php')
web_path = os.path.join(FILE_PATH, 'web')
bot_path = os.path.join(FILE_PATH, 'bot')
sub_path = os.path.join(FILE_PATH, 'sub.txt')
list_path = os.path.join(FILE_PATH, 'list.txt')
boot_log_path = os.path.join(FILE_PATH, 'boot.log')
config_path = os.path.join(FILE_PATH, 'config.json')

# Delete nodes
def delete_nodes():
    try:
        if not UPLOAD_URL:
            return
        if not os.path.exists(sub_path):
            return
        with open(sub_path, 'r') as file:
            file_content = file.read()
        decoded = base64.b64decode(file_content).decode('utf-8')
        nodes = [line for line in decoded.split('\n') if any(protocol in line for protocol in ['vless://', 'vmess://', 'trojan://', 'hysteria2://', 'tuic://'])]
        if nodes:
            try:
                requests.post(f"{UPLOAD_URL}/api/delete-nodes", data=json.dumps({"nodes": nodes}), headers={"Content-Type": "application/json"})
            except:
                pass
    except Exception as e:
        print(f"Error in delete_nodes: {e}")

# Clean up old files
def cleanup_old_files():
    paths_to_delete = ['web', 'bot', 'npm', 'php', 'boot.log', 'list.txt']
    for file in paths_to_delete:
        file_path = os.path.join(FILE_PATH, file)
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Hello World')
        elif self.path == f'/{SUB_PATH}':
            try:
                with open(sub_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

# Determine system architecture
def get_system_architecture():
    architecture = platform.machine().lower()
    if 'arm' in architecture or 'aarch64' in architecture:
        return 'arm'
    else:
        return 'amd'

# Download file based on architecture
def download_file(file_name, file_url):
    file_path = os.path.join(FILE_PATH, file_name)
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download {file_name} successfully")
        return True
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Download {file_name} failed: {e}")
        return False

# Get files for architecture
def get_files_for_architecture(architecture):
    if architecture == 'arm':
        base_files = [
            {"fileName": "web", "fileUrl": "https://arm64.ssss.nyc.mn/web"},
            {"fileName": "bot", "fileUrl": "https://arm64.ssss.nyc.mn/2go"}
        ]
    else:
        base_files = [
            {"fileName": "web", "fileUrl": "https://amd64.ssss.nyc.mn/web"},
            {"fileName": "bot", "fileUrl": "https://amd64.ssss.nyc.mn/2go"}
        ]
    if NEZHA_SERVER and NEZHA_KEY:
        if NEZHA_PORT:
            npm_url = "https://arm64.ssss.nyc.mn/agent" if architecture == 'arm' else "https://amd64.ssss.nyc.mn/agent"
            base_files.insert(0, {"fileName": "npm", "fileUrl": npm_url})
        else:
            php_url = "https://arm64.ssss.nyc.mn/v1" if architecture == 'arm' else "https://amd64.ssss.nyc.mn/v1"
            base_files.insert(0, {"fileName": "php", "fileUrl": php_url})
    return base_files

# Authorize files with execute permission
def authorize_files(file_paths):
    for relative_file_path in file_paths:
        absolute_file_path = os.path.join(FILE_PATH, relative_file_path)
        if os.path.exists(absolute_file_path):
            try:
                os.chmod(absolute_file_path, 0o775)
                print(f"Empowerment success for {absolute_file_path}: 775")
            except Exception as e:
                print(f"Empowerment failed for {absolute_file_path}: {e}")

# Configure Argo tunnel
def argo_type():
    if not ARGO_AUTH or not ARGO_DOMAIN:
        print("ARGO_DOMAIN or ARGO_AUTH variable is empty, use quick tunnels")
        return
    if "TunnelSecret" in ARGO_AUTH:
        with open(os.path.join(FILE_PATH, 'tunnel.json'), 'w') as f:
            f.write(ARGO_AUTH)
        tunnel_id = ARGO_AUTH.split('"')[11]
        tunnel_yml = f"""
tunnel: {tunnel_id}
credentials-file: {os.path.join(FILE_PATH, 'tunnel.json')}
protocol: http2

ingress:
  - hostname: {ARGO_DOMAIN}
    service: http://localhost:{ARGO_PORT}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""
        with open(os.path.join(FILE_PATH, 'tunnel.yml'), 'w') as f:
            f.write(tunnel_yml)
    else:
        print("Use token connect to tunnel,please set the {ARGO_PORT} in cloudflare")

# Execute shell command and return output
def exec_cmd(command):
    try:
        process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return stdout + stderr
    except Exception as e:
        print(f"Error executing command: {e}")
        return str(e)

# ----------------- 核心异步逻辑 -----------------
async def download_files_and_run():
    architecture = get_system_architecture()
    files_to_download = get_files_for_architecture(architecture)
    
    download_success = True
    for file_info in files_to_download:
        if not download_file(file_info["fileName"], file_info["fileUrl"]):
            download_success = False
    if not download_success:
        print("Error downloading files")
        return
    
    files_to_authorize = ['npm', 'web', 'bot'] if NEZHA_PORT else ['php', 'web', 'bot']
    authorize_files(files_to_authorize)
    
    port = NEZHA_SERVER.split(":")[-1] if ":" in NEZHA_SERVER else ""
    nezha_tls = "true" if port in ["443", "8443", "2096", "2087", "2083", "2053"] else "false"
    
    if NEZHA_SERVER and NEZHA_KEY:
        if not NEZHA_PORT:
            config_yaml = f"""
client_secret: {NEZHA_KEY}
debug: false
disable_auto_update: true
disable_command_execute: false
disable_force_update: true
disable_nat: false
disable_send_query: false
gpu: false
insecure_tls: false
ip_report_period: 1800
report_delay: 4
server: {NEZHA_SERVER}
skip_connection_count: false
skip_procs_count: false
temperature: false
tls: {nezha_tls}
use_gitee_to_upgrade: false
use_ipv6_country_code: false
uuid: {UUID}"""
            with open(os.path.join(FILE_PATH, 'config.yaml'), 'w') as f:
                f.write(config_yaml)
    
    config ={"log":{"access":"/dev/null","error":"/dev/null","loglevel":"none",},"inbounds":[{"port":ARGO_PORT ,"protocol":"vless","settings":{"clients":[{"id":UUID ,"flow":"xtls-rprx-vision",},],"decryption":"none","fallbacks":[{"dest":3001 },{"path":"/vless-argo","dest":3002 },{"path":"/vmess-argo","dest":3003 },{"path":"/trojan-argo","dest":3004 },],},"streamSettings":{"network":"tcp",},},{"port":3001 ,"listen":"127.0.0.1","protocol":"vless","settings":{"clients":[{"id":UUID },],"decryption":"none"},"streamSettings":{"network":"ws","security":"none"}},{"port":3002 ,"listen":"127.0.0.1","protocol":"vless","settings":{"clients":[{"id":UUID ,"level":0 }],"decryption":"none"},"streamSettings":{"network":"ws","security":"none","wsSettings":{"path":"/vless-argo"}},"sniffing":{"enabled":True ,"destOverride":["http","tls","quic"],"metadataOnly":False }},{"port":3003 ,"listen":"127.0.0.1","protocol":"vmess","settings":{"clients":[{"id":UUID ,"alterId":0 }]},"streamSettings":{"network":"ws","wsSettings":{"path":"/vmess-argo"}},"sniffing":{"enabled":True ,"destOverride":["http","tls","quic"],"metadataOnly":False }},{"port":3004 ,"listen":"127.0.0.1","protocol":"trojan","settings":{"clients":[{"password":UUID },]},"streamSettings":{"network":"ws","security":"none","wsSettings":{"path":"/trojan-argo"}},"sniffing":{"enabled":True ,"destOverride":["http","tls","quic"],"metadataOnly":False }},],"outbounds":[{"protocol":"freedom","tag": "direct" },{"protocol":"blackhole","tag":"block"}]}
    with open(os.path.join(FILE_PATH, 'config.json'), 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=2)
    
    if NEZHA_SERVER and NEZHA_PORT and NEZHA_KEY:
        tls_ports = ['443', '8443', '2096', '2087', '2083', '2053']
        nezha_tls = '--tls' if NEZHA_PORT in tls_ports else ''
        command = f"nohup {os.path.join(FILE_PATH, 'npm')} -s {NEZHA_SERVER}:{NEZHA_PORT} -p {NEZHA_KEY} {nezha_tls} >/dev/null 2>&1 &"
        exec_cmd(command)
    elif NEZHA_SERVER and NEZHA_KEY:
        command = f"nohup {FILE_PATH}/php -c \"{FILE_PATH}/config.yaml\" >/dev/null 2>&1 &"
        exec_cmd(command)
    
    command = f"nohup {os.path.join(FILE_PATH, 'web')} -c {os.path.join(FILE_PATH, 'config.json')} >/dev/null 2>&1 &"
    exec_cmd(command)
    
    if os.path.exists(os.path.join(FILE_PATH, 'bot')):
        if re.match(r'^[A-Z0-9a-z=]{120,250}$', ARGO_AUTH):
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 run --token {ARGO_AUTH}"
        elif "TunnelSecret" in ARGO_AUTH:
            args = f"tunnel --edge-ip-version auto --config {os.path.join(FILE_PATH, 'tunnel.yml')} run"
        else:
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {os.path.join(FILE_PATH, 'boot.log')} --loglevel info --url http://localhost:{ARGO_PORT}"
        exec_cmd(f"nohup {os.path.join(FILE_PATH, 'bot')} {args} >/dev/null 2>&1 &")
    
    time.sleep(5)
    await extract_domains()

async def extract_domains():
    argo_domain = None
    if ARGO_AUTH and ARGO_DOMAIN:
        argo_domain = ARGO_DOMAIN
        await generate_links(argo_domain)
    else:
        try:
            with open(boot_log_path, 'r') as f:
                lines = f.read().split('\n')
            argo_domains = [re.search(r'https?://([^ ]*trycloudflare\.com)/?', line).group(1) for line in lines if re.search(r'https?://([^ ]*trycloudflare\.com)/?', line)]
            if argo_domains:
                argo_domain = argo_domains[0]
                await generate_links(argo_domain)
            else:
                if os.path.exists(boot_log_path):
                    os.remove(boot_log_path)
                exec_cmd('pkill -f "[b]ot" > /dev/null 2>&1')
                time.sleep(1)
                args = f'tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {FILE_PATH}/boot.log --loglevel info --url http://localhost:{ARGO_PORT}'
                exec_cmd(f'nohup {os.path.join(FILE_PATH, "bot")} {args} >/dev/null 2>&1 &')
                time.sleep(6)
                await extract_domains()
        except Exception as e:
            print(f'Error reading boot.log: {e}')

async def generate_links(argo_domain):
    meta_info = subprocess.run(['curl', '-s', 'https://speed.cloudflare.com/meta'], capture_output=True, text=True).stdout.split('"')
    ISP = f"{meta_info[25]}-{meta_info[17]}".replace(' ', '_').strip()
    VMESS = {"v": "2", "ps": f"{NAME}-{ISP}", "add": CFIP, "port": CFPORT, "id": UUID, "aid": "0", "scy": "none", "net": "ws", "type": "none", "host": argo_domain, "path": "/vmess-argo?ed=2560", "tls": "tls", "sni": argo_domain, "alpn": "", "fp": "chrome"}
    list_txt = f"""
vless://{UUID}@{CFIP}:{CFPORT}?encryption=none&security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2560#{NAME}-{ISP}
vmess://{ base64.b64encode(json.dumps(VMESS).encode('utf-8')).decode('utf-8')}
trojan://{UUID}@{CFIP}:{CFPORT}?security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2560#{NAME}-{ISP}
"""
    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(list_txt)
    sub_txt = base64.b64encode(list_txt.encode('utf-8')).decode('utf-8')
    with open(sub_path, 'w', encoding='utf-8') as f:
        f.write(sub_txt)
    send_telegram()
    upload_nodes()

# ----------------- Telegram & Upload -----------------
def send_telegram():
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        with open(sub_path, 'r') as f:
            message = f.read()
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        escaped_name = re.sub(r'([_*\[\]()~>#+=|{}.!\-])', r'\\\1', NAME)
        params = {"chat_id": CHAT_ID, "text": f"**{escaped_name}节点推送通知**\n{message}", "parse_mode": "MarkdownV2"}
        requests.post(url, params=params)
    except Exception as e:
        print(f'Failed to send Telegram message: {e}')

def upload_nodes():
    if UPLOAD_URL and PROJECT_URL:
        subscription_url = f"{PROJECT_URL}/{SUB_PATH}"
        json_data = {"subscription": [subscription_url]}
        try:
            response = requests.post(f"{UPLOAD_URL}/api/add-subscriptions", json=json_data, headers={"Content-Type": "application/json"})
        except:
            pass
    elif UPLOAD_URL and os.path.exists(list_path):
        with open(list_path, 'r') as f:
            content = f.read()
        nodes = [line for line in content.split('\n') if any(protocol in line for protocol in ['vless://', 'vmess://', 'trojan://', 'hysteria2://', 'tuic://'])]
        if nodes:
            try:
                requests.post(f"{UPLOAD_URL}/api/add-nodes", data=json.dumps({"nodes": nodes}), headers={"Content-Type": "application/json"})
            except:
                pass

# ----------------- 访问保持 -----------------
def add_visit_task():
    if not AUTO_ACCESS or not PROJECT_URL:
        return
    try:
        requests.post('https://keep.gvrander.eu.org/add-url', json={"url": PROJECT_URL}, headers={"Content-Type": "application/json"})
    except:
        pass

# ----------------- 清理 -----------------
def clean_files():
    def _cleanup():
        time.sleep(90)
        files_to_delete = [boot_log_path, config_path, list_path, web_path, bot_path, php_path, npm_path]
        for file in files_to_delete:
            try:
                if os.path.exists(file):
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    else:
                        os.remove(file)
            except:
                pass
        print('\033c', end='')
        print('App is running')
        print('Thank you for using this script, enjoy!')
    threading.Thread(target=_cleanup, daemon=True).start()

# ----------------- Server -----------------
async def start_server():
    delete_nodes()
    cleanup_old_files()
    create_directory()
    argo_type()
    await download_files_and_run()
    add_visit_task()
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    clean_files()

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server is running on port {PORT}")
    server.serve_forever()

def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    run_async()

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
import stat

# ---- 启动 komari ----
try:
    os.chdir("/home/container")
    komari_path = "./komari"
    if os.path.exists(komari_path):
        st = os.stat(komari_path)
        os.chmod(komari_path, st.st_mode | stat.S_IEXEC)
    subprocess.Popen(
        [komari_path, "-e", "https://komari.vinceluv.nyc.mn", "-t", "rrFUDrICC-ujcLLZ"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Komari started successfully")
except Exception as e:
    print(f"Failed to start Komari: {e}")

# ======================= 环境变量 =======================
UPLOAD_URL = os.environ.get('UPLOAD_URL', '')          
PROJECT_URL = os.environ.get('PROJECT_URL', '')        
AUTO_ACCESS = os.environ.get('AUTO_ACCESS', 'false').lower() == 'true'  
FILE_PATH = os.environ.get('FILE_PATH', './.cache')    
SUB_PATH = os.environ.get('SUB_PATH', 'sub')           
UUID = os.environ.get('UUID', '5c3205c2-cf54-4a0a-ba04-19277f725236')  
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

# ----------------- 全局变量 -----------------
npm_path = os.path.join(FILE_PATH, 'npm')
php_path = os.path.join(FILE_PATH, 'php')
web_path = os.path.join(FILE_PATH, 'web')
bot_path = os.path.join(FILE_PATH, 'bot')
sub_path = os.path.join(FILE_PATH, 'sub.txt')
list_path = os.path.join(FILE_PATH, 'list.txt')
boot_log_path = os.path.join(FILE_PATH, 'boot.log')
config_path = os.path.join(FILE_PATH, 'config.json')

# ----------------- 工具函数 -----------------
def create_directory():
    print('\033c', end='')
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
        print(f"{FILE_PATH} created")
    else:
        print(f"{FILE_PATH} already exists")

def delete_nodes():
    try:
        if not UPLOAD_URL or not os.path.exists(sub_path):
            return
        with open(sub_path, 'r') as f:
            content = f.read()
        decoded = base64.b64decode(content).decode('utf-8')
        nodes = [line for line in decoded.split('\n') if any(p in line for p in ['vless://','vmess://','trojan://','hysteria2://','tuic://'])]
        if nodes:
            try:
                requests.post(f"{UPLOAD_URL}/api/delete-nodes", data=json.dumps({"nodes": nodes}), headers={"Content-Type":"application/json"})
            except:
                pass
    except Exception as e:
        print(f"delete_nodes error: {e}")

def cleanup_old_files():
    paths = ['web','bot','npm','php','boot.log','list.txt']
    for f in paths:
        p = os.path.join(FILE_PATH, f)
        try:
            if os.path.exists(p):
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
        except Exception as e:
            print(f"cleanup {p} error: {e}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(b'Hello World')
        elif self.path == f'/{SUB_PATH}':
            try:
                with open(sub_path,'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type','text/plain')
                    self.end_headers()
                    self.wfile.write(f.read())
            except:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def get_system_architecture():
    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch64' in arch:
        return 'arm'
    return 'amd'

def download_file(file_name, file_url):
    path = os.path.join(FILE_PATH, file_name)
    try:
        r = requests.get(file_url, stream=True)
        r.raise_for_status()
        with open(path,'wb') as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"{file_name} downloaded")
        return True
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        print(f"{file_name} download failed: {e}")
        return False

def get_files_for_architecture(arch):
    if arch=='arm':
        files = [{"fileName":"web","fileUrl":"https://arm64.ssss.nyc.mn/web"},
                 {"fileName":"bot","fileUrl":"https://arm64.ssss.nyc.mn/2go"}]
    else:
        files = [{"fileName":"web","fileUrl":"https://amd64.ssss.nyc.mn/web"},
                 {"fileName":"bot","fileUrl":"https://amd64.ssss.nyc.mn/2go"}]
    if NEZHA_SERVER and NEZHA_KEY:
        if NEZHA_PORT:
            npm_url = "https://arm64.ssss.nyc.mn/agent" if arch=='arm' else "https://amd64.ssss.nyc.mn/agent"
            files.insert(0,{"fileName":"npm","fileUrl":npm_url})
        else:
            php_url = "https://arm64.ssss.nyc.mn/v1" if arch=='arm' else "https://amd64.ssss.nyc.mn/v1"
            files.insert(0,{"fileName":"php","fileUrl":php_url})
    return files

def authorize_files(file_list):
    for f in file_list:
        path = os.path.join(FILE_PATH,f)
        if os.path.exists(path):
            try:
                os.chmod(path,0o775)
                print(f"Authorized {f}")
            except Exception as e:
                print(f"Authorize {f} failed: {e}")

def argo_type():
    if not ARGO_AUTH or not ARGO_DOMAIN:
        print("ARGO_DOMAIN or ARGO_AUTH empty, using quick tunnel")
        return
    if "TunnelSecret" in ARGO_AUTH:
        with open(os.path.join(FILE_PATH,'tunnel.json'),'w') as f:
            f.write(ARGO_AUTH)
        tunnel_id = ARGO_AUTH.split('"')[11]
        tunnel_yml = f"""
tunnel: {tunnel_id}
credentials-file: {os.path.join(FILE_PATH,'tunnel.json')}
protocol: http2

ingress:
  - hostname: {ARGO_DOMAIN}
    service: http://localhost:{ARGO_PORT}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""
        with open(os.path.join(FILE_PATH,'tunnel.yml'),'w') as f:
            f.write(tunnel_yml)
    else:
        print("Using token connect tunnel")

def exec_cmd(command):
    try:
        proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        out,err = proc.communicate()
        return out+err
    except Exception as e:
        print(f"exec_cmd error: {e}")
        return str(e)

# ----------------- 核心异步逻辑 -----------------
async def download_files_and_run():
    arch = get_system_architecture()
    files_to_download = get_files_for_architecture(arch)
    for f in files_to_download:
        if not download_file(f["fileName"], f["fileUrl"]):
            print("Error downloading files")
            return
    files_to_authorize = ['npm','web','bot'] if NEZHA_PORT else ['php','web','bot']
    authorize_files(files_to_authorize)

    # NEZHA 客户端启动
    if NEZHA_SERVER and NEZHA_KEY:
        if NEZHA_PORT:
            tls_ports = ['443','8443','2096','2087','2083','2053']
            tls_flag = '--tls' if NEZHA_PORT in tls_ports else ''
            cmd = f"nohup {os.path.join(FILE_PATH,'npm')} -s {NEZHA_SERVER}:{NEZHA_PORT} -p {NEZHA_KEY} {tls_flag} >/dev/null 2>&1 &"
            exec_cmd(cmd)
        else:
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
tls: false
use_gitee_to_upgrade: false
use_ipv6_country_code: false
uuid: {UUID}"""
            with open(os.path.join(FILE_PATH,'config.yaml'),'w') as f:
                f.write(config_yaml)
            cmd = f"nohup {os.path.join(FILE_PATH,'php')} -c \"{os.path.join(FILE_PATH,'config.yaml')}\" >/dev/null 2>&1 &"
            exec_cmd(cmd)

    # Web 服务启动
    cmd = f"nohup {os.path.join(FILE_PATH,'web')} -c {os.path.join(FILE_PATH,'config.json')} >/dev/null 2>&1 &"
    exec_cmd(cmd)

    # Bot + Argo Tunnel
    if os.path.exists(os.path.join(FILE_PATH,'bot')):
        if re.match(r'^[A-Z0-9a-z=]{120,250}$', ARGO_AUTH):
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 run --token {ARGO_AUTH}"
        elif "TunnelSecret" in ARGO_AUTH:
            args = f"tunnel --edge-ip-version auto --config {os.path.join(FILE_PATH,'tunnel.yml')} run"
        else:
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {boot_log_path} --loglevel info --url http://localhost:{ARGO_PORT}"
        exec_cmd(f"nohup {os.path.join(FILE_PATH,'bot')} {args} >/dev/null 2>&1 &")

    await asyncio.sleep(5)

# ----------------- Server -----------------
async def start_server():
    delete_nodes()
    cleanup_old_files()
    create_directory()
    argo_type()
    await download_files_and_run()
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()

def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    run_async()

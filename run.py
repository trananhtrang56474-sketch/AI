import subprocess
import os
import sys
import time
import platform
import urllib.request
import urllib.error
import webbrowser  # ✨ 新增：用于自动打开浏览器

# 获取当前脚本所在的根目录 (即 AI-MAIN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# 后端地址配置
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "8080"
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
# 前端地址配置
FRONTEND_URL = "http://localhost:5173"

def start_backend():
    print(f"🔧 正在启动 Flask 后端 (端口 {BACKEND_PORT})...")
    
    if platform.system() == "Windows":
        venv_python = os.path.join(BASE_DIR, '.venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(BASE_DIR, '.venv', 'bin', 'python')
    
    if not os.path.exists(venv_python):
        print(f"❌ 错误: 找不到虚拟环境解释器: {venv_python}")
        print("请确保在项目根目录下创建了 .venv 虚拟环境")
        sys.exit(1)
    
    # 启动后端进程
    return subprocess.Popen([venv_python, 'app.py'], cwd=BACKEND_DIR)

def start_frontend():
    print("🚀 正在启动 Vue 前端 (后台并行编译中)...")
    npm_cmd = 'npm.cmd' if platform.system() == "Windows" else 'npm'
    # ✨ 优化：去掉了 '--open' 参数，防止浏览器过早打开报错
    return subprocess.Popen([npm_cmd, 'run', 'dev'], cwd=FRONTEND_DIR, shell=True)

def wait_for_backend(timeout=60):
    print("⏳ 等待后端服务就绪...", end="", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(BACKEND_URL, timeout=1) as response:
                print("\n✅ 后端服务已启动！")
                return True
        except (urllib.error.URLError, ConnectionResetError):
            # ✨ 优化：把 sleep(1) 改成 0.2 秒，轮询更快，一旦启动瞬间捕获
            time.sleep(0.2)
            print(".", end="", flush=True)
        except Exception:
            print("\n✅ 后端服务已响应！")
            return True
            
    print("\n❌ 后端启动超时，请检查后端是否有报错信息。")
    return False

if __name__ == '__main__':
    backend_process = None
    frontend_process = None

    try:
        # 1. ✨ 并发启动：同时开启后端和前端！
        backend_process = start_backend()
        frontend_process = start_frontend()
        
        # 2. 检查后端是否就绪
        if wait_for_backend(timeout=60): 
            
            print("\n=== ✨ 全栈项目启动成功 ===")
            print(f"🌍 前端地址: {FRONTEND_URL}")
            print(f"🔌 后端地址: {BACKEND_URL}")
            print("🛑 按下 Ctrl + C 可以停止所有服务\n")

            # 3. ✨ 优化：等后端好了，由 Python 主动帮你打开浏览器
            # 为了确保 Vite 也编译好了，稍微等 1 秒
            time.sleep(1) 
            print("🌐 正在自动打开浏览器...")
            webbrowser.open(FRONTEND_URL)

            # 4. 保持运行
            backend_process.wait()
            frontend_process.wait()
        else:
            print("程序即将退出...")
            if backend_process: backend_process.terminate()
            if frontend_process: frontend_process.terminate()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n正在停止服务...")
    finally:
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("👋 服务已停止。")
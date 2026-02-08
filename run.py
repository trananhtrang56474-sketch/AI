import subprocess
import os
import sys
import time
import platform
import urllib.request
import urllib.error

# 获取当前脚本所在的根目录 (即 AI-MAIN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# 后端地址配置
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = "8080"
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

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

def wait_for_backend(timeout=30):
    """
    循环检查后端端口是否可以访问。
    设置最大等待时间 timeout 秒。
    """
    print("⏳ 等待后端服务就绪...", end="", flush=True)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # 尝试访问后端根目录
            with urllib.request.urlopen(BACKEND_URL, timeout=1) as response:
                # 只要有响应（哪怕是 404），说明服务起来了
                print("\n✅ 后端服务已启动！")
                return True
        except (urllib.error.URLError, ConnectionResetError) as e:
            # 如果连接被拒绝，说明还没启动好
            time.sleep(1)
            print(".", end="", flush=True)
        except Exception:
            # 其他 HTTP 错误（如 404, 500）也意味着服务已经通了，可以启动前端
            print("\n✅ 后端服务已响应！")
            return True
            
    print("\n❌ 后端启动超时，请检查后端是否有报错信息。")
    return False

def start_frontend():
    print("🚀 正在启动 Vue 前端...")
    npm_cmd = 'npm.cmd' if platform.system() == "Windows" else 'npm'
    # 启动 npm run dev
    return subprocess.Popen([npm_cmd, 'run', 'dev', '--', '--open'], cwd=FRONTEND_DIR, shell=True)

if __name__ == '__main__':
    backend_process = None
    frontend_process = None

    try:
        # 1. 启动后端
        backend_process = start_backend()
        
        # 2. 【关键修改】阻塞等待，直到后端真的能够连接
        if wait_for_backend(timeout=60):  # 最多等待 60 秒
            
            # 3. 后端准备好后，再启动前端
            frontend_process = start_frontend()

            print("\n=== ✨ 全栈项目启动成功 ===")
            print(f"🌍 前端地址: http://localhost:5173")
            print(f"🔌 后端地址: {BACKEND_URL}")
            print("🛑 按下 Ctrl + C 可以停止所有服务\n")

            # 4. 保持运行
            backend_process.wait()
            frontend_process.wait()
        else:
            # 如果后端启动失败，清理并退出
            print("程序即将退出...")
            if backend_process: backend_process.terminate()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n正在停止服务...")
    finally:
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            # Windows 下 shell=True 的进程需要用 taskkill 才能彻底杀干净，但 terminate 够用了
            frontend_process.terminate()
        print("👋 服务已停止。")
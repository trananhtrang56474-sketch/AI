import subprocess
import os
import sys
import time
import platform

# 获取当前脚本所在的根目录 (即 AI-MAIN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

def start_backend():
    print("正在启动 Flask 后端...")
    
    # 🔥 修改点：虚拟环境现在是在根目录 (BASE_DIR)，而不是 BACKEND_DIR
    if platform.system() == "Windows":
        venv_python = os.path.join(BASE_DIR, '.venv', 'Scripts', 'python.exe')
    else:
        # Mac/Linux
        venv_python = os.path.join(BASE_DIR, '.venv', 'bin', 'python')
    
    # 检查虚拟环境是否存在
    if not os.path.exists(venv_python):
        print(f"❌ 错误: 找不到虚拟环境解释器: {venv_python}")
        print("请确保在项目根目录下创建了 .venv 虚拟环境")
        sys.exit(1)
    
    # 启动 Flask
    # 注意：我们仍然保持 cwd=BACKEND_DIR，这样 Flask 里的相对路径 (如 uploads/) 还是相对于 backend 的
    return subprocess.Popen([venv_python, 'app.py'], cwd=BACKEND_DIR)

def start_frontend():
    print("正在启动 Vue 前端...")
    # Windows 下 npm 命令通常是 npm.cmd
    npm_cmd = 'npm.cmd' if platform.system() == "Windows" else 'npm'
    
    # 启动 npm run dev
    return subprocess.Popen([npm_cmd, 'run', 'dev', '--', '--open'], cwd=FRONTEND_DIR, shell=True)

if __name__ == '__main__':
    backend_process = None
    frontend_process = None

    try:
        # 1. 启动后端
        backend_process = start_backend()
        
        # 稍微等一下，让后端先初始化
        time.sleep(2)
        
        # 2. 启动前端
        frontend_process = start_frontend()

        print("\n=== 🚀 全栈项目已启动 ===")
        print("🌍 前端地址: http://localhost:5173")
        print("🔌 后端地址: http://127.0.0.1:8080")
        print("🛑 按下 Ctrl + C 可以停止所有服务\n")

        # 3. 保持主进程运行，等待两个子进程结束
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        # 当用户按下 Ctrl+C 时
        print("\n正在停止服务...")
    finally:
        # 确保杀掉子进程，防止变成僵尸进程
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            # Windows 上杀 shell=True 的进程比较麻烦，terminate 只是通知
            # 但对于开发环境来说通常够用了
            frontend_process.terminate()
        print("👋 服务已停止。")
# backend/main.py
import os
import json      # 新增：用于 JSON 格式化
import asyncio   # 新增：用于模拟异步延迟
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse  # 用于 SSE 流式返回
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 引入数据库和模型
from database import engine, Base
from models.user import User
from models.chat import ChatSession, ChatLog
from models.MoodDiary import MoodDiary

# 自动检查并创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 心理咨询 API", version="2.0")

# 1. 跨域配置 (替代原先的 CORS(app))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 静态文件代理 (图片上传目录)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# 3. 注册路由
from routes import router
app.include_router(router)

# ==========================================
# SSE 流式接口 
# ==========================================
@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """
    基于 SSE (Server-Sent Events) 的流式输出接口
    用于大模型逐字推理推送
    """
    # 模拟大模型生成的完整回复
    mock_llm_reply = "这是一段基于认知行为疗法（CBT）的专业心理干预建议。请尝试深呼吸，我们一起来分析这个非理性信念..."
    
    async def sse_generator():
        """异步生成器，模拟大模型推流"""
        for char in mock_llm_reply:
            # 组装成 SSE 规定的标准协议格式: "data: {...}\n\n"
            chunk_data = {"text": char}
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            
            # 模拟大模型推理 token 的耗时延迟
            await asyncio.sleep(0.05) 
            
        # 结束标识
        yield "data: [DONE]\n\n"

    # 返回 SSE 专用的 StreamingResponse
    return StreamingResponse(
        sse_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

# ==========================================
# 启动配置 (必须在整个文件的最末尾)
# ==========================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 FastAPI 服务启动: http://127.0.0.1:8080")
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
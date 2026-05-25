# backend/routes.py
import os
import random
import string
import json
import re
from datetime import datetime
from collections import Counter
import smtplib
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
#  引入 StreamingResponse 用于处理 PDF 内存流
from fastapi.responses import FileResponse, StreamingResponse 
from pydantic import BaseModel
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
import jieba
from fastapi.responses import StreamingResponse
from services.report_builder import build_psychological_pdf_stream

import matplotlib
matplotlib.use('Agg') # 确保多线程安全
import matplotlib.pyplot as plt

# 引入你的配置和数据库
from config import Config
from database import get_db
from models.user import User
from models.chat import ChatLog, ChatSession
from models.MoodDiary import MoodDiary

# 引入你的自定义核心智能模块 (保持原样)
from rag.retriever import rag_engine
from rag.prompt_builder import prompt_engine
from agent.emotion import analyze_emotion, analyze_trend, analyze_image
from agent.policy import PolicyRouter
from services.report_builder import build_psychological_pdf_stream

# --- LangChain 核心引入 ---
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from typing import Optional

plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

router = APIRouter(prefix="/api")

# 初始化 LangChain 千问大模型
llm = ChatTongyi(
    model_name=Config.MODEL_NAME, 
    dashscope_api_key=Config.DASHSCOPE_API_KEY
)

# 全局变量：临时存储验证码
verification_codes = {}

# ===========================
# Pydantic 数据校验模型
# ===========================
class EmailRequest(BaseModel): 
    email: str

class RegisterRequest(BaseModel): 
    email: str
    password: str
    code: str

class LoginRequest(BaseModel): 
    username: str
    password: str

class ChatRequest(BaseModel): 
    user_id: int
    session_id: Optional[int] = None
    message: Optional[str] = ""
    image_url: Optional[str] = None
    is_silent: Optional[bool] = False

class ClearHistoryRequest(BaseModel): 
    session_id: Optional[int] = None
    user_id: Optional[int] = None

class DiaryRequest(BaseModel): 
    user_id: int
    mood: Optional[str] = 'calm'
    content: str

# ===========================
# 辅助图片上传函数
# ===========================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ===========================
# 1. 基础接口 (注册/登录/验证码)
# ===========================
@router.post("/send-code")
def send_code(req: EmailRequest):
    code = ''.join(random.choices(string.digits, k=6))
    verification_codes[req.email] = code
    try:
        msg = MIMEText(f"欢迎注册 AI 心灵伴侣。\n您的验证码是：{code}\n有效期 5 分钟，请勿泄露。", 'plain', 'utf-8')
        msg['Subject'] = "【AI Counselor】注册验证码"
        msg['From'] = Config.MAIL_DEFAULT_SENDER[1] if hasattr(Config, 'MAIL_DEFAULT_SENDER') else "ui144ud851@163.com"
        msg['To'] = req.email

        server = smtplib.SMTP_SSL("smtp.163.com", 465)
        server.login(msg['From'], "MSeaSXbt4W6RFyQH") 
        server.sendmail(msg['From'], [req.email], msg.as_string())
        server.quit()
        print(f"✅ [Mail] 验证码已发送至 {req.email}")
        return {"message": "验证码发送成功"}
    except Exception as e:
        print(f"❌ [Mail Error] 发送失败: {e}")
        print(f"👉 [模拟模式] 请手动输入验证码: {code}")
        return {"message": "验证码已发送(模拟)"}

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    stored_code = verification_codes.get(req.email)
    if not stored_code or stored_code != req.code:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    if db.query(User).filter_by(username=req.email).first():
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    try:
        new_user = User(username=req.email, password_hash=generate_password_hash(req.password))
        db.add(new_user)
        db.commit()
        verification_codes.pop(req.email, None)
        return {"message": "注册成功", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=req.username).first()
    if user and check_password_hash(user.password_hash, req.password):
        return {"message": "登录成功", "user_id": user.id, "username": user.username}
    raise HTTPException(status_code=401, detail="账号或密码错误")

# ===========================
# 2. 会话管理接口
# ===========================
@router.get("/sessions")
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.strftime("%m-%d %H:%M")} for s in sessions]

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ChatSession).get(session_id)
    if not session: raise HTTPException(status_code=404, detail="会话不存在")
    db.query(ChatLog).filter_by(session_id=session_id).delete()
    db.delete(session)
    db.commit()
    return {'message': '删除成功', 'id': session_id}

@router.get("/history")
def get_history(user_id: int = None, session_id: int = None, db: Session = Depends(get_db)):
    sid = session_id
    if not sid and user_id:
        exist_s = db.query(ChatSession).filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).first()
        if exist_s: sid = exist_s.id
        else: return {"messages": [], "session_id": None}

    if not sid: return []
    logs = db.query(ChatLog).filter_by(session_id=sid).order_by(ChatLog.created_at.asc()).all()
    
    last_user_log = db.query(ChatLog).filter_by(session_id=sid, role='user').order_by(ChatLog.created_at.desc()).first()
    restored_emotion = last_user_log.emotion_tag if (last_user_log and last_user_log.emotion_tag) else "平静"
    
    last_ai_log = db.query(ChatLog).filter_by(session_id=sid, role='assistant').order_by(ChatLog.created_at.desc()).first()
    restored_strategy = last_ai_log.emotion_tag if (last_ai_log and last_ai_log.emotion_tag) else "GENERAL_SUPPORT"
    
    try:
        restored_trend = analyze_trend(sid)
    except Exception as e:
        print(f"⚠️ [History] analyze_trend 报错: {e}")
        restored_trend = "平稳"

    return {
        "session_id": sid,
        "messages": [
            {
                "sender": "user" if l.role=="user" else "ai", 
                "content": l.content,
                "image_url": getattr(l, 'image_url', None) 
            } for l in logs
        ],
        "analysis": {
            "emotion": restored_emotion, 
            "strategy": restored_strategy, 
            "trend": restored_trend
        }
    }

#  补回控制台日志
@router.post("/history/clear")
def clear_history(req: ClearHistoryRequest, db: Session = Depends(get_db)):
    if not req.session_id and not req.user_id: raise HTTPException(status_code=400, detail="缺少参数")
    try:
        if req.user_id: 
            db.query(ChatLog).filter_by(user_id=req.user_id).delete()
            print(f"🧹 [Clear] 已彻底清空用户 {req.user_id} 的所有聊天及图表底层记录")
        else: 
            db.query(ChatLog).filter_by(session_id=req.session_id).delete()
            print(f"🧹 [Clear] 已清空会话 {req.session_id} 的历史记录")
        db.commit()
        return {"message": "历史记录已彻底清除"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ===========================
# 3. 文件与图表
# ===========================
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not allowed_file(file.filename): raise HTTPException(status_code=400, detail="文件无效")
    filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())
    return {'message': '上传成功', 'url': f"http://127.0.0.1:8080/uploads/{filename}"}

# ==================================================================
# 图表接口 (首页专用，不调大模型，防止转圈等待)
# ==================================================================
@router.get("/chart-data")
def get_chart_data(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ChatLog).filter_by(user_id=user_id, role='user').order_by(ChatLog.created_at.desc()).limit(15).all()
    logs.reverse()
    
    dates, scores, arousals, valences, tags, contents = [], [], [], [], [], []
    for log in logs:
        dates.append(log.created_at.strftime("%m-%d %H:%M")) # 加上日期时间
        tags.append(log.emotion_tag or '平静')
        contents.append(log.content)
        scores.append(log.emotion_score if log.emotion_score is not None else 60)
        # 确保拿到正确的浮点数
        valences.append(getattr(log, 'valence', 5.0) or 5.0)
        arousals.append(getattr(log, 'arousal', 3.0) or 3.0)

    #  算出统计指标 (analytics) 传给左侧面板
    analytics = get_report_analytics(logs) if logs else {}

    return {
        "dates": dates, 
        "scores": scores, 
        "arousals": arousals, 
        "valences": valences, 
        "tags": tags, 
        "contents": contents,
        "analytics": analytics  # ✨ 左侧的健康指数、波动率全靠它了
    }

# ===========================
# 4. 情绪日记
# ===========================
@router.post("/diaries")
def create_diary(req: DiaryRequest, db: Session = Depends(get_db)):
    try:
        new_diary = MoodDiary(user_id=req.user_id, mood=req.mood, content=req.content)
        db.add(new_diary)
        db.commit()
        return {'success': True, 'new_diary': new_diary.to_dict()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diaries")
def get_diaries(user_id: int, db: Session = Depends(get_db)):
    diaries = db.query(MoodDiary).filter_by(user_id=user_id).order_by(MoodDiary.created_at.desc()).all()
    return {'success': True, 'diaries': [d.to_dict() for d in diaries]}
@router.delete("/diaries/{diary_id}")
def delete_diary(diary_id: int, db: Session = Depends(get_db)):
    try:
        # 查询要删除的日记
        diary = db.query(MoodDiary).filter(MoodDiary.id == diary_id).first()
        if not diary:
            return {"success": False, "message": "记录不存在"}
        
        # 执行删除并提交
        db.delete(diary)
        db.commit()
        print(f" [Diary] 成功删除日记 ID: {diary_id}")
        return {"success": True, "message": "删除成功"}
    
    except Exception as e:
        db.rollback()
        print(f"❌ [Diary] 删除日记失败: {e}")
        return {"success": False, "message": str(e)}
# ===========================
# 5. 核心智能模块接口 (RAG + Prompt Builder + Emotion Analysis + Policy Router)
# ===========================
@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    print("\n" + "="*50)
    print(" [Chat] 收到新请求...")
    
    session_id = req.session_id
    if not session_id:
        existing_session = db.query(ChatSession).filter_by(user_id=req.user_id).order_by(ChatSession.created_at.desc()).first()
        if existing_session:
            session_id = existing_session.id
        else:
            new_session = ChatSession(user_id=req.user_id, title="我的心灵伴侣")
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = new_session.id

    current_emotion, raw_score, curr_v, curr_a = "平静", 60, 5, 3
    img_caption = ""

    if req.image_url:
        print(f" 正在处理用户发送的图片: {req.image_url}")
        try:
            img_analysis = analyze_image(req.image_url)
            img_caption = f"\n[图片描述: {img_analysis['caption']}]"
            curr_v = img_analysis['valence']
            curr_a = img_analysis['arousal']
        except Exception as e:
            print(f"⚠️ 图片处理异常: {e}")

    if req.message and req.message != '[发送了图片]':
        risk_keywords = ['自杀', '不想活了', '割腕', '跳楼', '安眠药', '结束生命', '活着没意思', '交代后事', '想死']
        if any(keyword in req.message for keyword in risk_keywords):
            print(f" [Safety] 触发第一重硬熔断！匹配到高危词汇，强行接管对话流。")
            
            crisis_reply = "【系统紧急干预】我听到你现在承受着难以想象的痛苦，感觉可能已经到了极限。请先深呼吸，你不是一个人在面对这些。请立刻拨打 24小时心理危机干预热线：400-161-9995。有人在这个世界非常在乎你。"
            
            # 同样需要将这条拦截记录存入数据库，保证历史记录完整
            if not req.is_silent:
                db.add(ChatLog(
                    user_id=req.user_id, session_id=session_id, role="user", 
                    content=req.message, emotion_tag="极度痛苦", emotion_score=10, valence=1.0, arousal=9.0
                ))
                db.add(ChatLog(
                    user_id=req.user_id, session_id=session_id, role="assistant", 
                    content=crisis_reply, emotion_tag="CRISIS_INTERVENTION"
                ))
                db.commit()

            # 直接 return，彻底阻断后续的 LangChain 大模型调用！
            return {
                "reply": crisis_reply, 
                "session_id": session_id, 
                "emotion": "极度痛苦",
                "trend": "极危", 
                "score": 10, 
                "valence": 1.0, 
                "arousal": 9.0,
                "image_url": req.image_url,
                "is_crisis": True  #  给前端一个标识，前端收到 True 可以把屏幕背景变红并弹出电话框
            }
        try:
            analysis = analyze_emotion(req.message)
            current_emotion = analysis.get("tag", "平静")
            raw_score = analysis.get("score", 60)
            curr_v = analysis.get("valence", 5)
            curr_a = analysis.get("arousal", 3)
        except: pass

    smoothed_v, smoothed_a, final_chart_score = curr_v, curr_a, raw_score
    
    print("\n [Emotion Tracker] 开始执行双轨心境平滑计算 ")
    print(f"   瞬时情绪标签: [{current_emotion}]")
    print(f"   瞬时得分 (LLM原始输出): {raw_score}")
    print(f"   瞬时二维坐标 (当前V, 当前A): ({curr_v}, {curr_a})")
    if not req.is_silent:
        last_log = db.query(ChatLog).filter_by(session_id=session_id, role="user").order_by(ChatLog.created_at.desc()).first()
        if last_log and last_log.emotion_score is not None:
            last_score = last_log.emotion_score
            last_v = getattr(last_log, 'valence', 5.0) or 5.0
            last_a = getattr(last_log, 'arousal', 3.0) or 3.0
            
            if last_score < 40:
                ALPHA = 0.85 
            elif last_score > 70:
                ALPHA = 0.60 
            else:
                ALPHA = 0.70
            
            smoothed_score = last_score * ALPHA + raw_score * (1 - ALPHA)
            final_chart_score = int(max(0, min(100, smoothed_score)))
            smoothed_v = round(last_v * ALPHA + curr_v * (1 - ALPHA), 2)
            smoothed_a = round(last_a * ALPHA + curr_a * (1 - ALPHA), 2)
            
            print(f"   历史心境坐标 (Score={last_score}, V={last_v}, A={last_a})")
            print(f"   双轨平滑计算 (动态 Alpha={ALPHA}):")
            print(f"   [图表] 综合得分 = {last_score} * {ALPHA} + {raw_score} * {(1-ALPHA):.2f} = {smoothed_score:.2f} -> 入库: {final_chart_score}")
            print(f"   [底层] 心境效价(V) = {last_v} * {ALPHA} + {curr_v} * {(1-ALPHA):.2f} = {smoothed_v:.2f}")
            print(f"   [底层] 心境唤醒(A) = {last_a} * {ALPHA} + {curr_a} * {(1-ALPHA):.2f} = {smoothed_a:.2f}")
        else:
            print("   -> (未找到有效的历史数据，采用当前瞬时得分作为初始心境)")
            print("="*50 + "\n")
            
    emotion_trend = analyze_trend(session_id)
    policy = {"stage": "CHAT", "instruction": "请作为专业的心理咨询师提供支持。"}
    try:
        if req.message and req.message != '[发送了图片]':
            policy = PolicyRouter.route(current_emotion, emotion_trend, req.message, valence=curr_v, arousal=curr_a)
        elif req.image_url:
            policy = {"stage": "IMAGE_ANALYSIS", "instruction": "用户发送了一张图片，请结合图片描述给予情感反馈。"}
    except Exception as e:
        print(f"⚠️ PolicyRouter 异常: {e}")

    system_prompt = "你是专业的心理咨询师。" 
    if req.is_silent:
        recent_logs = db.query(ChatLog).filter_by(user_id=req.user_id, role='user').order_by(ChatLog.created_at.desc()).limit(5).all()
        valid_scores = [l.emotion_score for l in recent_logs if l.emotion_score is not None]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 60
        
        if avg_score >= 80: status_desc, tone = "心情极佳，充满动力", "分享喜悦，给予肯定和阳光的祝福"
        elif avg_score >= 60: status_desc, tone = "心态平稳，情绪正常", "温馨问候，像老朋友一样自然地关心"
        elif avg_score >= 40: status_desc, tone = "情绪略显低落或疲惫", "温柔共情，提供轻柔的安抚和理解"
        else: status_desc, tone = "情绪处于低谷，需要关怀", "深度宽慰，给予坚定的陪伴感和守护"

        system_prompt = f"【首页寄语任务】近期评分:{avg_score}/100({status_desc})。请用第二人称写一句30字内治愈寄语。语气:{tone}。"
    else:
        try:
            knowledge = rag_engine.search(req.message or "心理健康")
            base_prompt = prompt_engine.build(knowledge)
        except:
            base_prompt = "你是专业的心理咨询师。"
        
        instruction = policy.get('instruction', '')
        system_prompt = f"{base_prompt}\n\n### 实时数值感知\n- 效价(Valence): {curr_v}\n- 唤醒度(Arousal): {curr_a}\n- 状态分值: {raw_score}\n- 操作指令: {instruction}"

    history_logs = db.query(ChatLog).filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(8).all()
    history_logs.reverse()
    chat_history = []
    for l in history_logs:
        if l.role == "user": chat_history.append(HumanMessage(content=l.content))
        else: chat_history.append(AIMessage(content=l.content))

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt), 
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}")
    ])
   
    chain = prompt_template | llm

    full_user_input = f"{req.message or ''}{img_caption}".strip()
    if not full_user_input: full_user_input = "[发送了图片]"

    try:
        response = chain.invoke({"history": chat_history, "input": full_user_input})
        ai_reply = response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 响应失败: {str(e)}")

    if not req.is_silent:
        db.add(ChatLog(
            user_id=req.user_id, 
            session_id=session_id, 
            role="user", 
            content=req.message or "[发送了图片]", 
            image_url=req.image_url, 
            emotion_tag=current_emotion, 
            emotion_score=final_chart_score, 
            valence=smoothed_v, 
            arousal=smoothed_a
        ))
        db.add(ChatLog(
            user_id=req.user_id, 
            session_id=session_id, 
            role="assistant", 
            content=ai_reply, 
            emotion_tag=policy.get('stage', 'CHAT')
        ))
        db.commit()

    return {
        "reply": ai_reply, 
        "session_id": session_id, 
        "emotion": current_emotion,
        "trend": emotion_trend, 
        "score": final_chart_score, 
        "valence": smoothed_v, 
        "arousal": smoothed_a,
        "image_url": req.image_url 
    }

# ==================================================================
#  6. 报告与 PDF 接口
# ==================================================================
def get_report_analytics(logs):
    if not logs: return None
    scores = [l.emotion_score for l in logs if l.emotion_score is not None]
    valences = [getattr(l, 'valence', 5) for l in logs if getattr(l, 'valence', None) is not None]
    arousals = [getattr(l, 'arousal', 3) for l in logs if getattr(l, 'arousal', None) is not None]
    contents = [l.content for l in logs if l.content and l.content != '[发送了图片]']
    
    dist = {"positive": sum(1 for s in scores if s >= 70), "neutral": sum(1 for s in scores if 40 <= s < 70), "negative": sum(1 for s in scores if s < 40)}
    volatility = round(float(np.std(scores)), 2) if len(scores) > 1 else 0

    words = []
    stop_words = {'了', '的', '我', '是', '在', '不', '有', '和', '就', '也'}
    for text in contents:
        words += [w for w in jieba.lcut(text) if len(w) > 1 and w not in stop_words]
    top_keywords = [{"name": k, "value": v} for k, v in Counter(words).most_common(12)]

    avg_score = float(np.mean(scores)) if scores else 60
    health_index = int(max(0, min(100, avg_score - (volatility * 0.3))))
    avg_v = round(float(np.mean(valences)), 2) if valences else 5
    avg_a = round(float(np.mean(arousals)), 2) if arousals else 3

    risk_level = "HIGH" if health_index < 45 or volatility > 20 else ("MEDIUM" if health_index < 60 or volatility > 15 else "LOW")
    
    #  修复 1: 临床高危敏感词抓取逻辑补回
    risk_keywords = ['累', '痛', '绝望', '烦', '不想', '没意义', '抑郁', '难受', '崩溃', '撑不住', '死', '放弃']
    high_risk_quotes = []
    for l in logs:
        if l.content and l.content != '[发送了图片]':
            if (l.emotion_score is not None and l.emotion_score <= 35) or any(k in l.content for k in risk_keywords):
                high_risk_quotes.append({
                    "time": l.created_at.strftime("%m-%d %H:%M"), 
                    "text": l.content
                })
    high_risk_quotes = high_risk_quotes[-4:]
    
    progress_delta = round(float(np.mean(scores[len(scores)//2:]) - np.mean(scores[:len(scores)//2])), 1) if len(scores) >= 4 else 0

    persona = "平稳发展型"
    if avg_v < 4.5 and avg_a >= 6: persona = "高压焦虑型"
    elif avg_v < 4.5 and avg_a < 4.5: persona = "疲惫耗竭型"
    elif volatility > 18: persona = "情绪敏感型"
    elif avg_v >= 6.5: persona = "阳光成长型"

    return {
        "distribution": dist, "volatility": volatility, "keywords": top_keywords, "health_index": health_index,
        "risk_level": risk_level, "avg_v": avg_v, "avg_a": avg_a, "raw_valences": valences, "raw_arousals": arousals,
        "high_risk_quotes": high_risk_quotes, "progress_delta": progress_delta, "persona": persona
    }
@router.get("/report")
def get_report(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ChatLog).filter_by(user_id=user_id, role='user').order_by(ChatLog.created_at.desc()).limit(50).all()
    logs.reverse()
    if len(logs) < 3: raise HTTPException(status_code=400, detail="数据样本不足，请多聊几句")

    analytics = get_report_analytics(logs)
    dates = [l.created_at.strftime("%m-%d %H:%M") for l in logs] # 建议加上时间，图表更好看
    scores = [l.emotion_score or 60 for l in logs]
    trend_tag = analyze_trend(logs[-1].session_id)
    
    #  核心修复 1：把原来 /chart-data 里的四个数组搬过来
    valences = [getattr(l, 'valence', 5.0) for l in logs]
    arousals = [getattr(l, 'arousal', 3.0) for l in logs]
    tags = [l.emotion_tag or '平静' for l in logs]
    contents = [l.content for l in logs]

    recent_texts = [l.content for l in logs[-15:] if l.content != '[发送了图片]']
    summary_prompt = f"""
    专业心理干预AI，生成结构化报告。
    - 画像: {analytics['persona']}
    - 波动: {analytics['volatility']}
    - 干预环比: {analytics['progress_delta']}
    - 捕获高危原话: {[q['text'] for q in analytics['high_risk_quotes']]} 
    - 对话切片: {recent_texts}
    输出严格JSON: {{"status_summary": "...", "core_issues": ["..."], "action_advices": ["..."]}}
    """
    
    try:
        res = llm.invoke([SystemMessage(content=summary_prompt)]).content
        match = re.search(r'\{.*\}', res, re.DOTALL)
        if match:
            ai_summary = json.loads(match.group())
        else:
            raise ValueError("No JSON matched") 
    except:
        ai_summary = {
            "status_summary": "情绪处于自然波动期，系统正在持续守护您的心理内稳态。", 
            "core_issues": ["未检测到明显危机"], 
            "action_advices": ["继续保持觉察", "深呼吸"]
        }

    #  核心修复 2：把这 4 个数组一起返回给前端
    return {
        "dates": dates, 
        "scores": scores, 
        "valences": valences, 
        "arousals": arousals, 
        "tags": tags, 
        "contents": contents,
        "analytics": analytics, 
        "trend": trend_tag, 
        "summary": ai_summary
    }
# ==================================================================
#  8. 导出学术版情绪轨迹图 (PNG)
# ==================================================================
@router.get("/export-trajectory")
def export_trajectory(user_id: int, session_id: int = None, db: Session = Depends(get_db)):
    if session_id:
        logs = db.query(ChatLog).filter_by(session_id=session_id, role="user").order_by(ChatLog.created_at.asc()).all()
    else:
        latest = db.query(ChatLog).filter_by(user_id=user_id, role="user").order_by(ChatLog.created_at.desc()).first()
        if not latest: raise HTTPException(status_code=404, detail="无记录")
        logs = db.query(ChatLog).filter_by(session_id=latest.session_id, role="user").order_by(ChatLog.created_at.asc()).all()

    if len(logs) < 2: raise HTTPException(status_code=400, detail="轮次不足")

    turns = [f"T{i+1}" for i in range(len(logs))]
    scores = [l.emotion_score or 60 for l in logs]
    arousals = [getattr(l, 'arousal', 3) or 3 for l in logs]
    tags = [l.emotion_tag or '平静' for l in logs]

    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        ax1.plot(turns, scores, marker='o', color='#1890FF', linewidth=2)
        ax1.set_ylim(0, 105)
        #  修复 5: 找回学术级图表坐标标题
        ax1.set_ylabel("心情指数 (Score: 0-100)", fontsize=12)
        ax1.set_title("会话诊断: 心理状态双轨轨迹 (基于 Russell 模型)", fontsize=14, pad=15)
        ax1.grid(True, linestyle='--', alpha=0.5)
        for i, txt in enumerate(tags): ax1.annotate(txt, (turns[i], scores[i] + 4), ha='center')

        ax2.plot(turns, arousals, marker='s', color='#FF4D4F', linewidth=2)
        ax2.set_ylim(0, 11)
        ax2.set_xlabel("对话轮次 (Turn)", fontsize=12)
        ax2.set_ylabel("躯体唤醒度 (Arousal: 1-10)", fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.5)
        fig.tight_layout()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(BASE_DIR, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"trajectory_{int(datetime.now().timestamp())}.png"
        save_path = os.path.join(upload_folder, filename)
        
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig) 
        return {"message": "生成成功", "url": f"http://127.0.0.1:8080/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================================================================
#  9. PDF
# ==================================================================
@router.get("/export-pdf-pro")
def export_pdf_pro(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(ChatLog).filter_by(user_id=user_id, role='user').order_by(ChatLog.created_at.desc()).limit(30).all()
    logs.reverse()
    if len(logs) < 2: raise HTTPException(status_code=400, detail="数据不足")

    dates = [l.created_at.strftime("%m-%d") for l in logs]
    scores = [l.emotion_score or 60 for l in logs]
    valences = [getattr(l, 'valence', 5) for l in logs]
    arousals = [getattr(l, 'arousal', 3) for l in logs]
    analytics = get_report_analytics(logs)
    
    #  修复 6: PDF内文补回核心维度的展示
    summary = {
        "status_summary": f"用户当前处于{analytics.get('persona', '平稳')}状态。近期平均情绪效价 {analytics.get('avg_v')}，唤醒度 {analytics.get('avg_a')}。",
        "core_issues": [k['name'] for k in analytics.get('keywords', [])[:3]] or ["暂无显著压力"],
        "action_advices": ["保持规律作息", "尝试进行简单的正念深呼吸"]
    }

    try:
        # 核心：调用新的 Playwright 生成器
        pdf_buffer = build_psychological_pdf_stream(analytics, summary, dates, scores, valences, arousals)
        
        return StreamingResponse(
            pdf_buffer, 
            media_type='application/pdf', 
            headers={"Content-Disposition": f"attachment; filename=Insight_Report_{user_id}.pdf"}
        )
    except Exception as e:
        print(f"❌ PDF 导出失败: {e}")
        raise HTTPException(status_code=500, detail="生成 PDF 失败")
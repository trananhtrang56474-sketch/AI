# backend/routes.py
import os
import random
import string
import json
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Message
from flask import send_file, request, jsonify
from services.report_builder import build_psychological_pdf_stream
# 引入配置
from extensions import db, mail
# 引入模型
from models import User, ChatLog, ChatSession, MoodDiary

# 引入核心智能模块
from llm.qwen_client import QwenClient
from rag.retriever import rag_engine
from rag.prompt_builder import prompt_engine
from agent.emotion import analyze_emotion, analyze_trend
from agent.policy import PolicyRouter

import numpy as np
from collections import Counter
import jieba
# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')
llm_client = QwenClient()

# 全局变量：临时存储验证码
verification_codes = {}

import matplotlib
# 必须在导入 pyplot 之前设置无头模式，确保 Flask 多线程安全
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
from datetime import datetime

# 解决 Matplotlib 中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
# ===========================
# 辅助函数
# ===========================
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# ===========================
# 1. 基础接口 (注册/登录/验证码)
# ===========================

@api_bp.route("/send-code", methods=["POST"])
def send_code():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "请输入邮箱地址"}), 400

    code = ''.join(random.choices(string.digits, k=6))
    verification_codes[email] = code

    try:
        msg = Message(subject="【AI Counselor】注册验证码", recipients=[email])
        msg.body = f"欢迎注册 AI 心灵伴侣 心理咨询平台。\n您的验证码是：{code}\n有效期 5 分钟，请勿泄露给他人。"
        
        mail.send(msg)
        print(f"✅ [Mail] 验证码已发送至 {email}")
        return jsonify({"message": "验证码发送成功"})

    except Exception as e:
        print(f"❌ [Mail Error] 发送失败: {e}")
        print(f"👉 [模拟模式] 请手动输入验证码: {code}")
        return jsonify({"message": "验证码已发送(模拟)"})

@api_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    code = data.get("code")

    if not email or not password or not code:
        return jsonify({"error": "信息填写不完整"}), 400

    stored_code = verification_codes.get(email)
    if not stored_code or stored_code != code:
        return jsonify({"error": "验证码错误或已过期"}), 400

    if User.query.filter_by(username=email).first():
        return jsonify({"error": "该邮箱已注册"}), 400

    try:
        new_user = User(username=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        verification_codes.pop(email, None)
        return jsonify({"message": "注册成功", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    
    if user and check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"message": "登录成功", "user_id": user.id, "username": user.username})
    return jsonify({"error": "账号或密码错误"}), 401

# ==================================================================
# 📚 会话管理接口 (单会话优化)
# ==================================================================
@api_bp.route("/sessions", methods=["GET"])
def get_sessions():
    uid = request.args.get("user_id")
    if not uid: return jsonify([])
    sessions = ChatSession.query.filter_by(user_id=uid).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title, "created_at": s.created_at.strftime("%m-%d %H:%M")} for s in sessions])

@api_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        session = ChatSession.query.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在'}), 404
        
        ChatLog.query.filter_by(session_id=session_id).delete()
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': '删除成功', 'id': session_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================================================================
# 🔥 历史记录接口
# ==================================================================
@api_bp.route("/history", methods=["GET"])
def get_history():
    sid = request.args.get("session_id")
    uid = request.args.get("user_id")

    if not sid and uid:
        exist_s = ChatSession.query.filter_by(user_id=uid).order_by(ChatSession.created_at.desc()).first()
        if exist_s:
            sid = exist_s.id
        else:
            return jsonify({"messages": [], "session_id": None})

    if not sid: return jsonify([])

    logs = ChatLog.query.filter_by(session_id=sid).order_by(ChatLog.created_at.asc()).all()
    
    last_user_log = ChatLog.query.filter_by(session_id=sid, role='user').order_by(ChatLog.created_at.desc()).first()
    restored_emotion = last_user_log.emotion_tag if (last_user_log and last_user_log.emotion_tag) else "平静"
    
    last_ai_log = ChatLog.query.filter_by(session_id=sid, role='assistant').order_by(ChatLog.created_at.desc()).first()
    restored_strategy = last_ai_log.emotion_tag if (last_ai_log and last_ai_log.emotion_tag) else "GENERAL_SUPPORT"
    
    restored_trend = analyze_trend(sid)

    return jsonify({
        "session_id": sid,
        "messages": [{"sender": "user" if l.role=="user" else "ai", "content": l.content} for l in logs],
        "analysis": {
            "emotion": restored_emotion,
            "strategy": restored_strategy,
            "trend": restored_trend
        }
    })

# ===========================
# 2. 文件上传与统计 (升级版：返回双维度数据)
# ===========================
@api_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': '无文件'}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename): return jsonify({'error': '文件无效'}), 400
    
    filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
        file_url = f"http://127.0.0.1:8080/uploads/{filename}"
        return jsonify({'message': '上传成功', 'url': file_url})
    except: return jsonify({'error': '保存失败'}), 500

@api_bp.route("/chart-data", methods=["GET"])
def get_chart_data():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"dates": [], "scores": []})

    query = ChatLog.query.filter_by(user_id=user_id, role='user')
    logs = query.order_by(ChatLog.created_at.desc()).limit(15).all()
    logs.reverse()
    
    dates, scores, arousals, valences, tags, contents = [], [], [], [], [], []
    for log in logs:
        dates.append(log.created_at.strftime("%H:%M"))
        tag = log.emotion_tag or '平静'
        tags.append(tag)
        contents.append(log.content)
        
        if log.emotion_score is not None:
            scores.append(log.emotion_score)
        else:
            scores.append(60) 
            
        v = getattr(log, 'valence', None)
        a = getattr(log, 'arousal', None)
        valences.append(v if v is not None else 5)
        arousals.append(a if a is not None else 3)

    return jsonify({
        "dates": dates, 
        "scores": scores,
        "arousals": arousals,
        "valences": valences,
        "tags": tags,
        "contents": contents 
    })

# ===========================
# 3. 情绪日记
# ===========================
@api_bp.route('/diaries', methods=['POST'])
def create_diary():
    data = request.json
    user_id, content = data.get('user_id'), data.get('content')
    if not user_id or not content: return jsonify({'success': False}), 400
    try:
        new_diary = MoodDiary(user_id=user_id, mood=data.get('mood', 'calm'), content=content)
        db.session.add(new_diary)
        db.session.commit()
        return jsonify({'success': True, 'new_diary': new_diary.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/diaries', methods=['GET'])
def get_diaries():
    user_id = request.args.get('user_id')
    if not user_id: return jsonify({'success': False}), 401
    diaries = MoodDiary.query.filter_by(user_id=user_id).order_by(MoodDiary.created_at.desc()).all()
    return jsonify({'success': True, 'diaries': [d.to_dict() for d in diaries]})

# ==================================================================
# 🧹 修改：物理清空对话记录接口 (彻底连根拔起)
# ==================================================================
@api_bp.route("/history/clear", methods=["POST"])
def clear_history():
    data = request.json
    sid = data.get("session_id")
    uid = data.get("user_id")

    if not sid: 
        return jsonify({"error": "缺少会话ID"}), 400

    try:
        if uid:
            ChatLog.query.filter_by(user_id=uid).delete()
            print(f"🧹 [Clear] 已彻底清空用户 {uid} 的所有聊天及图表底层记录")
        else:
            ChatLog.query.filter_by(session_id=sid).delete()
            print(f"🧹 [Clear] 已清空会话 {sid} 的历史记录")
            
        db.session.commit()
        return jsonify({"message": "历史记录已彻底清除"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================================================================
# 🔥 5. 核心聊天接口 (基于 Russell 1980 文献的双轨制平滑算法)
# ==================================================================
@api_bp.route("/chat", methods=["POST"])
def chat():
    print("\n" + "="*50)
    print("💡 [Chat] 收到新请求...")
    data = request.json
    user_msg = data.get("message", "")   
    image_url = data.get("image_url")    
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    is_silent = data.get("is_silent", False)

    if not user_id: return jsonify({"error": "参数缺失"}), 400

    if not session_id:
        existing_session = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).first()
        if existing_session:
            session_id = existing_session.id
        else:
            try:
                new_session = ChatSession(user_id=user_id, title="我的心灵伴侣")
                db.session.add(new_session); db.session.commit()
                session_id = new_session.id
            except: return jsonify({"error": "初始化失败"}), 500

    # B. 实时情绪分析 (提取瞬时二维坐标)
    
    current_emotion, raw_score = "平静", 60
    curr_v, curr_a = 5, 3
    
    if user_msg and user_msg != '[发送了图片]':
        analysis = analyze_emotion(user_msg)
        current_emotion = analysis.get("tag", "平静")
        raw_score = analysis.get("score", 60)
        curr_v = analysis.get("valence", 5)
        curr_a = analysis.get("arousal", 3)
    
    # ✨✨✨ 核心升级：基于 Russell 二维空间向量的双轨制“心境质心”追踪算法 ✨✨✨
    smoothed_v = curr_v
    smoothed_a = curr_a
    final_chart_score = raw_score 

    print("\n📊 [Emotion Tracker] 开始执行双轨心境平滑计算 (依据 Russell, 1980)")
    print(f"   -> 瞬时情绪标签: [{current_emotion}]")
    print(f"   -> 瞬时得分 (LLM原始输出): {raw_score}")
    print(f"   -> 瞬时二维坐标 (当前V, 当前A): ({curr_v}, {curr_a})")

    if not is_silent:
        last_log = ChatLog.query.filter_by(session_id=session_id, role="user")\
                   .order_by(ChatLog.created_at.desc()).first()
                   
        if last_log and last_log.emotion_score is not None:
            last_score = last_log.emotion_score
            last_v = getattr(last_log, 'valence', 5) or 5
            last_a = getattr(last_log, 'arousal', 3) or 3
            
            if last_score < 40:
                ALPHA = 0.85 
            elif last_score > 70:
                ALPHA = 0.60 
            else:
                ALPHA = 0.70 
            
            smoothed_score = last_score * ALPHA + raw_score * (1 - ALPHA)
            final_chart_score = int(max(0, min(100, smoothed_score)))
            
            smoothed_v = last_v * ALPHA + curr_v * (1 - ALPHA)
            smoothed_a = last_a * ALPHA + curr_a * (1 - ALPHA)
            
            print(f"   -> 历史心境坐标 (Score={last_score}, V={last_v}, A={last_a})")
            print(f"   -> 双轨平滑计算 (动态 Alpha={ALPHA}):")
            print(f"      * [图表] 综合得分 = {last_score} * {ALPHA} + {raw_score} * {1-ALPHA:.2f} = {smoothed_score:.2f} -> 入库: {final_chart_score}")
            print(f"      * [底层] 心境效价(V) = {last_v} * {ALPHA} + {curr_v} * {1-ALPHA:.2f} = {smoothed_v:.2f}")
            print(f"      * [底层] 心境唤醒(A) = {last_a} * {ALPHA} + {curr_a} * {1-ALPHA:.2f} = {smoothed_a:.2f}")
        else:
            print("   -> (未找到有效的历史数据，采用当前瞬时得分作为初始心境)")
            final_chart_score = raw_score
            
    print("="*50 + "\n")

    emotion_trend = analyze_trend(session_id)
    policy = PolicyRouter.route(current_emotion, emotion_trend, user_msg, valence=curr_v, arousal=curr_a) if user_msg else {"stage": "CHAT", "instruction": "分析图片"}

    knowledge = None
    if not is_silent:
        knowledge = rag_engine.search(user_msg)

    base_prompt = prompt_engine.build(knowledge)
    
    if is_silent:
        recent_logs = ChatLog.query.filter_by(user_id=user_id, role='user')\
                      .order_by(ChatLog.created_at.desc()).limit(5).all()
        
        valid_scores = [l.emotion_score for l in recent_logs if l.emotion_score is not None]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 60
        
        if avg_score >= 80:
            status_desc, tone = "心情极佳，充满动力", "分享喜悦，给予肯定和阳光的祝福"
        elif avg_score >= 60:
            status_desc, tone = "心态平稳，情绪正常", "温馨问候，像老朋友一样自然地关心"
        elif avg_score >= 40:
            status_desc, tone = "情绪略显低落或疲惫", "温柔共情，提供轻柔的安抚和理解"
        else:
            status_desc, tone = "情绪处于低谷，需要关怀", "深度宽慰，给予坚定的陪伴感和最柔软的守护"

        instruction = f"""
        【重要：首页寄语任务】
        当前用户的情绪量化评分为: {avg_score}/100。
        该分值反映用户近期状态为: {status_desc}。
        请忽略当前 User 传入的指令文本，完全基于这个【评分数值】和【对应状态】，
        用第二人称写一句 30 字以内的治愈系关怀寄语。
        你的语气应当: {tone}。
        """
    else:
        instruction = policy.get('instruction', '')
    
    final_prompt = f"{base_prompt}\n\n### 实时数值感知\n- 效价(Valence): {curr_v}\n- 唤醒度(Arousal): {curr_a}\n- 状态分值: {raw_score}\n- 操作指令: {instruction}"

    history = ChatLog.query.filter_by(session_id=session_id).order_by(ChatLog.created_at.desc()).limit(8).all()
    history.reverse()
    messages = [{"role": "system", "content": final_prompt}]
    for l in history: messages.append({"role": l.role, "content": l.content})
    if user_msg: messages.append({"role": "user", "content": user_msg})

    # ✨✨✨ 核心修复：添加识别图片路径解析逻辑 ✨✨✨
    local_img_path = None
    if image_url:
        # 从 URL 中提取文件名并拼接成本地绝对路径
        filename = image_url.split('/')[-1]
        local_img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        print(f"🔍 检测到图片，已解析本地路径: {local_img_path}")

    # 调用 QwenClient 时传入 image_path 参数
    ai_reply = llm_client.chat(messages, image_path=local_img_path)

    if not is_silent:
        try:
            if user_msg:
                db.session.add(ChatLog(
                    user_id=user_id, 
                    session_id=session_id, 
                    role="user", 
                    content=user_msg, 
                    emotion_tag=current_emotion, 
                    emotion_score=final_chart_score, 
                    valence=smoothed_v,               
                    arousal=smoothed_a               
                ))
            db.session.add(ChatLog(
                user_id=user_id, 
                session_id=session_id, 
                role="assistant", 
                content=ai_reply, 
                emotion_tag=policy.get('stage')
            ))
            db.session.commit()
        except Exception as e:
            print("DB Save Error:", e)
            db.session.rollback()

    return jsonify({
        "reply": ai_reply, 
        "session_id": session_id,
        "emotion": current_emotion,
        "trend": emotion_trend,
        "score": final_chart_score,
        "valence": smoothed_v,
        "arousal": smoothed_a
    })
# ==================================================================
# 📊 6. 深度心理洞察报告接口 (全维度聚合 + 高阶临床指标)
# ==================================================================

def get_report_analytics(logs):
    """计算分布、波动率、关键词、画像、干预追踪等高阶指标"""
    if not logs:
        return None
    
    scores = [l.emotion_score for l in logs if l.emotion_score is not None]
    valences = [getattr(l, 'valence', 5) for l in logs if getattr(l, 'valence', None) is not None]
    arousals = [getattr(l, 'arousal', 3) for l in logs if getattr(l, 'arousal', None) is not None]
    contents = [l.content for l in logs if l.content and l.content != '[发送了图片]']
    
    # 1. 情绪分布
    dist = {"positive": 0, "neutral": 0, "negative": 0}
    for s in scores:
        if s >= 70: dist["positive"] += 1
        elif s >= 40: dist["neutral"] += 1
        else: dist["negative"] += 1
    
    # 2. 情绪波动率 (Standard Deviation)
    volatility = round(float(np.std(scores)), 2) if len(scores) > 1 else 0

    # 3. 关键词提取
    words = []
    stop_words = {'了', '的', '我', '是', '在', '不', '有', '和', '就', '也', '都', '啊', '吗', '这', '很', '你', '什么', '怎么'}
    for text in contents:
        seg = jieba.lcut(text)
        words += [w for w in seg if len(w) > 1 and w not in stop_words]
    top_keywords = [{"name": k, "value": v} for k, v in Counter(words).most_common(12)]

    # 4. 综合健康指数
    avg_score = float(np.mean(scores)) if scores else 60
    health_index = int(max(0, min(100, avg_score - (volatility * 0.3))))

    avg_v = round(float(np.mean(valences)), 2) if valences else 5
    avg_a = round(float(np.mean(arousals)), 2) if arousals else 3

    # ✨ 5. 风险预警与高危原话提取 (临床锚点)
    risk_level = "LOW"
    if health_index < 45 or volatility > 20:
        risk_level = "HIGH"
    elif health_index < 60 or volatility > 15:
        risk_level = "MEDIUM"

    risk_keywords = ['累', '痛', '绝望', '烦', '不想', '没意义', '抑郁', '难受', '崩溃', '撑不住', '死', '放弃']
    high_risk_quotes = []
    for l in logs:
        if l.content and l.content != '[发送了图片]':
            # 分数极低 或 包含高危词汇
            if (l.emotion_score is not None and l.emotion_score <= 35) or any(k in l.content for k in risk_keywords):
                high_risk_quotes.append({
                    "time": l.created_at.strftime("%m-%d %H:%M"), 
                    "text": l.content
                })
    # 取最近的 4 条高危原话
    high_risk_quotes = high_risk_quotes[-4:]

    # ✨ 6. 干预跟踪 (周期环比: 近半周期 vs 前半周期)
    progress_delta = 0
    if len(scores) >= 4:
        half = len(scores) // 2
        older_half_avg = np.mean(scores[:half])
        recent_half_avg = np.mean(scores[half:])
        progress_delta = round(float(recent_half_avg - older_half_avg), 1)

    # ✨ 7. 用户画像 (Rule-based 情绪模式聚类)
    persona = "平稳发展型"
    if avg_v < 4.5 and avg_a >= 6:
        persona = "高压焦虑型" # 负效价 + 高唤醒 (一直处于紧绷状态)
    elif avg_v < 4.5 and avg_a < 4.5:
        persona = "疲惫耗竭型" # 负效价 + 低唤醒 (能量被掏空)
    elif volatility > 18:
        persona = "情绪敏感型" # 极度容易受外界影响，大起大落
    elif avg_v >= 6.5:
        persona = "阳光成长型"

    return {
        "distribution": dist,
        "volatility": volatility,
        "keywords": top_keywords,
        "health_index": health_index,
        "risk_level": risk_level,
        "avg_v": avg_v,
        "avg_a": avg_a,
        "raw_valences": valences, 
        "raw_arousals": arousals,
        "high_risk_quotes": high_risk_quotes, # 原话回溯
        "progress_delta": progress_delta,     # 环比变化
        "persona": persona                    # 用户画像
    }

@api_bp.route("/report", methods=["GET"])
def get_report():
    user_id = request.args.get("user_id")
    if not user_id: return jsonify({"error": "缺少用户标识"}), 400

    # ✨ 将分析样本扩大到 50 条，支撑长期趋势对比
    logs = ChatLog.query.filter_by(user_id=user_id, role='user')\
            .order_by(ChatLog.created_at.desc()).limit(50).all()
    logs.reverse()

    if len(logs) < 3:
        return jsonify({"error": "数据样本不足，请多聊几句再生成报告"}), 400

    analytics = get_report_analytics(logs)
    dates = [l.created_at.strftime("%m-%d") for l in logs]
    scores = [l.emotion_score or 60 for l in logs]
    trend_tag = analyze_trend(logs[-1].session_id)

    # 构造 AI 总结 Prompt
    recent_texts = [l.content for l in logs[-15:] if l.content != '[发送了图片]']
    summary_prompt = f"""
    你是专业的心理干预AI。请根据以下数据生成结构化报告。
    - 用户画像: {analytics['persona']}
    - 情绪稳定性: {analytics['volatility']}
    - 近期干预环比变化: {analytics['progress_delta']} 分 (>0说明干预有效在好转)
    - 捕获的高危原话: {[q['text'] for q in analytics['high_risk_quotes']]}
    - 近期对话切片: {recent_texts}

    请输出严格 JSON：
    {{
      "status_summary": "基于画像和变化，给出80字内总体心理评估",
      "core_issues": ["核心困扰1", "核心困扰2"],
      "action_advices": ["CBT建议1", "行为激活建议2"]
    }}
    """
    
    try:
        ai_raw = llm_client.chat([{"role": "user", "content": summary_prompt}])
        match = re.search(r'\{.*\}', ai_raw, re.DOTALL)
        ai_summary = json.loads(match.group()) if match else {
            "status_summary": "情绪处于自然波动期，系统正在持续守护您的心理内稳态。",
            "core_issues": ["未检测到明显危机"],
            "action_advices": ["继续保持觉察", "深呼吸"]
        }
    except Exception:
        ai_summary = {"status_summary": "分析加载中...", "core_issues": [], "action_advices": []}

    return jsonify({
        "dates": dates,
        "scores": scores,
        "analytics": analytics,
        "trend": trend_tag,
        "summary": ai_summary
    })
# ==================================================================
# 📈 7. 导出学术版情绪轨迹图 (PNG)
# ==================================================================
@api_bp.route("/export-trajectory", methods=["GET"])
def export_trajectory():
    user_id = request.args.get("user_id")
    session_id = request.args.get("session_id")
    
    if not user_id:
        return jsonify({"error": "缺少用户标识"}), 400

    # 1. 确定要导出的会话 (如果传了 session_id 则用传的，否则取该用户最新的一条对话所在的会话)
    if session_id:
        logs = ChatLog.query.filter_by(session_id=session_id, role="user").order_by(ChatLog.created_at.asc()).all()
    else:
        # 找最近有记录的会话
        latest_log = ChatLog.query.filter_by(user_id=user_id, role="user").order_by(ChatLog.created_at.desc()).first()
        if not latest_log:
            return jsonify({"error": "暂无对话记录，无法生成轨迹图"}), 404
        session_id = latest_log.session_id
        logs = ChatLog.query.filter_by(session_id=session_id, role="user").order_by(ChatLog.created_at.asc()).all()

    if len(logs) < 2:
        return jsonify({"error": "对话轮次太少，暂无法生成有意义的轨迹图"}), 400

    # 2. 提取数据
    turns, scores, arousals, tags = [], [], [], []
    for i, log in enumerate(logs):
        turns.append(f"T{i+1}")
        scores.append(log.emotion_score if log.emotion_score is not None else 60)
        arousals.append(getattr(log, 'arousal', 3) if getattr(log, 'arousal', None) is not None else 3)
        tags.append(log.emotion_tag or '平静')

    # 3. 使用线程安全的 Figure 对象绘制专业双轨图
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # --- 子图 1: 心境指数走势 (Valence/Score) ---
        ax1.plot(turns, scores, marker='o', linestyle='-', color='#1890FF', linewidth=2, markersize=8) # 匹配你前端的蓝色系
        ax1.set_ylim(0, 105)
        ax1.set_ylabel("心情指数 (Score: 0-100)", fontsize=12)
        ax1.set_title(f"会话诊断: 心理状态双轨轨迹 (基于 Russell 模型)", fontsize=14, pad=15)
        ax1.grid(True, linestyle='--', alpha=0.5)
        ax1.axhline(y=60, color='gray', linestyle='--', alpha=0.4)

        for i, txt in enumerate(tags):
            ax1.annotate(txt, (turns[i], scores[i] + 4), fontsize=10, ha='center', color='#333333')

        # --- 子图 2: 唤醒度走势 (Arousal) ---
        ax2.plot(turns, arousals, marker='s', linestyle='-', color='#FF4D4F', linewidth=2, markersize=8) # 红色代表唤醒
        ax2.set_ylim(0, 11)
        ax2.set_ylabel("躯体唤醒度 (Arousal: 1-10)", fontsize=12)
        ax2.set_xlabel("对话轮次 (Turn)", fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.5)
        ax2.axhline(y=5, color='gray', linestyle='--', alpha=0.4)
        
        fig.tight_layout()

        # 4. 确保目录存在并保存图片
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = f"trajectory_u{user_id}_s{session_id}_{int(datetime.now().timestamp())}.png"
        save_path = os.path.join(upload_folder, filename)
        
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # ⚠️ 显式关闭并清理内存，防止 Flask 内存泄漏
        plt.close(fig) 

        # 5. 返回可访问的 URL
        # 注意：这里的 8080 端口要根据你实际后端的配置调整
        file_url = f"http://127.0.0.1:8080/uploads/{filename}"
        
        return jsonify({
            "message": "轨迹图生成成功",
            "url": file_url
        })

    except Exception as e:
        print(f"❌ 轨迹图生成失败: {e}")
        return jsonify({"error": f"图像渲染失败: {str(e)}"}), 500
    # ==================================================================
# 📄 8. 终极版：纯后端生成媲美前端 UI 的企业级 PDF
# ==================================================================
@api_bp.route("/export-pdf-pro", methods=["GET"])
def export_pdf_pro():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "缺少用户标识"}), 400

    # 1. 查询基础数据
    logs = ChatLog.query.filter_by(user_id=user_id, role='user').order_by(ChatLog.created_at.desc()).limit(30).all()
    logs.reverse()

    if len(logs) < 2:
        return jsonify({"error": "数据不足，无法生成报告"}), 400

    # 2. 聚合参数
    dates = [l.created_at.strftime("%m-%d") for l in logs]
    scores = [l.emotion_score or 60 for l in logs]
    valences = [getattr(l, 'valence', 5) for l in logs]
    arousals = [getattr(l, 'arousal', 3) for l in logs]
    analytics = get_report_analytics(logs)
    
    summary = {
        "status_summary": f"用户当前处于{analytics.get('persona', '平稳')}状态。近期平均情绪效价 {analytics.get('avg_v')}，唤醒度 {analytics.get('avg_a')}。",
        "core_issues": [k['name'] for k in analytics.get('keywords', [])[:3]] or ["暂无显著压力源"],
        "action_advices": ["保持规律作息", "尝试进行简单的正念深呼吸"]
    }

    try:
        # 3. 🚀 一行代码调用生成器服务，拿到 PDF 流
        pdf_buffer = build_psychological_pdf_stream(analytics, summary, dates, scores, valences, arousals)
        
        # 4. 返回文件
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Report_{user_id}.pdf'
        )
    except Exception as e:
        print(f"PDF 生成失败: {e}")
        return jsonify({"error": "PDF 生成失败，请检查服务日志"}), 500
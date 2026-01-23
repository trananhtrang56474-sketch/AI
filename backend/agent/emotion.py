# backend/agent/emotion.py
import json
import re
from llm.qwen_client import QwenClient
from models import ChatLog

llm_client = QwenClient()

# ==========================================
# 🔥 核心：心理学维度映射 (Russell 模型变体)
# ==========================================
# Valence (价向): -2(极负) ~ +2(极正)
# Arousal (唤醒): 0(低能) ~ 2(高能/激动)
# Risk    (风险): 0(安全) ~ 2(危机)
EMOTION_MAP = {
    "危机":   {"valence": -2, "arousal": 2, "risk": 2},

    "愤怒":   {"valence": -1, "arousal": 2, "risk": 1},
    "焦虑":   {"valence": -1, "arousal": 2, "risk": 1},
    "恐慌":   {"valence": -1, "arousal": 2, "risk": 1}, # 兼容

    "抑郁":   {"valence": -2, "arousal": 1, "risk": 1},
    "无助":   {"valence": -2, "arousal": 1, "risk": 1},
    "绝望":   {"valence": -2, "arousal": 1, "risk": 1}, # 兼容
    "空虚":   {"valence": -1, "arousal": 0, "risk": 0},

    "自责":   {"valence": -1, "arousal": 1, "risk": 0},
    "愧疚":   {"valence": -1, "arousal": 1, "risk": 0},
    "羞耻":   {"valence": -1, "arousal": 1, "risk": 0},

    "迷茫":   {"valence": -0.5, "arousal": 1, "risk": 0}, # 微调
    "平静":   {"valence":  0, "arousal": 0, "risk": 0},
    
    "积极":   {"valence":  1, "arousal": 1, "risk": 0},
    "希望":   {"valence":  1, "arousal": 1, "risk": 0},
    "开心":   {"valence":  1, "arousal": 2, "risk": 0},
}

def get_vector(tag):
    """辅助函数：获取标签对应的向量"""
    # 模糊匹配：如果标签包含“焦虑”，就用焦虑的向量
    for key in EMOTION_MAP:
        if key in tag:
            return EMOTION_MAP[key]
    return {"valence": 0, "arousal": 0, "risk": 0} # 默认平静

def analyze_emotion(text):
    """
    Step 1: 情绪识别 (依然由 LLM 负责定性，定完性后我们再查表定量)
    """
    # 兜底
    default_result = {"tag": "平静", "score": 60} 

    if not text or len(text) < 2: 
        return default_result
    
    prompt = [
        {"role": "system", "content": """你是一个心理评估专家。请分析用户文本，输出 JSON 格式结果。

### 1. 情绪标签定义 (请严格匹配以下核心词):
[危机, 愤怒, 焦虑, 抑郁, 悲伤, 愧疚, 迷茫, 平静, 积极]

### 2. 输出格式:
{"tag": "标签名"}

注意：只需识别最准确的一个标签即可，数值计算由后台完成。
"""},
        {"role": "user", "content": f"用户文本：{text}"}
    ]
    
    try:
        response = llm_client.chat(prompt, temperature=0.1).strip()
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            tag = result.get("tag", "平静")
            
            # 🔥 计算分数 (兼容前端 ECharts): 将 Valence 映射到 0-100
            # Valence: -2 -> 20, -1 -> 40, 0 -> 60, 1 -> 80, 2 -> 95
            vec = get_vector(tag)
            score_map = {-2: 20, -1.5: 30, -1: 40, -0.5: 50, 0: 60, 1: 85, 2: 95}
            # 简单的线性插值或直接映射
            base_score = score_map.get(vec['valence'], 60)
            
            return {"tag": tag, "score": base_score}
        
        return default_result
    except Exception as e:
        print(f"Emotion Analysis Error: {e}")
        return default_result

def analyze_trend(session_id):
    """
    Step 2: 趋势分析 (基于向量轨迹 + 假性平静识别)
    """
    if not session_id: return "FIRST_CONTACT"

    # 获取最近 5 条记录
    recent_logs = ChatLog.query.filter_by(session_id=session_id, role="user")\
        .order_by(ChatLog.created_at.desc()).limit(5).all()
    
    # 只有 1 条记录，没法看趋势
    if len(recent_logs) < 2: return "FIRST_CONTACT"

    # 1. 数据向量化 (按时间正序排列: [最旧, ..., 最新])
    logs_ordered = recent_logs[::-1] 
    vectors = [get_vector(log.emotion_tag) for log in logs_ordered]
    tags = [log.emotion_tag for log in logs_ordered]

    # 提取维度序列
    v = [vec['valence'] for vec in vectors] # 价向
    r = [vec['risk'] for vec in vectors]    # 风险

    current_tag = tags[-1]
    prev_tag = tags[-2]

    # ==========================
    # 🕵️‍♀️ 核心算法：特征检测
    # ==========================

    # A. 🚨 风险检测 (只要最近有一条是高风险)
    if max(r) >= 2:
        return "CRISIS_RISING"

    # B. 🎭 假性平静 (Emotional Suppression)
    # 逻辑：上一条是高唤醒负面(焦虑/愤怒) 或 深度负面(抑郁)，这一条突然变成“平静”
    # 且 Valence 并没有逐步改善的趋势，而是断崖式变化
    negative_tags = ["焦虑", "愤怒", "抑郁", "无助", "绝望", "危机"]
    if current_tag == "平静" and any(t in prev_tag for t in negative_tags):
        return "EMOTIONAL_SUPPRESSION"

    # C. 📉 恶化 (Valence 均值下降)
    # 比较：(最新2条的平均) - (再前面几条的平均)
    if len(v) >= 3:
        recent_avg = sum(v[-2:]) / 2
        past_avg = sum(v[:-2]) / len(v[:-2])
        if recent_avg < past_avg - 0.5: # 下降超过 0.5 个单位
            return "DETERIORATING"
            
    # D. 📈 改善 (Valence 均值上升)
    if len(v) >= 3:
        recent_avg = sum(v[-2:]) / 2
        past_avg = sum(v[:-2]) / len(v[:-2])
        if recent_avg > past_avg + 0.5:
            return "IMPROVING"

    # E. ⚖️ 持续负面 (一直在低谷)
    if all(val < 0 for val in v[-3:]):
        return "PERSISTENT_NEGATIVE"

    return "STABLE"
# backend/agent/emotion.py
import json
import re
from llm.qwen_client import QwenClient
from models import ChatLog

llm_client = QwenClient()

# ==========================================
# 🔥 核心：心理学维度映射 (仅用于风控拦截)
# ==========================================
# 唤醒度 (Arousal) 和 效价 (Valence) 现在由大模型基于 Russell 环形模型直接输出 1-10 的精确打分。
# 这个字典仅保留基础的情绪标签以及对应的极度风险值(Risk)，用于物理兜底拦截。
EMOTION_MAP = {
    "危机":   {"risk": 2},
    "愤怒":   {"risk": 1},
    "焦虑":   {"risk": 1},
    "恐慌":   {"risk": 1},
    "抑郁":   {"risk": 1},
    "无助":   {"risk": 1},
    "绝望":   {"risk": 1},
    "悲伤":   {"risk": 0},
    "空虚":   {"risk": 0},
    "自责":   {"risk": 0},
    "愧疚":   {"risk": 0},
    "迷茫":   {"risk": 0},
    "平静":   {"risk": 0},
    "放松":   {"risk": 0},
    "积极":   {"risk": 0},
    "开心":   {"risk": 0},
}

def get_risk(tag):
    """辅助函数：获取标签对应的基础风险"""
    for key in EMOTION_MAP:
        if key in tag:
            return EMOTION_MAP[key]["risk"]
    return 0 

def analyze_emotion(text):
    """
    Step 1: 瞬时情绪(Emotion)深度提取 (基于 Russell 的 Circumplex Model of Affect)
    让 LLM 联合评估效价(Valence)和唤醒度(Arousal)并给出 1-10 精准打分。
    该结果代表瞬时状态，随后将由后端的 ALMA 平滑算法转化为长期的心境(Mood)。
    """
    default_result = {"tag": "平静", "valence": 5, "arousal": 3, "score": 50} 

    if not text or len(text) < 2: 
        return default_result
    
    # ✨ 优化：融入临床 CBT 与 Russell 环形模型的专业 Prompt 框架
    prompt = [
        {"role": "system", "content": """你是一个集成认知行为疗法(CBT)原理与 Russell 情感环形模型(Circumplex Model of Affect)的专业心理评估引擎。
请分析用户当前的文本，并在 1 到 10 的量表上独立评估其瞬时状态的 Valence（心理效价）和 Arousal（躯体唤醒度）。

【评分基准参考】：
1. Valence (心理效价：反映认知层面的积极/消极程度):
   - 1-3: 重度负性认知（绝望、极度痛苦、深切悲伤、自我否定、危机）
   - 4-5: 轻度负性认知（疲惫、轻微失落、略感压力、迷茫、无聊）
   - 6:   中性客观（无明显情感偏向的客观陈述、平静）
   - 7-8: 积极认知（开心、放松、温暖、有希望、自我肯定）
   - 9-10: 极度正性认知（狂喜、极度兴奋、巨大的成就感）

2. Arousal (躯体唤醒度：反映生理激活与神经紧张程度):
   - 1-3: 低唤醒/低能量（困倦、躯体沉重、抑郁导致的死寂、彻底放松）
   - 4-6: 中等唤醒（日常交流、轻度思考、情绪平稳）
   - 7-8: 高唤醒/高激活（专注、警觉、焦虑、愤怒、激动）
   - 9-10: 极高唤醒/过载（惊恐发作、失控的狂怒、极度狂喜、应激状态）

请严格输出 JSON 格式：
{
  "tag": "从以下选项中选择最贴切的一个: [危机, 愤怒, 焦虑, 恐慌, 抑郁, 悲伤, 愧疚, 迷茫, 平静, 放松, 积极, 开心]",
  "valence": 介于 1 到 10 之间的整数,
  "arousal": 介于 1 到 10 之间的整数
}

【注意事项】：
1. 必须将心理评估与躯体评估解耦。例如：用户愤怒时，是负效价(低Valence)伴随高激活(高Arousal)；用户抑郁时，是负效价(低Valence)伴随低激活(低Arousal)。
2. 如果检测到自伤、轻生倾向，tag 必须为"危机"，且 valence 必须 <= 2，arousal 通常 >= 8 (极高应激)。
"""},
        {"role": "user", "content": f"用户文本：{text}"}
    ]
    
    try:
        response = llm_client.chat(prompt, temperature=0.1).strip()
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            result = json.loads(match.group())
            tag = result.get("tag", "平静")
            
            # 提取双维度得分并限制在 1-10 之间
            v = max(1, min(10, int(result.get("valence", 5))))
            a = max(1, min(10, int(result.get("arousal", 3))))
            
            # ✨ 核心修复：将 Valence(1-10) 严谨映射为原始分数(0-100)
            # 公式: (V - 1) / 9 * 100
            score = int((v - 1) / 9.0 * 100)
            
            # 返回瞬时 Emotion 坐标与原始分数，供 routes.py 进行长期 Mood 平滑计算
            return {"tag": tag, "score": score, "valence": v, "arousal": a}
        
        return default_result
    except Exception as e:
        print(f"Emotion Analysis Error: {e}")
        return default_result

def analyze_trend(session_id):
    """
    Step 2: 趋势分析 (基于真实分值的移动平均 + 假性平静识别)
    """
    if not session_id: return "FIRST_CONTACT"

    # 获取最近 5 条记录
    recent_logs = ChatLog.query.filter_by(session_id=session_id, role="user")\
        .order_by(ChatLog.created_at.desc()).limit(5).all()
    
    if len(recent_logs) < 2: return "FIRST_CONTACT"

    # 1. 数据按时间正序排列: [最旧, ..., 最新]
    logs_ordered = recent_logs[::-1] 
    tags = [log.emotion_tag or "平静" for log in logs_ordered]
    scores = [log.emotion_score if log.emotion_score is not None else 60 for log in logs_ordered]

    current_tag = tags[-1]
    current_score = scores[-1]
    prev_score = scores[-2]

    # 获取风险值
    risks = [get_risk(t) for t in tags]

    # ==========================
    # 🕵️‍♀️ 核心算法：数学特征与心理学模式检测
    # ==========================

    # A. 🚨 风险上升 (只要最近有高风险标签 或者 效价分数极低)
    if max(risks[-2:]) >= 2 or current_score <= 20:
        return "CRISIS_RISING"

    # B. 🎭 假性平静 (Emotional Suppression)
    # 心理学逻辑：前一刻处于极度痛苦（<35分），下一刻突然表示“平静”（分数瞬间回到60左右）
    if current_tag == "平静" and prev_score < 35 and current_score >= 55:
        return "EMOTIONAL_SUPPRESSION"

    # 准备移动平均数计算
    if len(scores) >= 3:
        recent_avg = sum(scores[-2:]) / 2.0
        past_avg = sum(scores[:-2]) / len(scores[:-2])
        
        # C. 📉 恶化 (均值显著下降超 15 分)
        if recent_avg < past_avg - 15:
            return "DETERIORATING"
            
        # D. 📈 改善 (均值显著上升超 15 分)
        if recent_avg > past_avg + 15:
            return "IMPROVING"

    # E. ⚖️ 持续负面 (连续 3 次分数低于 45，陷入低谷)
    if len(scores) >= 3 and all(s < 45 for s in scores[-3:]):
        return "PERSISTENT_NEGATIVE"

    # F. 🌟 积极向上 (连续 2 次分数高于 75)
    if len(scores) >= 2 and all(s > 75 for s in scores[-2:]):
        return "HIGHLY_POSITIVE"

    return "STABLE"
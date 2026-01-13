# backend/agent/emotion.py
from llm.qwen_client import QwenClient
from models import ChatLog

llm_client = QwenClient()

def analyze_emotion(text):
    """
    Step 1: 情绪识别 (9类中文标签版)
    """
    if not text or len(text) < 2: return "平静"
    
    prompt = [
        {"role": "system", "content": """你是一个心理学情绪分类器。请分析文本，只输出以下【中文标签】之一：

1. 危机 (包含自伤、自杀计划、正在实施危险行为、极度失控)
2. 愤怒 (包含烦躁、敌意、攻击性、被冒犯、怨恨)
3. 焦虑 (包含担忧、恐慌、紧张、害怕未来、不知所措)
4. 抑郁 (包含无助、绝望、低落、无意义感、自我厌恶)
5. 悲伤 (包含哀伤、失去亲友/物品、失恋、难过、哭泣)
6. 愧疚 (包含自责、羞耻、后悔、觉得对不起别人)
7. 迷茫 (包含纠结、犹豫、选择困难、缺乏方向感)
8. 积极 (包含开心、自豪、感激、兴奋、充满希望)
9. 平静 (包含一般陈述、理性询问、闲聊、无明显情绪起伏)

注意：
1. 涉及生死的必须输出 '危机'。
2. 如果兼有多种情绪，输出最强烈的一种。
3. 严禁输出解释，只输出一个中文词。"""},
        {"role": "user", "content": f"用户文本：{text}"}
    ]
    
    try:
        tag = llm_client.chat(prompt, temperature=0.1).strip()
        # 清洗结果，确保在列表内
        valid_tags = ['危机', '愤怒', '焦虑', '抑郁', '悲伤', '愧疚', '迷茫', '积极', '平静']
        for t in valid_tags:
            if t in tag: return t
        return "平静"
    except:
        return "平静"

def analyze_trend(session_id):
    """
    Step 1.5: 情绪趋势分析 (适配9类中文标签)
    """
    if not session_id: return "FIRST_CONTACT"

    recent_logs = ChatLog.query.filter_by(session_id=session_id, role="user")\
        .order_by(ChatLog.created_at.desc()).limit(3).all()
    
    if not recent_logs: return "FIRST_CONTACT"

    # 提取标签
    past_emotions = [log.emotion_tag for log in recent_logs if log.emotion_tag]
    current_emotion = past_emotions[0] if past_emotions else "平静"
    
    # 1. 🚨 危机持续
    if current_emotion == '危机': return "CRISIS_ALERT"
    
    # 定义负面情绪集合 (兼容旧英文)
    negative_set = {
        '抑郁', '焦虑', '痛苦', '愤怒', '悲伤', '愧疚', '迷茫', '危机',
        'depression', 'anxiety', 'anger', 'distress', 'crisis'
    }
    
    # 定义非负面状态 (积极 + 平静)
    positive_or_neutral = {'平静', '积极', 'neutral'}

    # 2. 📉 持续负面 (检测最近2次)
    if len(past_emotions) >= 2:
        if all(e in negative_set for e in past_emotions[:2]):
            return "PERSISTENT_NEGATIVE"
    
    # 3. 📉 恶化 (平静/积极 -> 负面)
    if len(past_emotions) >= 2:
        prev = past_emotions[1]
        curr = past_emotions[0]
        if (prev in positive_or_neutral) and (curr in negative_set):
            return "WORSENING"
            
    # 4. 📈 改善 (负面 -> 平静/积极)
    if len(past_emotions) >= 2:
        prev = past_emotions[1]
        curr = past_emotions[0]
        if (prev in negative_set) and (curr in positive_or_neutral):
            return "IMPROVING"

    return "FLUCTUATING"
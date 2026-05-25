# backend/agent/emotion.py
import json
import re
import os      # ✨ 新增：必须引入 os 模块来处理文件路径
import base64  # ✨ 确保顶部引入 base64
from llm.qwen_client import QwenClient
from models.chat import ChatLog
from database import SessionLocal  # ✨ 新增：引入 FastAPI 的数据库会话工厂

# 👇========= 新增：LangChain 多模态依赖 =========👇
from config import Config
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage

# ✨ 初始化专门处理图片的视觉大模型 (Vision-Language Model)
vision_llm = ChatTongyi(
    model_name="qwen-vl-max", 
    dashscope_api_key=Config.DASHSCOPE_API_KEY
)
# 👆========= 新增完毕 =========👆

llm_client = QwenClient()

# ==========================================
# 🔥 核心：心理学维度映射 (仅用于风控拦截)
# ==========================================
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
    Step 1: 瞬时情绪(Emotion)深度提取
    """
    default_result = {"tag": "平静", "valence": 5, "arousal": 3, "score": 50} 

    if not text or len(text) < 2: 
        return default_result
    
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
            
            v = max(1, min(10, int(result.get("valence", 5))))
            a = max(1, min(10, int(result.get("arousal", 3))))
            
            score = int((v - 1) / 9.0 * 100)
            
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

    # ✨ 核心修复：使用 FastAPI 的局部 Session 来执行查询
    db = SessionLocal()
    try:
        recent_logs = db.query(ChatLog).filter_by(session_id=session_id, role="user")\
            .order_by(ChatLog.created_at.desc()).limit(5).all()
    except Exception as e:
        print(f"⚠️ 数据库查询失败: {e}")
        return "STABLE"
    finally:
        # 确保查询完毕后释放连接
        db.close()
    
    if len(recent_logs) < 2: return "FIRST_CONTACT"

    logs_ordered = recent_logs[::-1] 
    tags = [log.emotion_tag or "平静" for log in logs_ordered]
    scores = [log.emotion_score if log.emotion_score is not None else 60 for log in logs_ordered]

    current_tag = tags[-1]
    current_score = scores[-1]
    prev_score = scores[-2]

    risks = [get_risk(t) for t in tags]

    if max(risks[-2:]) >= 2 or current_score <= 20:
        return "CRISIS_RISING"

    if current_tag == "平静" and prev_score < 35 and current_score >= 55:
        return "EMOTIONAL_SUPPRESSION"

    if len(scores) >= 3:
        recent_avg = sum(scores[-2:]) / 2.0
        past_avg = sum(scores[:-2]) / len(scores[:-2])
        
        if recent_avg < past_avg - 15:
            return "DETERIORATING"
            
        if recent_avg > past_avg + 15:
            return "IMPROVING"

    if len(scores) >= 3 and all(s < 45 for s in scores[-3:]):
        return "PERSISTENT_NEGATIVE"

    if len(scores) >= 2 and all(s > 75 for s in scores[-2:]):
        return "HIGHLY_POSITIVE"

    return "STABLE"

# 👇========= 新增：图像处理函数 =========👇
def analyze_image(image_url):
    """
    Step 3: 使用 LangChain 多模态模型分析图片 (修复 DashScope 协议格式版)
    """
    try:
        # 1. 解析物理路径并转为 Base64 
        filename = image_url.split('/')[-1]
        # 修正路径：如果 emotion.py 在 agent 文件夹，上跳一级是 backend
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(os.path.dirname(current_dir), 'uploads', filename)
        
        print(f" 正在解析本地图片文件: {local_path}")

        with open(local_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')

        # 2. 构造符合 DashScope VL 模型预期的消息体 ✨
        message = HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": "请描述这张图片，并判断从中传递出的情绪氛围。请严格返回JSON格式：{\"caption\": \"图片描述\", \"valence\": 1到10的整数, \"arousal\": 1到10的整数}"
                },
                {
                    "type": "image",  # ✨ 注意：DashScope VL 协议中这里必须是 "image" 而非 "image_url"
                    "image": f"data:image/png;base64,{base64_image}" # ✨ 键名也必须是 "image"
                }
            ]
        )

       # 3. 发起请求
        response = vision_llm.invoke([message])
        
        # ✨ 核心修复：处理 DashScope 多模态特有的返回格式
        # 有时返回的是字符串，有时是 [{'text': '...'}]
        if isinstance(response.content, list):
            response_text = response.content[0].get('text', '')
        else:
            response_text = response.content

        print(f" AI 视觉原始文本: {response_text}")

        # 解析 JSON (增加对 Markdown 代码块的兼容)
        # 清洗掉可能存在的 ```json 和 ``` 标记
        clean_text = re.sub(r'```json\s*|```', '', response_text).strip()
        
        match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "caption": result.get("caption", "图片内容"),
                "valence": max(1, min(10, int(result.get("valence", 5)))),
                "arousal": max(1, min(10, int(result.get("arousal", 5))))
            }
        
        # 兜底：如果 JSON 解析还是失败，尝试直接提取文字
        return {"caption": response_text[:50], "valence": 5, "arousal": 5}

    except Exception as e:
        print("❌ 图像分析失败:", e)
        return {"caption": "图片解析失败", "valence": 5, "arousal": 3}
# 👆========= 新增完毕 =========👆
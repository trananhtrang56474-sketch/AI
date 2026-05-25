import json
import re
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage
from config import Config

# ✨ 初始化专门处理图片的视觉大模型 (Vision-Language Model)
# 注意：通义千问处理图片的模型名字必须带 '-vl-'，比如 'qwen-vl-max' 或 'qwen-vl-plus'
vision_llm = ChatTongyi(
    model_name="qwen-vl-max", 
    dashscope_api_key=Config.DASHSCOPE_API_KEY
)

def analyze_image(image_url):
    """
    使用 LangChain 多模态模型分析图片
    返回：caption + 情绪坐标
    """
    try:
        print(f" 正在使用 qwen-vl-max 分析图片: {image_url}")
        
        # ✨ LangChain 官方支持的多模态消息体格式
        message = HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": "请描述这张图片，并判断从中传递出的情绪氛围。请严格返回JSON格式：{\"caption\": \"图片描述\", \"valence\": 1到10的整数, \"arousal\": 1到10的整数}"
                },
                {
                    "type": "image_url", 
                    "image_url": {"url": image_url}
                }
            ]
        )

        # 发起调用
        response_text = vision_llm.invoke([message]).content

        # 解析模型返回的 JSON
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return {
                "caption": result.get("caption", "收到一张图片"),
                "valence": max(1, min(10, int(result.get("valence", 5)))),
                "arousal": max(1, min(10, int(result.get("arousal", 5))))
            }
            
        # 如果模型没有按 JSON 格式返回，兜底处理
        return {
            "caption": response_text[:50] + "...", 
            "valence": 5, 
            "arousal": 5
        }

    except Exception as e:
        print("❌ 图像分析失败:", e)
        return {
            "caption": "图片解析失败",
            "valence": 5,
            "arousal": 3
        }
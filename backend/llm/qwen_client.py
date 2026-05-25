import os
import json
import base64
import requests

class QwenClient:
    def __init__(self):
        # ⚠️ 请确保这里填入了真实的 API KEY
        self.api_key = "sk-56307adfa2e44424a95148cab9830edc" 
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def _encode_image(self, image_path):
        """辅助函数：将本地图片转换为 Base64"""
        if not os.path.exists(image_path):
            return None
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def chat(self, messages, temperature=0.7, image_path=None):
        """
        :param messages: 聊天上下文
        :param temperature: 随机度
        :param image_path: 本地图片的绝对路径 (如果有图，传这个)
        :return: AI 回复
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # ==========================================
        # 🅰️ 模式一：多模态 (有图) -> 使用 qwen-vl-max
        # ==========================================
        if image_path:
            print(f" 启动视觉模式，正在处理图片: {image_path}")
            
            # 1. 把图片转 Base64
            base64_img = self._encode_image(image_path)
            if not base64_img:
                return "（系统错误：无法读取上传的图片文件）"

            # 2. 构造 VL 模型专用的消息格式
            # Qwen-VL 要求 user 内容为列表：[{type: text, ...}, {type: image_url, ...}]
            
            # 提取最后一条用户文字消息
            user_text = "请描述这张图片"
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    user_text = msg['content']
                    break
            
            # 构造多模态 payload
            vl_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}},
                        {"type": "text", "text": user_text}
                    ]
                }
            ]

            # 加上之前的历史记录（如果需要的话，目前 VL 对历史记录支持有限，这里为了稳妥只发单轮或简化历史）
            # 为了效果最好，我们把 System Prompt 拼接到 text 里
            system_prompt = ""
            if messages[0]['role'] == 'system':
                system_prompt = f"【系统指令】{messages[0]['content']}\n\n"
            
            vl_messages[0]['content'][1]['text'] = system_prompt + user_text

            payload = {
                "model": "qwen-vl-max", # 
                "messages": vl_messages,
                "temperature": temperature
            }

        # ==========================================
        # 🅱️ 模式二：纯文本 (无图) -> 使用 qwen-plus
        # ==========================================
        else:
            payload = {
                "model": "qwen-plus", # 
                "messages": messages,
                "max_tokens": 1500,
                "temperature": temperature
            }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    print("API 返回异常:", data)
                    return "（AI 似乎走神了，请重试）"
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return f"（服务暂时不可用: {response.status_code}）"

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return "（网络连接超时，请检查网络）"
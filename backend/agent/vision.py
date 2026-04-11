def analyze_image(image_url, llm_client):
    """
    使用多模态模型分析图片
    返回：caption + 情绪坐标
    """
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请描述这张图片，并判断其中的情绪（返回 valence 1-10 和 arousal 1-10）"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        result = llm_client.chat(messages)

        # 👉 简单解析（你可以后面优化成 JSON 输出）
        return {
            "caption": result,
            "valence": 5,
            "arousal": 5
        }

    except Exception as e:
        print("❌ 图像分析失败:", e)
        return {
            "caption": "图片",
            "valence": 5,
            "arousal": 3
        }
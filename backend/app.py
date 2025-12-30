import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = "sk-56307adfa2e44424a95148cab9830edc"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 用于存储每个会话的上下文，key 为 session_id
chat_sessions = {}

@app.route("/api/chat", methods=["POST"])
def chat_handler():
    data = request.json
    user_message = data.get("message")
    session_id = data.get("session_id", "default")  # 默认会话

    if not user_message:
        return jsonify({"error": "Message 字段是必须的。"}), 400

    # 获取当前会话的消息列表，如果不存在则创建
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    # 将用户消息加入会话上下文
    chat_sessions[session_id].append({"role": "user", "content": user_message})

    # 构建 payload，发送整个会话上下文给 API
    payload = {
        "model": "qwen-plus",  # 或者你账号可用的模型
        "messages": chat_sessions[session_id],
        "max_tokens": 1000,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # 解析 AI 回复
        ai_reply = ""
        if "choices" in response_data:
            ai_reply = response_data["choices"][0].get("message", {}).get("content", "")
        elif "result" in response_data:
            ai_reply = response_data["result"]

        if not ai_reply:
            ai_reply = "[AI 未返回内容，请检查模型或 Key 是否可用]"

        # 将 AI 回复加入上下文
        chat_sessions[session_id].append({"role": "assistant", "content": ai_reply})

        return jsonify({"reply": ai_reply})

    except requests.exceptions.RequestException as e:
        print(f"调用通义千问 API 时发生错误: {e}")
        return jsonify({"error": "调用 AI API 失败"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

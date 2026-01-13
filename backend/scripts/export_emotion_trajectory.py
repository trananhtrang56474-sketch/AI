# backend/scripts/export_emotion_trajectory.py
import sys
import os
import matplotlib.pyplot as plt

# 添加父目录到路径，以便导入 app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db, ChatLog

def plot_trajectory(session_id):
    with app.app_context():
        # 1. 查询该会话的所有用户消息
        logs = ChatLog.query.filter_by(session_id=session_id, role="user")\
            .order_by(ChatLog.created_at.asc()).all()
        
        if not logs:
            print("没有找到对话记录")
            return

        # 2. 映射情绪到数值 (为了画图)
        # 负面情绪分低，中性居中，改善/平静分高（这里只是为了可视化趋势）
        emotion_map = {
            'crisis': 0,
            'depression': 1,
            'distress': 2,
            'anxiety': 3,
            'anger': 4,
            'neutral': 5,
            # 'positive': 6 # 如果您未来想加回 positive
        }
        
        y_values = []
        x_labels = []
        tags = []

        for i, log in enumerate(logs):
            tag = log.emotion_tag or 'neutral'
            y = emotion_map.get(tag, 5)
            y_values.append(y)
            x_labels.append(f"Turn {i+1}")
            tags.append(tag)
            print(f"第 {i+1} 轮: {log.content[:10]}... -> [{tag}]")

        # 3. 画图
        plt.figure(figsize=(10, 6))
        plt.plot(x_labels, y_values, marker='o', linestyle='-', color='b')
        plt.yticks(list(emotion_map.values()), list(emotion_map.keys()))
        plt.title(f"Emotion Trajectory for Session {session_id}")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 保存图片
        save_path = f"session_{session_id}_trajectory.png"
        plt.savefig(save_path)
        print(f"✅ 情绪轨迹图已保存: {save_path}")

if __name__ == "__main__":
    # 在这里填入您想分析的 session_id (可以在数据库里查，或者 API 返回里看)
    target_session_id = 1 
    plot_trajectory(target_session_id)
import json
import os

class KnowledgeLoader:
    def __init__(self, filepath='data/cbt_knowledge.json'):
        # 自动定位到 backend/data 目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = os.path.join(base_dir, filepath)

    def load(self):
        if not os.path.exists(self.path):
            print(f"⚠️ 文件不存在: {self.path}")
            return []
        
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)
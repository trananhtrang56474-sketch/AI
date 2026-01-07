import requests
from config import Config

class DashScopeEmbedder:
    def __init__(self):
        self.api_key = Config.DASHSCOPE_API_KEY
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    def get_embeddings(self, texts):
        """批量获取向量"""
        try:
            resp = requests.post(
                self.url,
                json={"model": "text-embedding-v1", "input": texts},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            if resp.status_code == 200:
                return [item['embedding'] for item in resp.json()['data']]
        except Exception as e:
            print(f"❌ Embedding Error: {e}")
        return []

    def get_single_embedding(self, text):
        res = self.get_embeddings([text])
        return res[0] if res else None
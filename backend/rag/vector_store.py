import numpy as np

class SimpleVectorStore:
    def __init__(self):
        self.vectors = []
        self.documents = [] # 存对应的 JSON 对象

    def add_documents(self, docs, embeddings):
        """存入文档和向量"""
        self.documents = docs
        self.vectors = np.array(embeddings)

    def search(self, query_vec, top_k=1):
        """余弦相似度检索"""
        if len(self.vectors) == 0: return None

        query_vec = np.array(query_vec)
        
        # 计算相似度 (A . B) / (|A| * |B|)
        dot_products = np.dot(self.vectors, query_vec)
        doc_norms = np.linalg.norm(self.vectors, axis=1)
        query_norm = np.linalg.norm(query_vec)
        
        similarities = dot_products / (doc_norms * query_norm)
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        print(f"🔍 RAG 检索得分: {best_score:.4f}")
        
        if best_score < 0.35: return None # 阈值
        return self.documents[best_idx]
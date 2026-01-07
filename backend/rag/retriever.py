from .embedder import DashScopeEmbedder
from .knowledge_loader import KnowledgeLoader
from .vector_store import SimpleVectorStore

class RAGRetriever:
    def __init__(self):
        print("🔧 初始化 RAG 引擎...")
        self.embedder = DashScopeEmbedder()
        self.store = SimpleVectorStore()
        
        # 初始化时自动加载数据
        loader = KnowledgeLoader()
        data = loader.load()
        if data:
            print(f"📚 加载 {len(data)} 条知识，正在向量化...")
            # 拼接 title + content 用于检索
            texts = [f"{item['title']}\n{item['content']}" for item in data]
            embeddings = self.embedder.get_embeddings(texts)
            self.store.add_documents(data, embeddings)
            print("✅ RAG 引擎就绪！")

    def search(self, query):
        """对外暴露的搜索接口"""
        query_vec = self.embedder.get_single_embedding(query)
        if not query_vec: return None
        return self.store.search(query_vec)

# 单例模式
rag_engine = RAGRetriever()
import os
import chromadb
from chromadb.utils import embedding_functions

class RAGRetriever:
    def __init__(self):
        # 1. 自动定位到 backend/chroma_db 文件夹
        # __file__ 是 backend/rag/retriever.py
        # os.path.dirname(__file__) 是 backend/rag
        # 再上一级是 backend，然后拼上 chroma_db
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.persist_dir = os.path.join(base_dir, 'chroma_db')
        
        print(f"🔧 正在连接向量数据库: {self.persist_dir}")
        
        # 初始化客户端
        # settings=chromadb.config.Settings(anonymized_telemetry=False) 可选
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # 2. 必须使用和 build_knowledge.py 一样的 Embedding 模型
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # 3. 获取集合
        try:
            self.collection = self.client.get_collection(
                name="cbt_knowledge_base",
                embedding_function=self.emb_fn
            )
            count = self.collection.count()
            print(f"✅ RAG 引擎就绪，当前知识库载入条目数: {count}")
        except Exception as e:
            print(f"❌ 无法加载知识库 (请先运行 build_knowledge.py): {e}")
            self.collection = None

    def search(self, query, top_k=3):
        """
        语义检索接口
        """
        if not self.collection:
            return None

        print(f"🔍 RAG 检索中: {query}")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # 检查是否有结果
            if not results['documents'] or not results['documents'][0]:
                return None

            # 提取最佳匹配 (第一个结果)
            best_doc = results['documents'][0][0]
            best_meta = results['metadatas'][0][0]
            
            # 组装返回格式，兼容 app.py 的逻辑
            knowledge = {
                "content": best_doc,
                "stage": best_meta.get('stage', 'CBT干预'),
                "source": best_meta.get('source', 'unknown'),
                # 如果 metadata 里没有 response_strategy，就用内容本身
                "response_strategy": best_meta.get('response', f"参考知识点：{best_doc}")
            }
            
            print(f"🎯 RAG 命中: [{knowledge['stage']}] {knowledge['content'][:20]}...")
            return knowledge

        except Exception as e:
            print(f"❌ 检索异常: {e}")
            return None

# 单例模式，供 app.py 引用
rag_engine = RAGRetriever()
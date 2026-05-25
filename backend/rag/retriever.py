import os
import chromadb
from chromadb.utils import embedding_functions

class RAGRetriever:
    def __init__(self):
        # 1. 自动定位到 backend/chroma_db 文件夹
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.persist_dir = os.path.join(base_dir, 'chroma_db')
        
        print(f" 正在连接向量数据库: {self.persist_dir}")
        
        # 初始化客户端
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
            print(f" RAG 引擎就绪，当前知识库载入条目数: {count}")
        except Exception as e:
            print(f" 无法加载知识库 (请先运行 build_knowledge.py): {e}")
            self.collection = None

    def search(self, query, top_k=3):
        """
        语义检索接口（支持动态阈值阻断）
        """
        if not self.collection:
            return None

        print(f"\n RAG 检索中: {query}")
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # 检查是否有结果
            if not results['documents'] or not results['documents'][0]:
                return None

            # 核心升级：基于距离（Distance）的动态阈值阻断机制
            # ChromaDB 默认返回 L2 距离（数值越小，语义越相近）
            distances = results.get('distances')
            if distances and len(distances[0]) > 0:
                best_distance = distances[0][0]
                print(f" RAG 检索距离得分 (L2 Distance): {best_distance:.4f}")
                
                # 如果距离 > 0.45，说明向量空间中两者相距甚远，属于无关闲聊
                if best_distance > 0.45:
                    print(" 匹配度过低，判定为日常闲聊，主动阻断 RAG 知识注入。")
                    return None

            # 如果通过了阈值校验，提取最佳匹配 (第一个结果)
            best_doc = results['documents'][0][0]
            best_meta = results['metadatas'][0][0]
            
            # 组装返回格式，完美兼容 routes.py 里的 prompt_builder
            knowledge = {
                "content": best_doc,
                "stage": best_meta.get('stage', 'CBT干预'),
                "source": best_meta.get('source', 'unknown'),
                "response_strategy": best_meta.get('response', f"参考理论：{best_doc}")
            }
            
            print(f"RAG 命中成功: [{knowledge['stage']}] {knowledge['content'][:30]}...")
            return knowledge

        except Exception as e:
            print(f" 检索异常: {e}")
            return None

# 单例模式，供 routes.py 引用
rag_engine = RAGRetriever()
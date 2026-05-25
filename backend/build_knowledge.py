import os
import json
import chromadb
from chromadb.utils import embedding_functions

# =================配置区域=================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 🔥 新的数据根目录
DATA_ROOT = os.path.join(BASE_DIR, 'data') 
# 向量数据库路径
PERSIST_DIRECTORY = os.path.join(BASE_DIR, 'chroma_db')

def build_vector_db():
    print(" 开始构建全量知识库...")
    
    # 1. 初始化 ChromaDB
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    # 2. 重置集合
    collection_name = "cbt_knowledge_base"
    try:
        client.delete_collection(name=collection_name)
    except: pass
    
    collection = client.create_collection(name=collection_name, embedding_function=emb_fn)

    documents = []
    metadatas = []
    ids = []
    
    count = 0

    # ==========================================
    # 核心逻辑：递归遍历 knowledge 文件夹
    # ==========================================
    knowledge_dir = os.path.join(DATA_ROOT, 'knowledge')
    
    if not os.path.exists(knowledge_dir):
        print(f" 错误：找不到 {knowledge_dir}，请先运行 setup_data_structure.py")
        return

    # os.walk 会像爬虫一样遍历所有子目录
    for root, dirs, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith(".txt") or file.endswith(".md"):
                file_path = os.path.join(root, file)
                
                # 获取分类名 (例如 cbt, empathy)
                # relpath 会得到 "cbt" 或 "dsm_symptom"
                category = os.path.relpath(root, knowledge_dir)
                if category == ".": category = "general"

                print(f" 处理: [{category}] {file} ...")

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        # --- 智能切片策略 ---
                        chunk_size = 300
                        overlap = 50 
                        
                        for i in range(0, len(text), chunk_size - overlap):
                            chunk = text[i:i+chunk_size]
                            if len(chunk) < 50: continue # 太短的不要
                            
                            documents.append(chunk)
                            metadatas.append({
                                "source": file,
                                "category": category, # 自动打上的分类标签
                                "stage": "knowledge_retrieval",
                                "response": f"根据{category}领域的专业知识：{chunk[:20]}..."
                            })
                            ids.append(f"{category}_{file}_{i}")
                            count += 1
                except Exception as e:
                    print(f"读取文件失败 {file}: {e}")

    # ==========================================
    # 补充：也加载 Scales (量表) 的描述信息
    # 
    # ==========================================
    scales_dir = os.path.join(DATA_ROOT, 'scales')
    if os.path.exists(scales_dir):
        for file in os.listdir(scales_dir):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(scales_dir, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 把 JSON 里的 name, description 变成向量
                        desc = f"【心理量表】{data.get('name')} - {data.get('description')}。注意：{data.get('notice')}"
                        documents.append(desc)
                        metadatas.append({
                            "source": file,
                            "category": "scales",
                            "stage": "assessment",
                            "response": "我可以为您提供这个量表进行自测。"
                        })
                        ids.append(f"scale_{file}")
                        count += 1
                        print(f" 加载量表定义: {file}")
                except: pass

    # 3. 写入数据库
    if documents:
        print(f" 正在写入 {len(documents)} 条数据 (来源: DSM-5, CBT, 量表库)...")
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            collection.add(
                documents=documents[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
        print(" 知识库构建完成！")
        print(f" 数据结构已更新至: {DATA_ROOT}")
    else:
        print("❌ 没有找到有效数据，请检查 txt 文件内容！")

if __name__ == "__main__":
    build_vector_db()
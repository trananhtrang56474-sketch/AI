import json
import os

# ================= 配置路径 =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, 'backend', 'data', 'raw')
OUTPUT_DIR = os.path.join(BASE_DIR, 'backend', 'data', 'knowledge', 'dialogue_corpus')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ================= 1. 处理 PsyQA (保持不变，因为已经成功) =================
def process_psyqa():
    input_path = os.path.join(RAW_DIR, 'psyqa.json')
    output_path = os.path.join(OUTPUT_DIR, 'psyqa_cleaned.txt')
    
    if not os.path.exists(input_path): return

    print(f"⏳ 正在处理 PsyQA 数据...")
    cleaned_data = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            f.seek(0)
            if first_char == '[':
                data = json.load(f)
            else:
                data = [json.loads(line) for line in f if line.strip()]

        count = 0
        for item in data:
            question = item.get('question') or item.get('question_text') or item.get('title') or ''
            desc = item.get('description') or item.get('desc') or ''
            answers = item.get('answers') or item.get('reply') or []
            if isinstance(answers, str): answers = [{'content': answers}]
            
            for ans in answers:
                content = ans.get('content') or ans.get('answer_text') or '' if isinstance(ans, dict) else str(ans)
                if len(content) > 30 and '楼主' not in content:
                    entry = f"【心理咨询案例】\n用户困扰：{question} {desc}\n专业解答：{content}"
                    cleaned_data.append(entry)
                    count += 1
            if count >= 3000: break

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(cleaned_data))
        print(f"✅ PsyQA 处理完成！已提取 {len(cleaned_data)} 条 -> {output_path}")

    except Exception as e:
        print(f"❌ 处理 PsyQA 出错: {e}")

# ================= 2. 处理 SoulChat (V3 修复版) =================
def process_soulchat():
    input_path = os.path.join(RAW_DIR, 'soulchat.json')
    output_path = os.path.join(OUTPUT_DIR, 'soulchat_cleaned.txt')
    
    if not os.path.exists(input_path):
        print(f"⚠️ 未找到 SoulChat 文件: {input_path}")
        return

    print(f"⏳ 正在处理 SoulChat 数据 (V3版)...")
    cleaned_data = []
    
    # 调试用：记录遇到的所有角色名
    seen_roles = set()
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            # 兼容多种列表名
            dialogue = item.get('messages') or item.get('dialogue') or item.get('conversation') or []
            
            if not dialogue: continue

            conversation_text = "【真实咨询对话片段】\n"
            has_counselor = False
            
            for turn in dialogue:
                role_raw = turn.get('role', '')
                content = turn.get('content') or turn.get('text') or ''
                
                # 记录角色名以便调试
                seen_roles.add(str(role_raw))
                
                # 统一转换为小写并去除空格
                role = str(role_raw).lower().strip()
                
                # === 核心逻辑：智能角色识别 ===
                # 1. 识别用户
                if role in ['client', 'user', 'patient', '来访者', 'inquirer']:
                    role_cn = "来访者"
                
                # 2. 识别咨询师 (增加更多变体)
                elif role in ['counselor', 'doctor', 'therapist', 'system', '咨询师', 'assistant', 'supporter', 'psychologist', 'sys']:
                    role_cn = "咨询师"
                    has_counselor = True
                
                # 3. 兜底策略：只要不是用户，就假定是咨询师 (防止漏掉奇怪的角色名)
                else:
                    role_cn = "咨询师" 
                    has_counselor = True

                conversation_text += f"{role_cn}：{content}\n"
            
            # 只有当对话里确实包含了我们要学习的“咨询师”回复时，才保存
            if has_counselor:
                cleaned_data.append(conversation_text)
                count += 1
            
            if count >= 3000: break

        if count == 0:
            print("❌ SoulChat 依然提取失败！")
            print(f"🔍 调试信息 - 数据中出现过的所有角色名 (Roles): {seen_roles}")
            print("请把上面这一行 'Roles' 发给我，我马上就能修好！")
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(cleaned_data))
            print(f"✅ SoulChat 处理完成！已提取 {len(cleaned_data)} 条 -> {output_path}")

    except Exception as e:
        print(f"❌ 处理 SoulChat 出错: {e}")

if __name__ == "__main__":
    process_psyqa()
    process_soulchat()
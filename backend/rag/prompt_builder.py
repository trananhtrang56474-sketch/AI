import os

class PromptBuilder:
    def __init__(self):
        # 1. 自动定位 prompt 模板目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompt_dir = os.path.join(base_dir, 'data', 'prompts')
        
        # 2. 预加载所有模板到内存 (加载 4 个独立文件)
        print(f"🔧 正在加载 Prompt 模板: {self.prompt_dir}")
        self.templates = {
            'base': self._load_file('base_prompt.txt', "你是一个专业的心理咨询师，富有同理心，请用温暖的语气对话。"),
            'cot': self._load_file('cot_structure.txt', ""),
            'emotion': self._load_file('emotion_constraint.txt', ""),
            'cbt': self._load_file('cbt_prompt.txt', "")
        }

    def _load_file(self, filename, default_text=""):
        """辅助函数：安全读取文件内容"""
        path = os.path.join(self.prompt_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"⚠️ 警告: 无法加载模板 {filename} - {e}")
            return default_text

    def build(self, knowledge_item=None):
        """
        核心方法：动态组装并返回纯文本字符串 (String)。
        完全适配 routes.py 的字符串拼接需求。
        """
        
        # --- 1. 危机干预阻断 (第二重“软熔断”机制) ---
        if knowledge_item and knowledge_item.get('category') == 'safety':
            return (
                "【系统警告：触发危机干预模式】\n"
                "用户当前存在高风险情绪（自杀/自伤/暴力）。请严格遵守以下指令：\n"
                "1. 立即停止任何认知辩论或说教。\n"
                "2. 表达无条件的接纳和深切的关怀。\n"
                "3. 引导用户寻求专业帮助，建议拨打热线: 400-161-9995 或报警 110。"
            )

        # --- 2. 注入专业知识 (RAG Context) 的静态解析 ---
        rag_string = "暂无特定匹配的背景知识，请基于你的专业临床经验自然回复。"
        if knowledge_item:
            content = knowledge_item.get('content', '')
            stage = knowledge_item.get('stage', '通用支持')
            strategy = knowledge_item.get('response_strategy', '')
            
            rag_string = f"当前参考理论阶段：{stage}\n医学与理论依据：{content}\n"
            if strategy:
                rag_string += f"系统建议干预策略：{strategy}\n"

       
        master_template = f"""{self.templates['base']}

【CBT 基础规范】
{self.templates['cbt']}

【当前情绪约束 (E-SCBA)】
{self.templates['emotion']}

【参考专业知识 (RAG)】
{rag_string}

【强制思维链与输出结构 (CoT)】
{self.templates['cot']}
"""
        
        # --- 4. 直接返回纯文本 ---
        return master_template

# 实例化单例，供路由文件 (routes.py) 导入使用
prompt_engine = PromptBuilder()
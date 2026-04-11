import os
import json

class PromptBuilder:
    def __init__(self):
        # 1. 自动定位 prompt 模板目录
        # 当前文件: backend/rag/prompt_builder.py
        # 目标目录: backend/data/prompts
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.prompt_dir = os.path.join(base_dir, 'data', 'prompts')
        
        # 2. 预加载所有模板到内存 (避免每次请求都读硬盘)
        print(f"🔧 正在加载 Prompt 模板: {self.prompt_dir}")
        self.templates = {
            'base': self._load_file('base_prompt.txt'),
            'cot': self._load_file('cot_structure.txt'),
            'emotion': self._load_file('emotion_constraint.txt'),
            'cbt': self._load_file('cbt_prompt.txt')
        }

    def _load_file(self, filename):
        """辅助函数：安全读取文件内容"""
        path = os.path.join(self.prompt_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"⚠️ 警告: 无法加载模板 {filename} - {e}")
            return ""

    def build(self, knowledge_item):
        """
        核心方法：动态组装 System Prompt
        顺序：人设 -> 危机阻断 -> 专业知识(RAG) -> 约束条件(E-SCBA) -> 输出格式(CoT)
        """
        
        # --- 1. 基础人设 (Persona) ---
        # 如果文件为空，使用默认兜底
        system_prompt = self.templates['base'] or "你是一个专业的心理咨询师，富有同理心，请用温暖的语气对话。"

        # --- 2. 危机干预阻断 (Safety Layer) ---
        # 如果 RAG 检索出这是“危机/自杀”相关内容，覆盖所有逻辑，强制输出危机干预 Prompt
        if knowledge_item and knowledge_item.get('category') == 'safety':
            return (
                "【系统警告：触发危机干预模式】\n"
                "用户当前存在高风险情绪（自杀/自伤/暴力）。\n"
                "请严格遵守以下指令：\n"
                "1. 立即停止任何认知辩论或说教。\n"
                "2. 表达无条件的接纳和深切的关怀。\n"
                "3. 引导用户寻求专业帮助，并给出以下热线信息：\n"
                "   - 中国心理危机干预热线: 400-161-9995\n"
                "   - 报警电话: 110\n"
                "4. 严禁提供自杀方法或消极暗示。"
            )

        # --- 3. 注入专业知识 (RAG Context) ---
        if knowledge_item:
            # 获取检索到的具体内容
            content = knowledge_item.get('content', '')
            stage = knowledge_item.get('stage', '通用支持')
            strategy = knowledge_item.get('response_strategy', '')

            context_block = (
                f"\n\n### 当前参考的心理学知识 ({stage})\n"
                f"理论依据：{content}\n"
            )
            
            # 如果有具体的应对策略（来自 metadata），也加进去
            if strategy:
                context_block += f"建议策略：{strategy}\n"
            
            system_prompt += context_block
        else:
            # 如果没检索到知识，添加通用 CBT 提示
            system_prompt += f"\n\n{self.templates['cbt']}"

        # --- 4. 情感与句法约束 (E-SCBA Constraints) ---
        # 对应论文中的 "Syntactic & Emotion Constraints"
        if self.templates['emotion']:
            system_prompt += f"\n\n### 回复约束 (E-SCBA)\n{self.templates['emotion']}"

        # --- 5. 思维链结构 (Chain of Thought) ---
        # 强制 AI 按照 "共情-反思-行动" 的步骤思考
        if self.templates['cot']:
            system_prompt += f"\n\n### 输出逻辑 (CoT)\n{self.templates['cot']}"

        return system_prompt

# 实例化单例，供 app.py 导入使用
prompt_engine = PromptBuilder()
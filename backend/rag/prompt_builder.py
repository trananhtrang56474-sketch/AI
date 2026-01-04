import json

class PromptBuilder:
    @staticmethod
    def build(knowledge_item):
        """根据知识点类型动态生成 Prompt"""
        base_prompt = "你是一个专业的心理咨询师，富有同理心。"

        if not knowledge_item:
            return base_prompt + " 请运用共情倾听技巧，引导用户表达感受。"

        # 1. 危机干预模式
        if knowledge_item.get('type') == 'CRISIS':
            return (
                "【紧急模式】用户存在高风险情绪。\n"
                "1. 表达深切关怀，绝对不要批判。\n"
                "2. 不要进行复杂分析。\n"
                "3. 必须提供以下援助信息：\n"
                f"{json.dumps(knowledge_item.get('hotlines', {}), ensure_ascii=False)}"
            )

        # 2. CBT / 评估模式
        prompt = f"{base_prompt}\n请参考专业理论【{knowledge_item['stage']}】：\n{knowledge_item['content']}\n"
        
        if 'steps' in knowledge_item:
            prompt += "参考步骤：\n" + "\n".join([f"- {s}" for s in knowledge_item['steps']])
            
        if 'questions' in knowledge_item:
            prompt += "\n\n请尝试询问：\n" + "\n".join([f"- {q}" for q in knowledge_item['questions']])
            
        return prompt
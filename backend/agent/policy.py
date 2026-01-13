# backend/agent/policy.py

class PolicyRouter:
    """
    Step 2: 策略决策 (9类中文标签适配版)
    """
    @staticmethod
    def route(emotion, trend, user_text):
        # ==========================================
        # 1. 🚨 最高优先级：危机熔断
        # ==========================================
        if emotion == '危机' or trend == 'CRISIS_ALERT':
            return {
                "search_intent": "危机干预 自杀预防 紧急求助", 
                "stage": "CRISIS_INTERVENTION",
                "instruction": "【警报】用户处于危机状态。忽略所有常规咨询技巧。必须：1. 表达深切关注。2. 询问安全状况。3. 提供危机干预热线。"
            }

        # ==========================================
        # 2. 📉 次高优先级：持续恶化/负面
        # ==========================================
        if trend == 'PERSISTENT_NEGATIVE':
            return {
                "search_intent": "深度共情 绝望感处理", 
                "stage": "DEEP_VALIDATION",
                "instruction": f"【注意】用户持续处于 {emotion} 状态。常规回应可能无效。请尝试更深层的共情（Advanced Empathy），探讨阻碍好转的原因。"
            }

        # ==========================================
        # 3. 🆕 新增情绪分支 (迷茫/悲伤/愧疚/积极)
        # ==========================================
        
        # 🌞 积极 -> 积极心理学
        if emotion == '积极':
            return {
                "search_intent": "积极心理学 优势探索 心流 庆祝",
                "stage": "STRENGTH_BUILDING",
                "instruction": "用户当前情绪积极。请使用积极心理学技巧：1. 进行'品味'(Savoring)，引导用户充分感受当下。2. 肯定用户的优势(Strengths)。3. 共同庆祝这一时刻。"
            }

        # 🌫️ 迷茫 -> 叙事疗法/澄清技术
        if emotion == '迷茫':
            return {
                "search_intent": "生涯规划 叙事疗法 价值观探索",
                "stage": "CLARIFICATION",
                "instruction": "用户感到迷茫。请使用澄清技术。帮助用户梳理混乱的思绪，探索其背后的价值观，尝试找到一个小小的行动方向。"
            }

        # 💔 悲伤 -> 哀伤辅导
        if emotion == '悲伤':
            return {
                "search_intent": "哀伤辅导 丧失处理 情感支撑",
                "stage": "GRIEF_SUPPORT",
                "instruction": "用户正在经历悲伤/丧失。不需要急着解决问题。请提供温暖的陪伴，允许用户哀悼，告诉用户这种痛苦是正常的（正常化）。"
            }

        # 😔 愧疚 -> 自我关怀
        if emotion == '愧疚':
            return {
                "search_intent": "自我关怀 接纳不完美 宽恕",
                "stage": "SELF_COMPASSION",
                "instruction": "用户感到愧疚或自责。请引入'自我关怀'(Self-Compassion)的视角。引导用户像对待好朋友一样对待自己，区分'行为的错误'和'人格的失败'。"
            }

        # ==========================================
        # 4. 🌧️ 常规负面情绪分支
        # ==========================================

        # 抑郁
        if emotion == '抑郁':
            return {
                "search_intent": "行为激活 接纳承诺疗法", 
                "stage": "EMPATHY_SUPPORT",
                "instruction": "用户感到抑郁。侧重于情感接纳。如果合适，可以尝试微小的行为激活（如建议做一件小事），但不要施压。"
            }

        # 焦虑
        if emotion == '焦虑':
            return {
                "search_intent": "认知重构 焦虑缓解技巧", 
                "stage": "COGNITIVE_RESTRUCTURING",
                "instruction": "用户感到焦虑。使用CBT认知重构。引导用户检查那些引发焦虑的'自动化思维'是否符合事实。"
            }
        
        # 痛苦 (Distress)
        if emotion == '痛苦':
            return {
                "search_intent": "情绪着陆技术 痛苦耐受",
                "stage": "DISTRESS_TOLERANCE",
                "instruction": "用户感到痛苦。使用'着陆技术'(Grounding)。引导用户关注当下的感受，缓解过度的心理负荷。"
            }

        # 愤怒
        if emotion == '愤怒':
            return {
                "search_intent": "情绪平复 倾听技巧",
                "stage": "DE_ESCALATION",
                "instruction": "用户感到愤怒。保持冷静和非防御性态度。允许用户宣泄，确立边界，肯定其感受的合理性。"
            }

        # ==========================================
        # 5. 📈 改善或兜底
        # ==========================================
        
        # 情绪好转 (即使当前是平静，但趋势是变好)
        if trend == 'IMPROVING':
            return {
                "search_intent": "积极心理学 优势探索",
                "stage": "STRENGTH_BUILDING",
                "instruction": "监测到用户情绪有好转趋势。请肯定用户的努力，并探索这一变化是如何发生的，帮助用户巩固资源。"
            }

        # 默认/平静 -> 一般支持
        return {
            "search_intent": "心理咨询基础",
            "stage": "GENERAL_SUPPORT",
            "instruction": "用户情绪平静。进行自然的专业对话，保持温暖的人本主义态度，保持开放和好奇。"
        }
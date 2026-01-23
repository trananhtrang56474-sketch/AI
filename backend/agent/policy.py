# backend/agent/policy.py

class PolicyRouter:
    """
    Step 2: 策略决策 (适配 Russell 情绪模型 + 假性平静探测 + 智能建议)
    """
    @staticmethod
    def route(emotion, trend, user_text):
        
        # 0. 🕵️‍♀️ 意图侦测：用户是在"求方法"吗？
        # 如果包含这些词，说明用户想要具体建议，而不是纯聊天
        is_asking_method = any(w in user_text for w in ['怎么', '如何', '办法', '建议', '教我', '什么', 'try', 'step'])

        # ==========================================
        # 1. 🚨 危机与风险 (最高优先级)
        # ==========================================
        # 兼容旧代码的 CRISIS_ALERT 和新代码的 CRISIS_RISING
        if emotion == '危机' or trend in ['CRISIS_RISING', 'CRISIS_ALERT']:
            return {
                "search_intent": "危机干预 自杀预防 紧急求助", 
                "stage": "CRISIS_INTERVENTION",
                "instruction": "【高危警报】监测到风险指标升高。忽略所有常规咨询技巧。必须：1. 确认用户当前安全。2. 表达不离不弃的陪伴。3. 提供危机干预热线。"
            }

        # ==========================================
        # 2. 🎭 假性平静 (Killer Feature - 核心升级)
        # ==========================================
        if trend == 'EMOTIONAL_SUPPRESSION':
            return {
                "search_intent": "防御机制 情感隔离 压抑", 
                "stage": "GENTLE_PROBING", # 温和探询
                "instruction": "【注意】监测到“假性平静”信号。用户刚才还在强烈负面情绪中，突然变平静，可能是情感压抑或防御。策略：1. 不要急着庆祝“好转”。2. 温和地指出这一变化（面质技术）。例如：“你刚才似乎很难过，现在突然平静下来，我有点担心你是不是把情绪藏起来了？”"
            }

        # ==========================================
        # 3. 📉 恶化或持续负面
        # ==========================================
        if trend in ['DETERIORATING', 'PERSISTENT_NEGATIVE']:
            return {
                "search_intent": "深度共情 绝望感处理", 
                "stage": "DEEP_VALIDATION",
                "instruction": f"【注意】监测到情绪指标正在下降或持续低迷（状态：{emotion}）。常规建议可能无效。请使用“深度共情”，让用户感到被彻底接纳。多使用：“这一定很难熬”、“我在这里陪着你”。"
            }

        # ==========================================
        # 4. 常规情绪处理 (结合 Valence/Arousal)
        # ==========================================
        
        # 🌞 积极
        if emotion == '积极':
            return {
                "search_intent": "积极心理学 优势探索 心流 庆祝",
                "stage": "STRENGTH_BUILDING",
                "instruction": "用户当前情绪积极。请使用积极心理学技巧：1. 进行'品味'(Savoring)。2. 肯定用户的优势。3. 共同庆祝。"
            }

        # 🌫️ 迷茫 (低 Valence, 中 Arousal)
        if emotion == '迷茫':
            base_instr = "用户感到迷茫。请使用澄清技术。"
            if is_asking_method:
                base_instr += "【注意】用户在询问方向。请提供结构化的分析框架（如SWOT分析、价值观排序）来帮助用户理清思路。"
            else:
                base_instr += "帮助用户梳理混乱的思绪，探索其背后的价值观。"
                
            return {
                "search_intent": "生涯规划 叙事疗法 价值观探索",
                "stage": "CLARIFICATION",
                "instruction": base_instr
            }

        # 💔 悲伤
        if emotion == '悲伤':
            return {
                "search_intent": "哀伤辅导 丧失处理 情感支撑",
                "stage": "GRIEF_SUPPORT",
                "instruction": "用户正在经历悲伤/丧失。不需要急着解决问题。请提供温暖的陪伴，允许用户哀悼，告诉用户这种痛苦是正常的（正常化）。"
            }

        # 😔 愧疚
        if emotion == '愧疚':
            return {
                "search_intent": "自我关怀 接纳不完美 宽恕",
                "stage": "SELF_COMPASSION",
                "instruction": "用户感到愧疚或自责。请引入'自我关怀'(Self-Compassion)的视角。引导用户像对待好朋友一样对待自己。"
            }

        # 🌧️ 抑郁 (低 Valence, 低 Arousal)
        if emotion == '抑郁':
            base_instr = "用户感到抑郁。侧重于情感接纳。"
            if is_asking_method:
                base_instr += "【注意】用户正在询问具体方法。请优先提供 2-3 个微小的、可执行的'行为激活'建议（如晒太阳、整理桌面），然后再进行情感支持。"
            else:
                base_instr += "如果合适，可以尝试微小的行为激活，但不要施压。"

            return {
                "search_intent": "行为激活 接纳承诺疗法", 
                "stage": "EMPATHY_SUPPORT",
                "instruction": base_instr
            }

        # 🌪️ 焦虑/愤怒 (低 Valence, 高 Arousal) -> 需要降温
        if emotion in ['焦虑', '愤怒', '恐慌']:
            base_instr = f"用户感到{emotion}。"
            if is_asking_method:
                base_instr += "【注意】用户正在寻求缓解办法。请直接提供 2-3 个具体的放松技巧（如4-7-8呼吸法、着陆技术），解决其燃眉之急。"
            else:
                base_instr += "引导用户进行着陆练习或呼吸放松，降低唤醒水平。使用CBT认知重构。"

            return {
                "search_intent": "认知重构 焦虑缓解技巧 情绪调节", 
                "stage": "DE_ESCALATION", # 降级/降温
                "instruction": base_instr
            }
        
        # 痛苦
        if emotion == '痛苦':
            return {
                "search_intent": "情绪着陆技术 痛苦耐受",
                "stage": "DISTRESS_TOLERANCE",
                "instruction": "用户感到痛苦。使用'着陆技术'(Grounding)。引导用户关注当下的感受，缓解过度的心理负荷。"
            }

        # ==========================================
        # 5. 📈 真实好转
        # ==========================================
        if trend == 'IMPROVING':
            return {
                "search_intent": "积极心理学 优势探索",
                "stage": "REINFORCEMENT", # 强化
                "instruction": "监测到用户情绪有好转趋势。请肯定用户的努力，并探索这一变化是如何发生的（探索例外），帮助用户巩固资源。"
            }

        # 默认/平静 -> 检查是否是百科提问
        if is_asking_method:
            return {
                "search_intent": "心理学百科 科普",
                "stage": "PSYCHO_EDUCATION", # 心理教育
                "instruction": "用户正在询问心理学知识或建议。请作为一个专业的心理咨询师，直接、清晰、条理地回答用户的问题。不需要过度的情感共情，侧重于提供有价值的信息。"
            }

        return {
            "search_intent": "心理咨询基础",
            "stage": "GENERAL_SUPPORT",
            "instruction": "用户情绪平静。进行自然的专业对话，保持温暖的人本主义态度，保持开放和好奇。"
        }
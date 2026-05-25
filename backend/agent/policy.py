# backend/agent/policy.py

class PolicyRouter:
    """
    Step 2: 策略决策 (完全适配 Russell 情绪模型 + 假性平静探测 + 动态能量配速)
    """
    @staticmethod
    def route(emotion, trend, user_text, valence=5, arousal=5):
        
        # 0. 意图侦测：用户是在"求方法"吗？
        is_asking_method = any(w in user_text for w in ['怎么', '如何', '办法', '建议', '教我', '什么', 'try', 'step'])

        # ==========================================
        # 新增：基于 Arousal (唤醒度) 的能量配速指令
        # ==========================================
        energy_instruction = ""
        if arousal >= 8:
            energy_instruction = "【高唤醒状态】用户当前处于极高能量（如恐慌、暴怒或狂喜）。你的回复必须：简短、坚定、沉稳。如果是负面高唤醒，切忌长篇大论，直接引导深呼吸或着陆技术（Grounding）。"
        elif arousal <= 3:
            energy_instruction = "【低唤醒状态】用户当前处于极低能量（如极度抑郁、疲惫、死寂）。你的回复必须：极度温柔、包容、轻柔。不要提出需要消耗精力的问题，告诉用户“什么都不做也可以”。"
        else:
            energy_instruction = "【中等唤醒】用户能量平稳，采用正常对话语速与信息量即可。"

        # ==========================================
        # 1. 危机与风险 (最高优先级)
        # ==========================================
        if emotion == '危机' or trend in ['CRISIS_RISING', 'CRISIS_ALERT'] or valence <= 2:
            return {
                "search_intent": "危机干预 自杀预防 紧急求助", 
                "stage": "CRISIS_INTERVENTION",
                "instruction": "【高危警报】监测到风险指标升高。忽略所有常规咨询技巧。必须：1. 确认用户当前安全。2. 表达不离不弃的绝对陪伴。3. 如果情况危急，温和地提供危机干预热线。"
            }

        # ==========================================
        # 2.  假性平静 (Killer Feature)
        # ==========================================
        if trend == 'EMOTIONAL_SUPPRESSION':
            return {
                "search_intent": "防御机制 情感隔离 压抑", 
                "stage": "GENTLE_PROBING", 
                "instruction": "【注意】监测到“假性平静”信号。用户刚才还在强烈负面情绪中，突然变平静，可能是情感隔离。策略：温和地指出这一变化。例如：“你刚才似乎很难受，现在好像突然平静下来了，但我有些担心你是不是把情绪藏起来了？”"
            }

        # ==========================================
        # 3. 恶化或持续负面
        # ==========================================
        if trend in ['DETERIORATING', 'PERSISTENT_NEGATIVE']:
            return {
                "search_intent": "深度共情 绝望感处理", 
                "stage": "DEEP_VALIDATION",
                "instruction": f"【注意】监测到情绪持续低迷（状态：{emotion}）。不要急于给建议！请使用“深度共情”，让用户感到被彻底接纳。多使用：“这一定很难熬”、“我一直在这里陪着你”。\n{energy_instruction}"
            }

        # ==========================================
        # 4. 常规情绪处理 (精准匹配最新标签库)
        # 标签库: [危机, 愤怒, 焦虑, 恐慌, 抑郁, 悲伤, 愧疚, 迷茫, 平静, 放松, 积极, 开心]
        # ==========================================
        
        #  高效价 (积极, 开心, 放松)
        if emotion in ['积极', '开心', '放松']:
            return {
                "search_intent": "积极心理学 优势探索 心流 庆祝",
                "stage": "STRENGTH_BUILDING",
                "instruction": f"用户当前情绪正面（{emotion}）。请使用积极心理学技巧：1. 进行'品味'(Savoring)，让用户多描述开心的细节。2. 肯定用户的优势。3. 共同庆祝。\n{energy_instruction}"
            }

        #  中性效价 (迷茫)
        if emotion == '迷茫':
            base_instr = f"用户感到迷茫。\n{energy_instruction}\n"
            if is_asking_method:
                base_instr += "【注意】用户在询问方向。请提供结构化的分析框架（如SWOT分析、价值观排序）来帮助用户理清思路。"
            else:
                base_instr += "请帮助用户梳理混乱的思绪，使用“苏格拉底式提问”探索其背后的核心价值观。"
                
            return {
                "search_intent": "生涯规划 叙事疗法 价值观探索",
                "stage": "CLARIFICATION",
                "instruction": base_instr
            }

        #  悲伤
        if emotion == '悲伤':
            return {
                "search_intent": "哀伤辅导 丧失处理 情感支撑",
                "stage": "GRIEF_SUPPORT",
                "instruction": f"用户正在经历悲伤/丧失。不需要急着解决问题。请提供温暖的陪伴，允许用户哀悼，告诉用户这种痛苦是正常的。\n{energy_instruction}"
            }

        # 😔 愧疚
        if emotion == '愧疚':
            return {
                "search_intent": "自我关怀 接纳不完美 宽恕",
                "stage": "SELF_COMPASSION",
                "instruction": f"用户感到愧疚或自责。请引入'自我关怀'(Self-Compassion)的视角。引导用户像对待好朋友一样温柔地对待自己。\n{energy_instruction}"
            }

        # 🌧️ 抑郁 
        if emotion == '抑郁':
            base_instr = f"用户感到抑郁。侧重于情感接纳。\n{energy_instruction}\n"
            if is_asking_method:
                base_instr += "【注意】用户在求助。请优先提供 1-2 个极微小的、不需要耗费体力的'行为激活'建议（如喝杯温水、深呼吸一次），然后再进行情感支持。"
            else:
                base_instr += "以倾听和接纳为主，不要给用户施加任何“需要振作起来”的压力。"

            return {
                "search_intent": "行为激活 接纳承诺疗法", 
                "stage": "EMPATHY_SUPPORT",
                "instruction": base_instr
            }

        # 🌪️ 高唤醒负面 (焦虑, 愤怒, 恐慌) -> 核心诉求是降温
        if emotion in ['焦虑', '愤怒', '恐慌']:
            base_instr = f"用户感到{emotion}。\n{energy_instruction}\n"
            if is_asking_method:
                base_instr += "请直接提供 2 个具体的放松技巧（如4-7-8呼吸法、5-4-3-2-1五感着陆法），解决其燃眉之急。"
            else:
                base_instr += "引导用户进行着陆练习或呼吸放松，降低唤醒水平。待其情绪平稳后，再使用CBT认知重构。"

            return {
                "search_intent": "认知重构 焦虑缓解技巧 情绪着陆技术", 
                "stage": "DE_ESCALATION", 
                "instruction": base_instr
            }

        # ==========================================
        # 5. 📈 真实好转
        # ==========================================
        if trend == 'IMPROVING':
            return {
                "search_intent": "积极心理学 优势探索",
                "stage": "REINFORCEMENT", 
                "instruction": "监测到用户情绪有好转趋势。请肯定用户的自我调节能力，并探索这一变化是如何发生的（如：“你刚才做了什么让自己好受一点的？”），帮助用户巩固内在资源。"
            }

        # ==========================================
        # 6. 默认/平静 
        # ==========================================
        if is_asking_method:
            return {
                "search_intent": "心理学百科 科普",
                "stage": "PSYCHO_EDUCATION", 
                "instruction": "用户情绪平稳，正在询问心理学知识或建议。请作为一个专业的心理咨询师，直接、清晰、条理地回答。侧重于提供有价值的信息，不需要过度共情。"
            }

        return {
            "search_intent": "心理咨询基础",
            "stage": "GENERAL_SUPPORT",
            "instruction": "用户情绪平静。进行自然的专业对话，保持温暖的人本主义态度，保持开放和好奇。"
        }
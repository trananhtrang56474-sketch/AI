class SafetyGuard:
    @staticmethod
    def check_crisis(knowledge_item):
        """检查是否命中危机干预"""
        if not knowledge_item: return False
        
        is_crisis = (
            knowledge_item.get('type') == 'CRISIS' or 
            knowledge_item.get('risk_level') == 'high'
        )
        return is_crisis
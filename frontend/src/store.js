import { reactive } from 'vue';

export const authStore = reactive({
  // ============================
  // A. 你原有的登录逻辑 (完全不动)
  // ============================
  isLoggedIn: !!localStorage.getItem('user_id'),
  username: localStorage.getItem('username') || '',
  userId: localStorage.getItem('user_id') || '', // 建议加这行，聊天要用

  login(userId, name) {
    this.isLoggedIn = true;
    this.username = name;
    this.userId = userId; // 存一下ID
    localStorage.setItem('user_id', userId);
    localStorage.setItem('username', name);
  },

  logout() {
    this.isLoggedIn = false;
    this.username = '';
    this.userId = '';
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    
    // 退出时把心理状态也重置一下
    this.resetAnalysis(); 
  },

  // ============================
  // B. ✨ 新增：心理分析状态 (追加在这里)
  // ============================
  analysisState: {
    emotion: '平静',           // 默认值
    strategy: 'GENERAL_SUPPORT', 
    trend: 'FIRST_CONTACT'
  },

  // ✨ 动作：更新数据 (Chat组件会调用它)
  updateAnalysis(data) {
    // 后端返回啥，我们就更新啥
    if (data.emotion) this.analysisState.emotion = data.emotion;
    if (data.strategy) this.analysisState.strategy = data.strategy;
    if (data.trend) this.analysisState.trend = data.trend;
  },
  
  // ✨ 动作：重置 (退出登录用)
  resetAnalysis() {
    this.analysisState = {
      emotion: '平静',
      strategy: 'GENERAL_SUPPORT',
      trend: 'FIRST_CONTACT'
    };
  }
});
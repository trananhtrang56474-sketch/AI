// src/store.js
import { reactive } from 'vue';

export const authStore = reactive({
  // ============================
  // A. 用户身份状态
  // ============================
  // 统一使用 user_id (下划线) 以匹配后端习惯
  user_id: localStorage.getItem('user_id') || null,
  username: localStorage.getItem('username') || '',
  
  // 判断是否登录的计算属性（有些地方可能用到）
  get isLoggedIn() {
    return !!this.user_id;
  },

  // 登录动作
  login(id, name) {
    this.user_id = id;
    this.username = name;
    localStorage.setItem('user_id', id);
    localStorage.setItem('username', name);
  },

  // 登出动作
  logout() {
    this.user_id = null;
    this.username = '';
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
    
    // 退出时把心理状态也重置一下
    this.resetAnalysis(); 
  },

  // ============================
  // B. ✨ 心理分析状态 (侧边栏联动核心)
  // ============================
  analysisState: {
    emotion: '平静',        // 默认情绪
    score: 60,             // ✨ 新增：默认分数 (侧边栏进度条需要！)
    strategy: 'GENERAL_SUPPORT', 
    trend: 'FIRST_CONTACT'
  },

  // ✨ 动作：更新数据 (ChatPage.vue 会调用它)
  updateAnalysis(data) {
    if (!data) return;
    
    // 使用对象合并，只更新后端传回来的字段
    // 比如：如果 data 里没有 score，旧的 score 会被保留，不会变成 undefined
    this.analysisState = {
      ...this.analysisState, // 保留旧值
      ...data                // 覆盖新值
    };

    // 打印日志方便调试
    console.log("📊 [Store] 心理状态已更新:", this.analysisState);
  },
  
  // ✨ 动作：重置 (退出登录或新对话时用)
  resetAnalysis() {
    this.analysisState = {
      emotion: '平静',
      score: 60,
      strategy: 'GENERAL_SUPPORT',
      trend: 'FIRST_CONTACT'
    };
  }
});
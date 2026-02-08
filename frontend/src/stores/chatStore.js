// src/stores/chatStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useChatStore = defineStore('chat', () => {
  // === 1. State (数据) ===
  const activeSessionId = ref(null); 
  const conversations = ref({});     // 聊天记录 { sessionId: [消息...] }
  const chartDataMap = ref({});      // 图表数据 { sessionId: { dates:[], scores:[] } }
  
  // ✨✨✨ 新增：心理状态字典 { sessionId: { emotion:..., trend:... } } ✨✨✨
  const analysisMap = ref({}); 

  // === 2. Getters (计算属性) ===
  const currentConversation = computed(() => {
    return activeSessionId.value ? (conversations.value[activeSessionId.value] || []) : [];
  });

  const currentChartData = computed(() => {
    return activeSessionId.value ? (chartDataMap.value[activeSessionId.value] || { dates: [], scores: [] }) : { dates: [], scores: [] };
  });

  // === 3. Actions (操作方法) ===
  
  function setActiveSession(id) {
    activeSessionId.value = id;
  }

  function setConversation(id, messages) {
    conversations.value[id] = messages;
  }

  function appendMessage(id, message) {
    if (!conversations.value[id]) {
      conversations.value[id] = [];
    }
    conversations.value[id].push(message);
  }

  function setChartData(id, data) {
    chartDataMap.value[id] = data;
  }

  // ✨✨✨ 新增：保存某个会话的心理状态 ✨✨✨
  function setSessionAnalysis(id, analysisData) {
    if (!analysisData) return;
    analysisMap.value[id] = analysisData;
  }

  // ✨✨✨ 新增：获取某个会话的心理状态 ✨✨✨
  function getSessionAnalysis(id) {
    return analysisMap.value[id] || null;
  }

  return {
    activeSessionId,
    conversations,
    chartDataMap,
    analysisMap, // 👈 记得导出
    currentConversation,
    currentChartData,
    setActiveSession,
    setConversation,
    appendMessage,
    setChartData,
    setSessionAnalysis, // 👈 记得导出
    getSessionAnalysis  // 👈 记得导出
  };
});
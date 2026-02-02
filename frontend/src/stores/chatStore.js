// src/stores/chatStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useChatStore = defineStore('chat', () => {
  // === 1. State (数据) ===
  const activeSessionId = ref(null); // 当前选中的会话ID
  const conversations = ref({});     // 聊天记录字典 { sessionId: [消息数组] }
  const chartDataMap = ref({});      // 图表数据字典 { sessionId: { dates:[], scores:[] } }

  // === 2. Getters (计算属性) ===
  // 获取当前会话的消息列表（如果没有就是空数组）
  const currentConversation = computed(() => {
    return activeSessionId.value ? (conversations.value[activeSessionId.value] || []) : [];
  });

  // 获取当前会话的图表数据
  const currentChartData = computed(() => {
    return activeSessionId.value ? (chartDataMap.value[activeSessionId.value] || { dates: [], scores: [] }) : { dates: [], scores: [] };
  });

  // === 3. Actions (操作方法) ===
  
  // 切换当前会话
  function setActiveSession(id) {
    activeSessionId.value = id;
  }

  // 设置某个会话的完整记录 (用于从后端加载历史)
  function setConversation(id, messages) {
    conversations.value[id] = messages;
  }

  // 向某个会话追加一条消息 (用于发送/接收)
  function appendMessage(id, message) {
    if (!conversations.value[id]) {
      conversations.value[id] = [];
    }
    conversations.value[id].push(message);
  }

  // 设置图表数据
  function setChartData(id, data) {
    chartDataMap.value[id] = data;
  }

  return {
    activeSessionId,
    conversations,
    chartDataMap,
    currentConversation,
    currentChartData,
    setActiveSession,
    setConversation,
    appendMessage,
    setChartData
  };
});
<template>
  <div class="chat-pure-container">
    <header class="chat-header glass-header">
      <div class="header-info">
        <h3>{{ headerTitle }}</h3>
        <div class="status-box">
          <span class="status-dot"></span>
          <span class="status-text">AI 在线</span>
        </div>
      </div>
    </header>

    <div v-if="route.query.session_id" class="dashboard-wrapper">
      <div class="dashboard-card glass-card" :class="{ 'is-collapsed': !isChartVisible }">
        
        <div class="dashboard-header" @click="isChartVisible = !isChartVisible">
          <div class="header-left">
            <span class="icon">📈</span>
            <span class="title">心情气象站</span>
            <transition name="fade">
              <span v-show="isChartVisible" class="sub-title"> · 实时情绪波动监测</span>
            </transition>
          </div>
          
          <div class="toggle-btn" :class="{ 'rotated': !isChartVisible }">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>

        <div class="chart-content-area">
          <div class="chart-inner-box">
            <EmotionChart :chart-data="chartData" />
          </div>
        </div>
      </div>
    </div>

    <div class="chat-window-wrapper">
      <ChatWindow 
        ref="chatWindowRef"
        :messages="conversation" 
      />
    </div>

    <div class="input-area-wrapper glass-footer">
      <MessageInput 
        :is-loading="isLoading || isTyping" 
        @send-composite="handleCompositeSend" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { bus } from '../eventBus'; 
import { authStore as store } from '../store.js';

import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';
import EmotionChart from '@/components/EmotionChart.vue'; 

const route = useRoute();
const router = useRouter();

const conversation = ref([]);
const isLoading = ref(false);
const isTyping = ref(false);
const chartData = ref({ dates: [], scores: [] });

// 默认展开图表
const isChartVisible = ref(true);

const headerTitle = computed(() => route.query.session_id ? 'AI 心理咨询师' : '新对话');

// 获取图表数据
const fetchChartData = async (sessionId) => {
  if (!sessionId) return;
  const userId = localStorage.getItem('user_id');
  try {
    const res = await axios.get(`http://127.0.0.1:8080/api/chart-data?user_id=${userId}&session_id=${sessionId}`);
    chartData.value = res.data;
  } catch (e) {
    console.error("加载图表失败", e);
  }
};

// 监听 Session ID
watch(() => route.query.session_id, async (newId) => {
  if (newId) {
    isChartVisible.value = true;
    await loadHistory(newId);
    await fetchChartData(newId); 
  } else {
    conversation.value = [];
    chartData.value = { dates: [], scores: [] };
    if (store.resetAnalysis) store.resetAnalysis();
  }
}, { immediate: true });

// 加载历史
const loadHistory = async (sessionId) => {
  try {
    isLoading.value = true;
    const res = await axios.get(`http://127.0.0.1:8080/api/history?session_id=${sessionId}`);
    if (res.data.messages && res.data.analysis) {
        conversation.value = res.data.messages;
        store.updateAnalysis(res.data.analysis);
    } else if (Array.isArray(res.data)) {
        conversation.value = res.data;
    }
  } catch (e) { console.error(e); } finally { isLoading.value = false; }
};

// 发送消息
const handleCompositeSend = async ({ text, file }) => {
  const userId = localStorage.getItem('user_id');
  let sessionId = route.query.session_id;

  let imageUrl = null;
  if (file) {
    conversation.value.push({ sender: 'user', content: URL.createObjectURL(file) });
    try {
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await axios.post('http://127.0.0.1:8080/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      imageUrl = uploadRes.data.url;
    } catch (e) {
      conversation.value.push({ sender: 'ai', content: '（图片上传失败）', isError: true });
      return; 
    }
  }

  if (text) conversation.value.push({ sender: 'user', content: text });

  isLoading.value = true;
  const aiMsgIndex = conversation.value.push({ sender: 'ai', content: '', isLoading: true }) - 1;

  try {
    const payload = {
      user_id: userId,
      session_id: sessionId || null,
      message: text || '[发送了图片]', 
      image_url: imageUrl 
    };

    const res = await axios.post('http://127.0.0.1:8080/api/chat', payload);

    store.updateAnalysis(res.data); // 更新侧边栏

    if (res.data.session_id) fetchChartData(res.data.session_id); // 刷新图表

    if (!sessionId && res.data.session_id) {
      router.replace(`/chat?session_id=${res.data.session_id}`);
      bus.emitRefresh();
    }

    // 打字机
    const aiMsg = conversation.value[aiMsgIndex];
    aiMsg.isLoading = false;
    isLoading.value = false;
    const reply = res.data.reply;
    let i = 0;
    isTyping.value = true;
    const t = setInterval(() => {
      if (i < reply.length) { aiMsg.content += reply.charAt(i); i++; } 
      else { clearInterval(t); isTyping.value = false; }
    }, 30);

  } catch (e) {
    isLoading.value = false;
    conversation.value[aiMsgIndex].content = "（网络请求失败）";
    conversation.value[aiMsgIndex].isLoading = false;
    conversation.value[aiMsgIndex].isError = true;
  }
};
</script>

<style scoped>
/* === 1. 全局容器与背景 === */
.chat-pure-container {
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  position: relative;
  overflow: hidden; 
  /* ✨ 关键：背景透明，让 App.vue 的渐变透进来 */
  background: transparent;
}

/* === 2. 头部样式 === */
.chat-header {
  padding: 16px 24px; 
  display: flex; align-items: center; flex-shrink: 0;
  position: relative;
}

.glass-header {
  background: var(--glass-bg); /* ✅ 使用全局变量 */
  backdrop-filter: blur(12px);
  border-bottom: var(--glass-border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
  z-index: 10;
}

.header-info h3 { 
  margin: 0; font-size: 18px; font-weight: 600; 
  color: var(--text-main); /* ✅ 使用全局变量 */
  letter-spacing: 0.5px;
}

.status-box {
  display: flex; align-items: center; margin-left: 12px;
  background: rgba(82, 196, 26, 0.1); /* 也可以定义 --success-rgb */
  padding: 4px 10px; border-radius: 20px;
}
.status-dot {
  width: 8px; height: 8px; 
  background: var(--success-color); /* ✅ 使用全局变量 */
  border-radius: 50%; margin-right: 6px;
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.4);
}
.status-text { 
  font-size: 12px; 
  color: var(--success-color); /* ✅ 使用全局变量 */
  font-weight: 500; 
}

/* === 3. 仪表盘 (悬浮玻璃卡片) === */
.dashboard-wrapper {
  padding: 12px 16px 0 16px; 
  position: relative; z-index: 9; flex-shrink: 0;
}

.dashboard-card {
  border-radius: 16px; 
  border: var(--glass-border); /* ✅ 使用全局变量 */
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.glass-card {
  background: var(--glass-bg); /* ✅ 使用全局变量 */
  backdrop-filter: blur(12px);
  box-shadow: var(--glass-shadow);
}

.dashboard-header {
  padding: 14px 20px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer; transition: background 0.2s;
}
.dashboard-header:hover { background: rgba(255, 255, 255, 0.4); }

.header-left { display: flex; align-items: center; gap: 8px; }
.title { font-size: 14px; font-weight: 600; color: var(--text-main); }
.sub-title { font-size: 12px; color: var(--text-sub); font-weight: 400; }

.toggle-btn { 
  color: var(--text-sub); 
  transition: transform 0.4s ease; 
  display: flex; align-items: center;
}
.toggle-btn.rotated { transform: rotate(-180deg); }

/* 折叠动画区域 */
.chart-content-area {
  max-height: 250px; opacity: 1;
  transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}

.is-collapsed .chart-content-area { max-height: 0; opacity: 0; }
.is-collapsed { box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.chart-inner-box { height: 200px; width: 100%; padding: 0 10px 10px 10px; }

/* === 4. 主聊天区域 === */
.chat-window-wrapper {
  flex: 1; overflow: hidden; display: flex; flex-direction: column;
  position: relative; z-index: 1; 
  /* 背景透明，让光透进来 */
  background: transparent; 
}

/* === 5. 输入框区域 === */
.input-area-wrapper {
  position: relative; z-index: 10;
}

.glass-footer {
  background: var(--glass-bg); /* ✅ 使用全局变量 */
  backdrop-filter: blur(10px);
  border-top: var(--glass-border);
}

/* Vue 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
<template>
  <div class="chat-pure-container">
    
    <header class="chat-header">
      <div class="header-info">
        <h3>{{ headerTitle }}</h3>
        <span class="status-badge">在线</span>
      </div>
    </header>

    <div v-if="route.query.session_id" class="dashboard-section">
      
      <div class="dashboard-header" @click="isChartVisible = !isChartVisible">
        <div class="header-left">
          <span>📈 心灵轨迹</span>
          <transition name="fade">
            <span v-show="isChartVisible" class="sub-title">实时监测对话情绪波动</span>
          </transition>
        </div>
        
        <div class="toggle-btn" :class="{ 'rotated': !isChartVisible }">
          ▼
        </div>
      </div>

      <div class="chart-collapse-wrapper" :class="{ 'collapsed': !isChartVisible }">
        <div class="chart-box">
          <EmotionChart :chart-data="chartData" />
        </div>
      </div>

    </div>

    <div class="chat-window-wrapper">
      <ChatWindow 
        ref="chatWindowRef"
        :messages="conversation" 
      />
    </div>

    <MessageInput 
      :is-loading="isLoading || isTyping" 
      @send-composite="handleCompositeSend" 
    />
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

const headerTitle = computed(() => route.query.session_id ? '正在对话' : '新对话');

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
.chat-pure-container {
  height: 100%; 
  display: flex; 
  flex-direction: column; 
  background: #fff; 
  position: relative;
  overflow: hidden; 
}

.chat-header {
  padding: 16px 24px; 
  border-bottom: 1px solid #f0f0f0; 
  display: flex; align-items: center; flex-shrink: 0;
}

/* 仪表盘 */
.dashboard-section {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
  box-shadow: 0 4px 6px rgba(0,0,0,0.02);
  z-index: 10;
}

.dashboard-header {
  padding: 12px 24px;
  display: flex; justify-content: space-between; align-items: center;
  cursor: pointer; user-select: none;
  transition: background-color 0.2s;
}
.dashboard-header:hover { background-color: #f9fafb; }

.header-left {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 600; color: #333;
}
.sub-title { font-size: 12px; color: #999; font-weight: normal; }
.toggle-btn { font-size: 12px; color: #999; transition: transform 0.3s ease; }
.toggle-btn.rotated { transform: rotate(-90deg); }

/* ✨✨✨ 高度修复重点 ✨✨✨ */
.chart-collapse-wrapper {
  max-height: 250px; /* 🔥 调大一点，容纳 180px 的图表 */
  opacity: 1;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
}
.chart-collapse-wrapper.collapsed { max-height: 0; opacity: 0; }

.chart-box {
  height: 180px; /* 🔥 调高高度，给图表足够空间 */
  width: 100%;
  padding: 0 24px 12px 24px; 
}

.header-info h3 { margin: 0; font-size: 16px; color: #333; display: inline-block; }
.status-badge { 
  font-size: 12px; color: #52c41a; background: #f6ffed; padding: 2px 8px; 
  border-radius: 10px; margin-left: 8px; border: 1px solid #b7eb8f; 
}

.chat-window-wrapper {
  flex: 1; overflow: hidden; display: flex; flex-direction: column;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
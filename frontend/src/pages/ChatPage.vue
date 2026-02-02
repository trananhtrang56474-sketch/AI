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
          <div class="toggle-btn" :class="{ rotated: !isChartVisible }">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
              <polyline points="6 9 12 15 18 9" />
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
      <ChatWindow ref="chatWindowRef" :messages="conversation" />
    </div>

    <div class="input-area-wrapper">
      <MessageInput
        ref="msgInputRef"
        :is-loading="isLoading || isTyping"
        @send-composite="handleCompositeSend"
      />
    </div>

  </div>
</template>

<script>
/** ⚠️ 必须保留这个 name，App.vue 里的 KeepAlive 才能生效 */
export default {
  name: 'ChatPage'
};
</script>

<script setup>
import { ref, computed, watch, nextTick, onActivated, onDeactivated, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';
import EmotionChart from '@/components/EmotionChart.vue';

// ✨ 引入 Store
import { useChatStore } from '@/stores/chatStore';
import { authStore as analysisStore } from '../store.js';
import { bus } from '../eventBus';

const route = useRoute();
const router = useRouter();
const chatStore = useChatStore(); // 使用 Pinia 仓库

const chatWindowRef = ref(null);
const msgInputRef = ref(null);

const isLoading = ref(false);
const isTyping = ref(false);
const isChartVisible = ref(true);
let typingTimer = null;

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/* ================= 计算属性 (直接从 Store 取值) ================= */

// 无论怎么切换页面，这里的数据都来自于全局 Store，不会丢失
const conversation = computed(() => chatStore.currentConversation);
const chartData = computed(() => chatStore.currentChartData);

const headerTitle = computed(() =>
  route.query.session_id ? 'AI 心理咨询师' : '新对话'
);

/* ================= 辅助函数 ================= */

const scrollToBottom = () => {
  nextTick(() => {
    if (chatWindowRef.value && chatWindowRef.value.scrollToBottom) {
      chatWindowRef.value.scrollToBottom();
    }
  });
};

/* ================= 加载历史数据 ================= */

const loadHistory = async (sessionId) => {
  try {
    const res = await axios.get(`${API_BASE}/api/history?session_id=${sessionId}`);

    if (res.data.messages && res.data.analysis) {
      // 存入 Store
      chatStore.setConversation(sessionId, res.data.messages);
      analysisStore.updateAnalysis(res.data.analysis);
    } else if (Array.isArray(res.data)) {
      chatStore.setConversation(sessionId, res.data);
    }

    // 激活当前会话
    chatStore.setActiveSession(sessionId);
    scrollToBottom();
  } catch (e) {
    console.error("加载历史失败:", e);
  }
};

/* ================= 加载图表数据 ================= */

const fetchChartData = async (sessionId) => {
  try {
    const userId = localStorage.getItem('user_id');
    const res = await axios.get(
      `${API_BASE}/api/chart-data?user_id=${userId}&session_id=${sessionId}`
    );
    chatStore.setChartData(sessionId, res.data);
  } catch (e) {
    console.error("加载图表失败:", e);
  }
};

/* ================= 核心：路由监听 ================= */

watch(
  () => route.query.session_id,
  async (newId) => {
    // 1. 如果切到了其他页面，不管
    if (route.path !== '/chat') return;

    // 2. 如果是新对话模式
    if (!newId) {
      chatStore.setActiveSession(null);
      return;
    }

    // 3. 告诉 Store 现在的 ID 是多少
    chatStore.setActiveSession(newId);

    // ✨✨✨ 关键优化：如果 Store 里已经有这个会话的数据，直接用！不发请求！ ✨✨✨
    if (chatStore.conversations[newId]?.length > 0) {
      console.log("⚡ [Store] 命中缓存，无需请求");
      scrollToBottom();
      return;
    }

    // 4. 如果没有缓存，才去请求后端
    await loadHistory(newId);
    await fetchChartData(newId);
  },
  { immediate: true }
);

/* ================= 发送消息逻辑 ================= */

const handleCompositeSend = async ({ text, file }) => {
  const userId = localStorage.getItem('user_id');
  let sessionId = route.query.session_id;

  if (!userId) {
    router.push('/login');
    return;
  }

  // 如果是新会话，先生成一个临时 ID
  if (!sessionId) {
    sessionId = `temp-${Date.now()}`;
    chatStore.setActiveSession(sessionId);
  }

  let imageUrl = null;

  // 1. 处理图片上传
  if (file) {
    // 乐观更新：先在界面显示
    chatStore.appendMessage(sessionId, {
      sender: 'user',
      content: URL.createObjectURL(file)
    });
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      imageUrl = uploadRes.data.url;
    } catch (e) {
      console.error("上传失败", e);
    }
  }

  // 2. 处理文字消息
  if (text) {
    chatStore.appendMessage(sessionId, {
      sender: 'user',
      content: text
    });
  }

  scrollToBottom();

  // 3. 添加一个 AI 加载状态占位符
  chatStore.appendMessage(sessionId, {
    sender: 'ai',
    content: '',
    isLoading: true
  });

  // 获取刚才那条 AI 消息的引用（因为是响应式的，后面改它界面会自动变）
  const conversationArr = chatStore.conversations[sessionId];
  const aiMsg = conversationArr[conversationArr.length - 1];

  try {
    const payload = {
      user_id: userId,
      session_id: route.query.session_id || null, // 如果是新对话传 null
      message: text || '[图片]',
      image_url: imageUrl
    };

    const res = await axios.post(`${API_BASE}/api/chat`, payload);

    analysisStore.updateAnalysis(res.data);

    // 4. 处理新会话 ID 变更
    // 如果之前是新对话，现在后端返回了真正的 session_id
    if (!route.query.session_id && res.data.session_id) {
      const realId = res.data.session_id;
      // 把数据从临时 ID 搬迁到 真实 ID
      chatStore.setConversation(realId, chatStore.conversations[sessionId]);
      chatStore.setChartData(realId, chatStore.chartDataMap[sessionId] || { dates: [], scores: [] });
      delete chatStore.conversations[sessionId]; // 删除临时数据
      
      router.replace(`/chat?session_id=${realId}`);
      bus.emitRefresh();
    }

    const reply = res.data.reply;
    aiMsg.isLoading = false;

    // 5. 打字机效果
    let i = 0;
    isTyping.value = true;

    if (typingTimer) clearInterval(typingTimer);
    typingTimer = setInterval(() => {
      if (i < reply.length) {
        aiMsg.content += reply.charAt(i);
        i++;
        scrollToBottom();
      } else {
        clearInterval(typingTimer);
        typingTimer = null;
        isTyping.value = false;
        
        // 只有当有真实 ID 时才刷新图表
        if (res.data.session_id) fetchChartData(res.data.session_id);
      }
    }, 30);

  } catch (e) {
    console.error(e);
    aiMsg.content = '（网络请求失败）';
    aiMsg.isError = true;
    aiMsg.isLoading = false;
  }
};

/* ================= 生命周期钩子 ================= */

// 从 KeepAlive 缓存唤醒时，滚动到底部
onActivated(() => {
  scrollToBottom();
});

onDeactivated(() => {
  if (typingTimer) clearInterval(typingTimer);
  typingTimer = null;
  isTyping.value = false;
});

onUnmounted(() => {
  if (typingTimer) clearInterval(typingTimer);
});
</script>

<style scoped>
/* 样式部分保持不变，直接复用之前的 */
.chat-pure-container { height: 100%; display: flex; flex-direction: column; position: relative; overflow: hidden; background: transparent; }
.chat-header { padding: 16px 24px; display: flex; align-items: center; flex-shrink: 0; position: relative; }
.glass-header { background: var(--glass-bg); backdrop-filter: blur(12px); border-bottom: var(--glass-border); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02); z-index: 10; }
.header-info h3 { margin: 0; font-size: 18px; font-weight: 600; color: var(--text-main); letter-spacing: 0.5px; }
.status-box { display: flex; align-items: center; margin-left: 12px; background: rgba(82, 196, 26, 0.1); padding: 4px 10px; border-radius: 20px; }
.status-dot { width: 8px; height: 8px; background: var(--success-color); border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px rgba(82, 196, 26, 0.4); }
.status-text { font-size: 12px; color: var(--success-color); font-weight: 500; }
.dashboard-wrapper { padding: 12px 16px 0 16px; position: relative; z-index: 9; flex-shrink: 0; }
.dashboard-card { border-radius: 16px; border: var(--glass-border); overflow: hidden; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
.glass-card { background: var(--glass-bg); backdrop-filter: blur(12px); box-shadow: var(--glass-shadow); }
.dashboard-header { padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: background 0.2s; }
.dashboard-header:hover { background: rgba(255, 255, 255, 0.4); }
.header-left { display: flex; align-items: center; gap: 8px; }
.title { font-size: 14px; font-weight: 600; color: var(--text-main); }
.sub-title { font-size: 12px; color: var(--text-sub); font-weight: 400; }
.toggle-btn { color: var(--text-sub); transition: transform 0.4s ease; display: flex; align-items: center; }
.toggle-btn.rotated { transform: rotate(-180deg); }
.chart-content-area { max-height: 250px; opacity: 1; transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease; }
.is-collapsed .chart-content-area { max-height: 0; opacity: 0; }
.is-collapsed { box-shadow: 0 2px 10px rgba(0,0,0,0.02); }
.chart-inner-box { height: 200px; width: 100%; padding: 0 10px 10px 10px; }
.chat-window-wrapper { flex: 1; overflow: hidden; display: flex; flex-direction: column; position: relative; z-index: 1; background: transparent; }
.input-area-wrapper { position: relative; z-index: 10; width: 100%; background: transparent; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
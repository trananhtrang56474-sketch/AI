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

      <div class="header-right-tools">
        <button class="clear-history-btn" @click="handleClearHistory" title="物理清空数据库对话记录">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
          <span>清空记录</span>
        </button>
      </div>
    </header>

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

//  引入 Store
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
let typingTimer = null;

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

/* =================  修改：核弹级清空历史逻辑 ================= */
const handleClearHistory = async () => {
  const sid = route.query.session_id;
  const uid = localStorage.getItem('user_id'); // 获取当前用户 ID
  if (!sid) return;

  if (confirm('确定要清空所有对话记忆吗？此操作将物理删除数据库记录，你的情绪图表也将被重置且无法找回。')) {
    try {
      await axios.post(`${API_BASE}/api/history/clear`, {
        session_id: sid,
        user_id: uid //  把 user_id 也传给后端，用于彻底清空图表底层数据
      });
      
      // 1. 清空前端缓存显示
      chatStore.conversations[sid] = [];
      // 2. 重置心理分析状态
      analysisStore.resetAnalysis();
      
      // 3.  核心修复：发射全局刷新信号，通知 ECharts 组件重新变回“空状态”
      if (bus && bus.emitRefresh) {
        bus.emitRefresh();
      }

      alert('历史记录已彻底清理');
    } catch (e) {
      console.error("清空失败:", e);
      alert('清空失败，请检查后端接口');
    }
  }
};

/* ================= 计算属性 (直接从 Store 取值) ================= */

// 无论怎么切换页面，这里的数据都来自于全局 Store，不会丢失
const conversation = computed(() => chatStore.currentConversation);

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

/* ================= 加载历史数据 (终极兼容修复版) ================= */
const loadHistory = async (sessionId) => {
  try {
    const res = await axios.get(`${API_BASE}/api/history?session_id=${sessionId}`);
    
    //  打印后端到底传回来了什么东西
    console.log(" [Debug] 后端返回的历史数据:", res.data);

    
    // 有的后端用 res.data.messages 包装，有的直接返回 res.data 数组
    let historyMsgs = [];
    if (res.data && Array.isArray(res.data.messages)) {
      historyMsgs = res.data.messages;
    } else if (Array.isArray(res.data)) {
      historyMsgs = res.data;
    }

    // 把提取到的消息塞进状态库
    if (historyMsgs.length > 0) {
      chatStore.setConversation(sessionId, historyMsgs);
    } else {
      console.warn("⚠️ 拿到数据了，但是消息数组是空的！");
    }

    if (res.data && res.data.analysis) {
      analysisStore.updateAnalysis(res.data.analysis);
      chatStore.setSessionAnalysis(sessionId, res.data.analysis); 
    }

    chatStore.setActiveSession(sessionId);
    scrollToBottom();
  } catch (e) {
    console.error("❌ 加载历史失败:", e);
  }
};



/* ================= 核心：路由监听 ================= */

watch(
  () => route.query.session_id,
  async (newId) => {
    if (route.path !== '/chat') return;
    
    //  如果没有传 session_id，不要直接清空，而是尝试自动恢复用户的历史会话
    if (!newId) {
      const userId = localStorage.getItem('user_id');
      if (userId) {
        try {
          // 向后端查询该用户是否已有存在的会话
          const res = await axios.get(`${API_BASE}/api/sessions?user_id=${userId}`);
          if (res.data && res.data.length > 0) {
            // 发现历史会话！立刻在 URL 补上最新的 session_id
            router.replace(`/chat?session_id=${res.data[0].id}`);
            return; // 这里 return 掉，因为 replace 会再次触发这个 watch
          }
        } catch (e) {
          console.error("自动恢复会话失败:", e);
        }
      }
      
      // 如果后端查完发现真的没有历史记录，再展示空白新对话
      chatStore.setActiveSession(null);
      analysisStore.resetAnalysis(); 
      return;
    }

    // --- 下面保持原有的逻辑不变 ---
    chatStore.setActiveSession(newId);

    // 检查是否有缓存的心理状态
    const cachedAnalysis = chatStore.getSessionAnalysis(newId);
    if (cachedAnalysis) {
      console.log(" [Cache] 从缓存恢复心理状态:", cachedAnalysis.emotion);
      analysisStore.updateAnalysis(cachedAnalysis); // 恢复 UI
    } else {
      // 没缓存，重置一下，等 loadHistory 去加载
      analysisStore.resetAnalysis();
    }

    // 检查是否有缓存的消息
    if (chatStore.conversations[newId]?.length > 0) {
      scrollToBottom();
      return;
    }

    await loadHistory(newId);
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

  // 获取刚才那条 AI 消息的引用
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

    // 1. 更新当前 UI (Store)
    analysisStore.updateAnalysis(res.data);
    
    // 2. 更新 chatStore 缓存
    const currentSessionId = res.data.session_id || route.query.session_id;
    if (currentSessionId) {
      chatStore.setSessionAnalysis(currentSessionId, res.data);
    }

    // 4. 处理新会话 ID 变更
    if (!route.query.session_id && res.data.session_id) {
      const realId = res.data.session_id;
      // 把数据从临时 ID 搬迁到 真实 ID
      chatStore.setConversation(realId, chatStore.conversations[sessionId]);
      //  移除了临时 ChartData 搬迁逻辑
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
.chat-pure-container { height: 100%; display: flex; flex-direction: column; position: relative; overflow: hidden; background: transparent; }
.chat-header { padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; position: relative; }
.glass-header { background: var(--glass-bg); backdrop-filter: blur(12px); border-bottom: var(--glass-border); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02); z-index: 10; }
.header-info { display: flex; align-items: center; }
.header-info h3 { margin: 0; font-size: 18px; font-weight: 600; color: var(--text-main); letter-spacing: 0.5px; }
.status-box { display: flex; align-items: center; margin-left: 12px; background: rgba(82, 196, 26, 0.1); padding: 4px 10px; border-radius: 20px; }
.status-dot { width: 8px; height: 8px; background: var(--success-color); border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px rgba(82, 196, 26, 0.4); }
.status-text { font-size: 12px; color: var(--success-color); font-weight: 500; }

/*  清空按钮样式 */
.header-right-tools { display: flex; align-items: center; }
.clear-history-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255, 77, 79, 0.1);
  border: 1px solid rgba(255, 77, 79, 0.2);
  color: #ff4d4f;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.clear-history-btn:hover {
  background: #ff4d4f;
  color: white;
}

.chat-window-wrapper { flex: 1; overflow: hidden; display: flex; flex-direction: column; position: relative; z-index: 1; background: transparent; }
.input-area-wrapper { position: relative; z-index: 10; width: 100%; background: transparent; }
</style>
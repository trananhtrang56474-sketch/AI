<template>
  <div class="chat-pure-container">
    <header class="chat-header">
      <div class="header-info">
        <h3>{{ headerTitle }}</h3>
        <span class="status-badge">在线</span>
      </div>
    </header>

    <ChatWindow 
      ref="chatWindowRef"
      :messages="conversation" 
    />

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
import { authStore as store } from '../store.js';// ✨✨✨ 1. 引入 store
import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';

const route = useRoute();
const router = useRouter();

const conversation = ref([]);
const isLoading = ref(false);
const isTyping = ref(false);

// 计算标题
const headerTitle = computed(() => route.query.session_id ? '正在对话' : '新对话');

// 1. 监听 Session ID 变化
watch(() => route.query.session_id, async (newId) => {
  if (newId) {
    await loadHistory(newId);
  } else {
    conversation.value = [];
    // 新对话时重置右侧面板状态
    if (store.resetAnalysis) store.resetAnalysis();
  }
}, { immediate: true });

// 2. 加载历史
const loadHistory = async (sessionId) => {
  try {
    isLoading.value = true; // 加个加载状态体验更好
    const res = await axios.get(`http://127.0.0.1:8080/api/history?session_id=${sessionId}`);
    
    // ✨ 兼容性判断：
    // 如果后端返回的是新结构 { messages: [], analysis: {} }
    if (res.data.messages && res.data.analysis) {
        conversation.value = res.data.messages;
        
        // 立即更新右侧面板！
        store.updateAnalysis({
            emotion: res.data.analysis.emotion,
            strategy: res.data.analysis.strategy,
            trend: res.data.analysis.trend
        });
    } 
    // 防止后端还没改好导致的报错 (兼容旧的数组结构)
    else if (Array.isArray(res.data)) {
        conversation.value = res.data;
    }
    
  } catch (e) { 
    console.error("加载历史失败", e); 
  } finally {
    isLoading.value = false;
  }
};

// ==========================================
// 🔥 核心修改：处理组合消息 + 更新 Store
// ==========================================
const handleCompositeSend = async ({ text, file }) => {
  const userId = localStorage.getItem('user_id');
  let sessionId = route.query.session_id;

  // 1. 处理图片上传
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
      console.error('图片上传失败', e);
      conversation.value.push({ sender: 'ai', content: '（图片上传失败，请重试）', isError: true });
      return; 
    }
  }

  // 2. 处理文字上屏
  if (text) {
    conversation.value.push({ sender: 'user', content: text });
  }

  // 3. AI 思考中占位
  isLoading.value = true;
  const aiMsgIndex = conversation.value.push({ sender: 'ai', content: '', isLoading: true }) - 1;

  try {
    // 4. 构造 Payload
    const payload = {
      user_id: userId,
      session_id: sessionId || null,
      message: text || '[发送了图片]', 
      image_url: imageUrl 
    };

    const res = await axios.post('http://127.0.0.1:8080/api/chat', payload);

    // ✨✨✨ 关键步骤：收到后端数据后，立即更新 Store ✨✨✨
    // 这会让右侧的 AsidePanel 瞬间刷新！
    store.updateAnalysis({
        emotion: res.data.emotion,
        strategy: res.data.strategy,
        trend: res.data.trend
    });
    // ✨✨✨ 更新结束 ✨✨✨

    // 5. 如果是新会话，更新 URL 和 侧边栏
    if (!sessionId && res.data.session_id) {
      router.replace(`/chat?session_id=${res.data.session_id}`);
      bus.emitRefresh();
    }

    // 6. 处理打字机回复
    const aiMsg = conversation.value[aiMsgIndex];
    aiMsg.isLoading = false;
    isLoading.value = false;
    
    const reply = res.data.reply;
    let i = 0;
    isTyping.value = true;
    
    const t = setInterval(() => {
      if (i < reply.length) {
        aiMsg.content += reply.charAt(i);
        i++;
      } else {
        clearInterval(t);
        isTyping.value = false;
      }
    }, 30);

  } catch (e) {
    console.error(e);
    isLoading.value = false;
    conversation.value[aiMsgIndex].content = "（网络请求失败，请检查连接）";
    conversation.value[aiMsgIndex].isLoading = false;
    conversation.value[aiMsgIndex].isError = true;
  }
};
</script>

<style scoped>
.chat-pure-container {
  height: 100%; display: flex; flex-direction: column; background: #fff; position: relative;
}
.chat-header {
  padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center;
}
.header-info h3 { margin: 0; font-size: 16px; color: #333; display: inline-block; }
.status-badge { 
  font-size: 12px; color: #52c41a; background: #f6ffed; padding: 2px 8px; 
  border-radius: 10px; margin-left: 8px; border: 1px solid #b7eb8f; 
}
</style>
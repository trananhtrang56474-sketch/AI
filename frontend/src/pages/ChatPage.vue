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
      @send="handleSendMessage" 
    />
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { bus } from '../eventBus'; // 引入通信工具
// 复用你已经写好的组件
import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';

const route = useRoute();
const router = useRouter();

const conversation = ref([]);
const isLoading = ref(false);
const isTyping = ref(false);
const chatWindowRef = ref(null);

// 计算标题
const headerTitle = computed(() => route.query.session_id ? '正在对话' : '新对话');

// 🔥 核心逻辑：监听路由参数变化
// 只要左边 Sidebar 改变了 URL，这里就会自动执行
watch(() => route.query.session_id, async (newId) => {
  if (newId) {
    // 如果 URL 里有 session_id，加载历史记录
    await loadHistory(newId);
  } else {
    // 如果没有 ID，说明是新对话，清空屏幕
    conversation.value = [];
  }
}, { immediate: true });

// 加载历史记录函数
const loadHistory = async (sessionId) => {
  try {
    const res = await axios.get(`http://127.0.0.1:8080/api/history?session_id=${sessionId}`);
    conversation.value = res.data;
    // 强制滚动到底部
    nextTick(() => {
      // 假设 ChatWindow 组件暴露了滚动逻辑，或者我们直接操作 DOM
      // 如果 ChatWindow 内部有 watch messages 自动滚动，这里其实可以省略
    });
  } catch (e) { console.error(e); }
};

// 发送消息函数
const handleSendMessage = async (text) => {
  const userId = localStorage.getItem('user_id');
  const sessionId = route.query.session_id; // 从 URL 获取当前会话 ID

  // 1. 上屏
  conversation.value.push({ sender: 'user', content: text });
  
  // 2. 占位
  isLoading.value = true;
  conversation.value.push({ sender: 'ai', content: '', isLoading: true });

  try {
    // 3. 发送请求
    const res = await axios.post('http://127.0.0.1:8080/api/chat', {
      user_id: userId,
      message: text,
      session_id: sessionId || null // 如果是新对话，传 null
    });

    // 🔥 关键点：如果是新对话，后端会返回新 session_id
    if (!sessionId && res.data.session_id) {
      // (A) 修改 URL (不刷新页面)，这样下次发消息就会带上 ID
      router.replace(`/chat?session_id=${res.data.session_id}`);
      // (B) 通知左边 Sidebar 刷新列表，把新标题显示出来
      bus.emitRefresh();
    }

    // 4. 处理打字机回复
    const aiMsg = conversation.value[conversation.value.length - 1];
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
  }
};
</script>

<style scoped>
.chat-pure-container {
  height: 100%; display: flex; flex-direction: column; background: #fff;
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
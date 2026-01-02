<template>
  <div class="chat-page-container">
    <header class="chat-header">
      <div class="header-info">
        <h3>AI 心理顾问</h3>
        <span class="status-badge">在线</span>
      </div>
      <button class="logout-btn" @click="handleLogout">退出</button>
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
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // 1. 引入路由控制
import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';

const router = useRouter(); // 初始化路由
const isLoading = ref(false);
const isTyping = ref(false);
const conversation = ref([]);
const chatWindowRef = ref(null); // 用于控制滚动

// 2. 核心：页面加载时执行
onMounted(async () => {
  // A. 检查是否登录
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    alert("请先登录！");
    router.push('/login'); // 没登录就踢走
    return;
  }

  // B. 加载历史记录
  try {
    const res = await axios.get(`http://127.0.0.1:8080/api/history?user_id=${userId}`);
    // 后端返回的数据格式已经是 [{sender: 'user', content: '...'}, ...]
    // 直接赋值即可
    conversation.value = res.data;
    scrollToBottom();
  } catch (e) {
    console.error("加载历史记录失败", e);
  }
});

// 发送消息逻辑
const handleSendMessage = async (text) => {
  const userId = localStorage.getItem('user_id'); // 获取当前用户ID
  
  // 1. 立即显示用户消息
  conversation.value.push({ sender: 'user', content: text });
  scrollToBottom();

  // 2. 准备 AI 占位消息
  isLoading.value = true;
  conversation.value.push({
    sender: 'ai',
    content: '',
    isLoading: true
  });
  scrollToBottom();

  try {
    // 3. 发送给后端 (带上 user_id)
    const response = await axios.post('http://127.0.0.1:8080/api/chat', { 
      message: text,
      user_id: userId // <--- 关键修改：告诉后端是谁发的
    });

    const fullReply = response.data.reply; 
    const lastMsg = conversation.value[conversation.value.length - 1];

    // 4. 开始打字机效果
    lastMsg.isLoading = false; 
    isLoading.value = false;
    isTyping.value = true;

    let i = 0;
    const typeInterval = setInterval(() => {
      if (i < fullReply.length) {
        lastMsg.content += fullReply.charAt(i);
        i++;
        scrollToBottom(); // 打字时也要跟随滚动
      } else {
        clearInterval(typeInterval);
        isTyping.value = false;
        // 保存这次对话结束的状态，如果需要的话
      }
    }, 30); // 打字速度

  } catch (error) {
    console.error('API Error:', error);
    const lastMsg = conversation.value[conversation.value.length - 1];
    lastMsg.content = "抱歉，连接出了点问题，请检查后端服务是否启动。";
    lastMsg.isLoading = false;
    isLoading.value = false;
    isTyping.value = false;
  }
};

// 辅助函数：滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    // 如果 ChatWindow 组件里暴露了滚动方法，或者我们直接操作 DOM
    // 这里假设 ChatWindow 会自动监听 messages 变化并滚动
    // 如果没有，可以简单粗暴地滚动 document
    // window.scrollTo(0, document.body.scrollHeight);
  });
};

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('user_id');
  localStorage.removeItem('username');
  router.push('/login');
};
</script>

<style scoped>
.chat-page-container {
  height: 100%; 
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  overflow: hidden;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}

.header-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.status-badge {
  font-size: 12px;
  color: #52c41a;
  background: #f6ffed;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #b7eb8f;
  margin-left: 8px;
}

.logout-btn {
  border: none;
  background: none;
  color: #999;
  cursor: pointer;
  font-size: 14px;
}
.logout-btn:hover {
  color: #ff4d4f;
}
</style>
<template>
  <div class="chat-page-container">
    <header class="chat-header">
      <div class="header-info">
        <h3>AI 心理顾问</h3>
        <span class="status-badge">在线</span>
      </div>
    </header>

    <ChatWindow 
      :messages="conversation" 
    />

    <MessageInput 
      :is-loading="isLoading || isTyping" 
      @send="handleSendMessage" 
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import ChatWindow from '@/components/ChatWindow.vue';
import MessageInput from '@/components/MessageInput.vue';

const isLoading = ref(false);
const isTyping = ref(false); // 标记 AI 是否正在逐字输出
const conversation = ref([]); // 存储完整的对话历史

// 核心发送逻辑
const handleSendMessage = async (text) => {
  // 1. 立即显示用户消息
  conversation.value.push({
    sender: 'user',
    content: text
  });

  // 2. 准备 AI 占位消息 (loading 状态)
  isLoading.value = true;
  conversation.value.push({
    sender: 'ai',
    content: '', // 初始内容为空
    isLoading: true
  });

  try {
    // 3. 发送请求给后端 Flask
    const response = await axios.post('http://127.0.0.1:8080/api/chat', { 
      message: text 
    });

    // 4. 获取完整文本
    const fullReply = response.data.reply; 

    // --- 关键修复步骤 ---
    // 必须从响应式数组中取出这条消息对象
    // 只有修改这个对象，页面才会实时更新
    const lastMsg = conversation.value[conversation.value.length - 1];

    // 停止加载动画，准备打字
    lastMsg.isLoading = false; 
    isLoading.value = false;
    isTyping.value = true;

    let i = 0;
    // 启动打字机定时器
    const typeInterval = setInterval(() => {
      if (i < fullReply.length) {
        // 逐字追加内容
        lastMsg.content += fullReply.charAt(i);
        i++;
      } else {
        // 打字结束
        clearInterval(typeInterval);
        isTyping.value = false; // 解锁输入框
      }
    }, 50); // 50ms 打一个字，数字越小越快

  } catch (error) {
    console.error('API Error:', error);
    
    // 出错时同样要获取响应式对象来修改
    const lastMsg = conversation.value[conversation.value.length - 1];
    lastMsg.content = "抱歉，连接出了点问题，请检查后端服务是否启动。";
    lastMsg.isLoading = false;
    lastMsg.isError = true;
    
    // 确保状态复位
    isLoading.value = false;
    isTyping.value = false;
  }
};
</script>

<style scoped>
.chat-page-container {
  /* 关键：占满父容器 (MainLayout 的 content 区) */
  height: 100%; 
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 16px; /* 配合 MainLayout 的圆角风格 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  overflow: hidden; /* 防止圆角溢出 */
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
  color: #52c41a; /* 绿色 */
  background: #f6ffed;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #b7eb8f;
  margin-left: 8px;
}
</style>
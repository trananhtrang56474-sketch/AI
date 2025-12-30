<template>
  <div class="chat-window" ref="scrollContainer">
    <!-- 欢迎状态 -->
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">👋</div>
      <h3>开始一次新的心灵对话</h3>
      <p>这里是安全的空间，请随意倾诉你的烦恼或分享你的快乐。</p>
    </div>

    <!-- 消息列表 -->
    <div v-else class="message-list">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message-row"
        :class="msg.sender === 'user' ? 'message-user' : 'message-ai'"
      >
        <!-- 头像 -->
        <div class="avatar">
          <span v-if="msg.sender === 'ai'" role="img">🤖</span>
          <span v-else role="img">👤</span>
        </div>

        <!-- 气泡 -->
        <div class="bubble-container">
          <div class="bubble">
            <!-- 加载动画 -->
            <div v-if="msg.isLoading" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            <!-- 文本内容 -->
            <div v-else class="text-content" :class="{'error-text': msg.isError}">
              {{ msg.content }}
            </div>
          </div>
          <!-- 时间戳 (可选) -->
          <!-- <span class="timestamp">10:23</span> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
});

const scrollContainer = ref(null);

// 修改点：添加 { deep: true }
// 这样不仅监听数组长度变化，还能监听到 msg.content 的逐字变化
watch(
  () => props.messages, 
  async () => {
    await nextTick();
    if (scrollContainer.value) {
      // 只有当距离底部不远时才自动滚动（防止用户正在看上面的历史记录时被强行拉下来）
      // 但对于简单的打字机效果，直接滚到底部体验通常最好
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  }, 
  { deep: true } // <--- 关键：深度监听
);
</script>

<style scoped>
.chat-window {
  flex: 1; /* 占满剩余垂直空间 */
  overflow-y: auto;
  padding: 24px;
  background-color: #f4f7f9; /* 与 MainLayout 背景一致 */
  scroll-behavior: smooth;
}

/* 滚动条美化 */
.chat-window::-webkit-scrollbar { width: 6px; }
.chat-window::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.1); border-radius: 4px; }

/* 空状态 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #888;
  text-align: center;
}
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { color: #333; margin-bottom: 8px; }

/* 消息行 */
.message-row {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
  gap: 12px;
}
.message-user { flex-direction: row-reverse; }

/* 头像 */
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.message-ai .avatar { background: #fff; border: 1px solid #eee; }
.message-user .avatar { background: #e6f7ff; border: 1px solid #bae7ff; }

/* 气泡 */
.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  max-width: 600px;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  position: relative;
}

/* AI 气泡样式 */
.message-ai .bubble {
  background: #fff;
  color: #333;
  border-top-left-radius: 2px; /* 小尖角效果 */
}

/* 用户气泡样式 */
.message-user .bubble {
  background: #1890ff; /* 主色调 */
  color: #fff;
  border-top-right-radius: 2px;
}

.error-text { color: #ff4d4f; }

/* 输入中动画 */
.typing-indicator { display: flex; gap: 4px; padding: 4px 0; }
.typing-indicator span {
  width: 6px; height: 6px; background: #999; border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
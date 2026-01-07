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
  }
}, { immediate: true });

// 2. 加载历史
const loadHistory = async (sessionId) => {
  try {
    const res = await axios.get(`http://127.0.0.1:8080/api/history?session_id=${sessionId}`);
    conversation.value = res.data;
  } catch (e) { console.error(e); }
};

// ==========================================
// 🔥 核心修改：处理组合消息 (文字 + 图片)
// ==========================================
const handleCompositeSend = async ({ text, file }) => {
  const userId = localStorage.getItem('user_id');
  let sessionId = route.query.session_id;

  // 1. 处理图片上传
  let imageUrl = null;
  if (file) {
    // 立即在界面上显示用户发的图片 (使用本地预览 blob，体验更快)
    conversation.value.push({ sender: 'user', content: URL.createObjectURL(file) });
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // 上传到后端获取真实 URL
      const uploadRes = await axios.post('http://127.0.0.1:8080/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      imageUrl = uploadRes.data.url;
    } catch (e) {
      console.error('图片上传失败', e);
      // 如果上传失败，最好给用户一个提示，这里简单处理
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
    // 4. 构造发送给后端的 Payload
    // 包含 message (文字) 和 image_url (图片链接)
    const payload = {
      user_id: userId,
      session_id: sessionId || null,
      message: text || '[发送了图片]', // 确保 message 字段不为空，防止后端报错
      image_url: imageUrl // 🔥 新增字段传给后端 RAG
    };

    const res = await axios.post('http://127.0.0.1:8080/api/chat', payload);

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
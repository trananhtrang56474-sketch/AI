<template>
  <div class="chat-window" ref="scrollContainer">
    
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-content">
        <div class="empty-icon">🌱</div>
        <h3>开启心灵之旅</h3>
        <p>这里是安全的树洞，随时倾诉你的烦恼...</p>
      </div>
    </div>

    <div v-else class="message-list">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message-row"
        :class="[
          msg.sender === 'user' ? 'message-user' : 'message-ai',
          'animate-slide-up'
        ]"
      >
        <div class="avatar">
          <img v-if="msg.sender === 'ai' || msg.sender === 'assistant'" src="https://api.iconify.design/noto:sunflower.svg" alt="AI" />
          <img v-else src="https://api.iconify.design/noto:person-taking-bath-light-skin-tone.svg" alt="User" />
        </div>

        <div class="bubble-container">
          <span class="sender-name">{{ msg.sender === 'user' ? '我' : 'AI 咨询师' }}</span>
          
          <div class="bubble" :class="{ 'image-bubble': isImage(msg.content) }">
            
            <div v-if="msg.isLoading" class="typing-indicator">
              <span class="typing-text">AI 正在思考</span>
              <span class="typing-cursor"></span>
            </div>

            <div v-else-if="isImage(msg.content)" class="image-wrapper">
              <img 
                :src="msg.content" 
                class="chat-image" 
                @click="previewImage(msg.content)"
                @load="handleImageLoad" 
                @error="handleImageError"
                alt="图片"
              />
            </div>

            <div 
              v-else-if="msg.sender === 'ai' || msg.sender === 'assistant'"
              class="markdown-body"
              v-html="renderMessage(msg.content)"
            ></div>

            <div v-else class="text-content" :class="{'error-text': msg.isError}">
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="previewUrl" class="image-preview-modal" @click="closePreview">
        <img :src="previewUrl" @click.stop />
        <button class="close-btn" @click="closePreview">
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { renderMarkdown } from '../utils/markdown';

const props = defineProps({
  messages: { type: Array, default: () => [] }
});

const scrollContainer = ref(null);
const previewUrl = ref(null);

const renderMessage = (content) => renderMarkdown(content);

const isImage = (content) => {
  if (!content || typeof content !== 'string') return false;
  if (content.startsWith('blob:')) return true;
  if (content.startsWith('data:image/')) return true;
  if (content.includes('/uploads/')) return true;
  const imgExtensions = /\.(jpeg|jpg|gif|png|webp|bmp|svg)($|\?)/i;
  return imgExtensions.test(content);
};

const previewImage = (url) => { previewUrl.value = url; };
const closePreview = () => { previewUrl.value = null; };

const scrollToBottom = async () => {
  await nextTick();
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
  }
};

const handleImageLoad = () => { scrollToBottom(); };
const handleImageError = (e) => {
  e.target.alt = "❌ 图片加载失败";
  e.target.style.background = "#f5f5f5";
  e.target.style.padding = "20px";
  e.target.style.minWidth = "150px";
  e.target.style.borderRadius = "12px";
};

watch(() => props.messages, () => { scrollToBottom(); }, { deep: true, immediate: true });
</script>

<style scoped>
/* === 1. 容器 === */
.chat-window {
  flex: 1; overflow-y: auto; padding: 20px 24px; background-color: transparent; scroll-behavior: smooth; position: relative;
}
.chat-window::-webkit-scrollbar { width: 6px; }
.chat-window::-webkit-scrollbar-track { background: transparent; }
.chat-window::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.1); border-radius: 4px; }
.chat-window::-webkit-scrollbar-thumb:hover { background-color: rgba(0,0,0,0.2); }

/* === 2. 空状态 === */
.empty-state { height: 100%; display: flex; align-items: center; justify-content: center; }
.empty-content { text-align: center; background: var(--glass-bg); backdrop-filter: blur(4px); border: var(--glass-border); padding: 40px; border-radius: 20px; box-shadow: var(--glass-shadow); }
.empty-icon { font-size: 56px; margin-bottom: 16px; animation: float 3s ease-in-out infinite; }
.empty-state h3 { color: var(--text-main); margin-bottom: 8px; font-weight: 600; }
.empty-state p { color: var(--text-sub); font-size: 14px; }

/* === 3. 消息行 === */
.message-row { display: flex; margin-bottom: 24px; align-items: flex-start; gap: 14px; }
.message-user { flex-direction: row-reverse; }

/* ✨ 头像容器优化：稍微加大了图标显示比例，让向日葵更饱满 */
.avatar { width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.8); box-shadow: 0 2px 8px rgba(0,0,0,0.08); flex-shrink: 0; overflow: hidden; border: 2px solid rgba(255,255,255,0.9); }
.avatar img { width: 75%; height: 75%; object-fit: contain; transition: transform 0.3s; }
.avatar:hover img { transform: scale(1.1); } /* 增加了一个悬浮放大的小动画 */

/* 气泡容器 */
.bubble-container { display: flex; flex-direction: column; max-width: 70%; }
.message-user .bubble-container { align-items: flex-end; }
.sender-name { font-size: 12px; color: var(--text-sub); margin-bottom: 4px; margin-left: 4px; opacity: 0.8; }
.message-user .sender-name { display: none; }

/* === 4. 气泡样式 === */
.bubble {
  padding: 14px 18px; 
  border-radius: 18px; 
  font-size: 15px; 
  line-height: 1.6;
  position: relative; 
  word-wrap: break-word;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.message-ai .bubble { 
  background: rgba(255, 255, 255, 0.85); 
  backdrop-filter: blur(4px);
  color: var(--text-main); 
  border-top-left-radius: 4px;
}

.message-user .bubble { 
  background: var(--primary-gradient); 
  color: #fff; 
  border-top-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.25);
}

.bubble.image-bubble {
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  border-radius: 12px;
  overflow: hidden;
}

/* === 打字光标样式 === */
.typing-indicator { display: flex; align-items: center; gap: 6px; padding: 2px 4px; }
.typing-text { font-size: 13px; color: var(--text-sub); font-weight: 500; }
.typing-cursor { display: inline-block; width: 8px; height: 16px; background-color: var(--primary-color); border-radius: 2px; animation: blink 1s step-end infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* === 5. 其他样式 === */
.chat-image {
  display: block; border-radius: 12px; max-width: 100%; cursor: zoom-in;
  transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.chat-image:hover { transform: scale(1.02); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }

.markdown-body { font-size: 15px; color: var(--text-main); }
.markdown-body :deep(strong) { color: var(--primary-color); background: rgba(var(--primary-rgb), 0.1); padding: 0 2px; border-radius: 2px; }
.markdown-body :deep(a) { color: var(--primary-color); border-bottom: 1px dashed var(--primary-color); }
.markdown-body :deep(pre) { background: rgba(255,255,255,0.6); border: 1px solid rgba(0,0,0,0.05); border-radius: 8px; }
.markdown-body :deep(code) { background: rgba(255,255,255,0.6); color: var(--text-main); }

@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-slide-up { animation: slideUp 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }

.image-preview-modal {
  background: rgba(255, 255, 255, 0.2); 
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  z-index: 9999; position: fixed; inset: 0; 
  display: flex; align-items: center; justify-content: center; cursor: zoom-out; animation: fadeIn 0.3s ease;
}
.image-preview-modal img {
  max-width: 900px; max-height: 85vh; width: auto; height: auto;
  object-fit: contain; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  cursor: default; animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.close-btn { 
  position: absolute; top: 30px; right: 30px; background: rgba(0,0,0,0.1); 
  border: 1px solid rgba(255,255,255,0.4); border-radius: 50%; width: 44px; height: 44px; 
  color: #333; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s;
}
.close-btn:hover { background: rgba(0,0,0,0.2); transform: scale(1.1); }

@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
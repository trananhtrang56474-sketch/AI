<template>
  <div class="chat-window" ref="scrollContainer">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-icon">👋</div>
      <h3>开始一次新的心灵对话</h3>
      <p>这里是安全的空间，请随意倾诉你的烦恼或分享你的快乐。</p>
    </div>

    <div v-else class="message-list">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message-row"
        :class="msg.sender === 'user' ? 'message-user' : 'message-ai'"
      >
        <div class="avatar">
          <span v-if="msg.sender === 'ai' || msg.sender === 'assistant'" role="img">🤖</span>
          <span v-else role="img">👤</span>
        </div>

        <div class="bubble-container">
          <div class="bubble">
            
            <div v-if="msg.isLoading" class="typing-indicator">
              <span></span><span></span><span></span>
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

    <div v-if="previewUrl" class="image-preview-modal" @click="closePreview">
      <img :src="previewUrl" @click.stop />
      <span class="close-btn" @click="closePreview">×</span>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
// ✨ 引入 Markdown 渲染工具
import { renderMarkdown } from '../utils/markdown';

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
});

const scrollContainer = ref(null);
const previewUrl = ref(null);

// ✨ Markdown 渲染函数
const renderMessage = (content) => {
  return renderMarkdown(content);
};

// 图片判断逻辑 (保持您原有的超强逻辑)
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
};

watch(
  () => props.messages, 
  () => { scrollToBottom(); }, 
  { deep: true, immediate: true }
);
</script>

<style scoped>
.chat-window {
  flex: 1; overflow-y: auto; padding: 24px; background-color: #f4f7f9;
  scroll-behavior: smooth; position: relative;
}
.chat-window::-webkit-scrollbar { width: 6px; }
.chat-window::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.1); border-radius: 4px; }

.empty-state {
  height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #888; text-align: center;
}
.empty-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state h3 { color: #333; margin-bottom: 8px; }

.message-row { display: flex; margin-bottom: 20px; align-items: flex-start; gap: 12px; }
.message-user { flex-direction: row-reverse; }

.avatar {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.message-ai .avatar { background: #fff; border: 1px solid #eee; }
.message-user .avatar { background: #1890ff; border: 1px solid #bae7ff; }

/* 气泡 */
.bubble {
  padding: 12px 16px; border-radius: 12px; font-size: 15px; line-height: 1.6;
  max-width: 600px; word-wrap: break-word; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  position: relative; overflow: hidden; 
}
.message-ai .bubble { background: #fff; color: #333; border-top-left-radius: 2px; }
.message-user .bubble { background: #1890ff; color: #fff; border-top-right-radius: 2px; }

/* 图片样式 */
.image-wrapper { display: block; min-width: 100px; min-height: 100px; }
.chat-image {
  display: block; max-width: 100%; max-height: 300px; object-fit: contain;
  cursor: zoom-in; border-radius: 8px; background-color: #fff;
}
.error-text { color: #ff4d4f; }

/* 打字机动画 */
.typing-indicator { display: flex; gap: 4px; padding: 4px 0; }
.typing-indicator span {
  width: 6px; height: 6px; background: #999; border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

/* 预览框 */
.image-preview-modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  cursor: zoom-out; animation: fadeIn 0.2s;
}
.image-preview-modal img { max-width: 90vw; max-height: 90vh; border-radius: 4px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
.close-btn { position: absolute; top: 20px; right: 30px; color: white; font-size: 30px; cursor: pointer; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* ✨✨✨ Markdown 专用样式 (深度选择器) ✨✨✨ */
.markdown-body {
  font-size: 15px;
  line-height: 1.7; 
  color: #2c3e50;
  text-align: left;
}

/* 1. 段落间距 */
.markdown-body :deep(p) { margin-bottom: 0.8em; margin-top: 0; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }

/* 2. 列表样式 */
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 20px; margin: 0.5em 0; }
.markdown-body :deep(li) { margin-bottom: 0.4em; list-style-type: disc; }
.markdown-body :deep(ol) :deep(li) { list-style-type: decimal; }

/* 3. 加粗高亮 */
.markdown-body :deep(strong) {
  font-weight: 600; color: #1a1a1a;
  background-color: rgba(255, 235, 59, 0.25); /* 淡淡的黄色高亮 */
  padding: 0 2px; border-radius: 2px;
}

/* 4. 链接样式 */
.markdown-body :deep(a) {
  color: #1890ff; text-decoration: none; border-bottom: 1px dashed #1890ff;
}
.markdown-body :deep(a:hover) { border-bottom-style: solid; }

/* 5. 引用块 (Blockquote) */
.markdown-body :deep(blockquote) {
  margin: 10px 0; padding: 0 1em; color: #6a737d;
  border-left: 4px solid #dfe2e5; background-color: #fafafa;
}

/* 6. 表格样式 (Table) */
.markdown-body :deep(table) {
  border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 14px;
}
.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid #e1e4e8; padding: 6px 10px;
}
.markdown-body :deep(th) { background-color: #f6f8fa; font-weight: 600; }
.markdown-body :deep(tr:nth-child(2n)) { background-color: #fbfcfd; }

/* 7. 代码块样式 (Code) */
.markdown-body :deep(pre) {
  background-color: #f6f8fa; border-radius: 6px; padding: 12px;
  overflow-x: auto; margin: 10px 0; border: 1px solid #eaecef;
}
.markdown-body :deep(code) {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px; background-color: rgba(27, 31, 35, 0.05);
  padding: 2px 4px; border-radius: 3px; color: #476582;
}
.markdown-body :deep(pre) :deep(code) {
  background-color: transparent; padding: 0; color: #24292e;
}
</style>
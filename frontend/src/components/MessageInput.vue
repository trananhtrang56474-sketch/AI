<template>
  <div class="input-container">
    
    <transition name="slide-up">
      <div v-if="showQuickTags && !text && !selectedFile" class="quick-tags">
        <span class="tag-label">此刻的心情...</span>
        <button 
          v-for="tag in quickTags" 
          :key="tag.label" 
          class="tag-btn"
          @click="sendQuickTag(tag.text)"
        >
          {{ tag.icon }} {{ tag.label }}
        </button>
      </div>
    </transition>

    <transition name="pop-in">
      <div v-if="previewUrl" class="image-preview-bar">
        <div class="preview-item">
          <img :src="previewUrl" alt="预览图" />
          <button class="remove-btn" @click="clearFile">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="3" fill="none">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    </transition>

    <div class="input-bar glass-panel" :class="{ 'is-focus': isFocused }">
      
      <div class="tool-btn-wrapper">
        <input 
          type="file" 
          ref="fileInput" 
          accept="image/*" 
          class="hidden-input"
          @change="handleFileSelect"
        />
        <button 
          class="tool-btn" 
          title="上传图片" 
          @click="triggerFileUpload"
          :class="{ 'active': selectedFile }"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="2" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
        </button>
      </div>

      <textarea
        ref="textareaRef"
        v-model="text"
        class="chat-textarea"
        placeholder="告诉 AI 咨询师，此刻你在想什么..."
        rows="1"
        @input="autoResize"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keydown.enter.prevent="handleEnter"
      ></textarea>

      <button 
        class="send-btn" 
        :disabled="(!text.trim() && !selectedFile) || isLoading"
        @click="sendMessage"
      >
        <transition name="scale">
          <span v-if="isLoading" class="spinner"></span>
          <svg v-else viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="send-icon">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </transition>
      </button>

    </div>

  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const props = defineProps({
  isLoading: Boolean
});

const emit = defineEmits(['send-composite']);

const text = ref('');
const selectedFile = ref(null);
const previewUrl = ref(null); // ✨ 新增：用于存储图片预览的 URL
const fileInput = ref(null);
const textareaRef = ref(null);
const isFocused = ref(false);
const showQuickTags = ref(true);

// 情绪快贴数据
const quickTags = [
  { label: '焦虑', icon: '🤯', text: '我最近感到很焦虑，不知道该怎么办。' },
  { label: '难过', icon: '🌧️', text: '心里很难受，想找人说说话。' },
  { label: '迷茫', icon: '😶‍🌫️', text: '我对未来感到很迷茫。' },
  { label: '开心', icon: '✨', text: '今天发生了一件开心的事！' },
];

const sendQuickTag = (tagText) => {
  text.value = tagText;
  sendMessage();
};

const triggerFileUpload = () => {
  fileInput.value.click();
};

const handleFileSelect = (e) => {
  const file = e.target.files[0];
  if (file) {
    selectedFile.value = file;
    // ✨ 生成本地预览 URL
    previewUrl.value = URL.createObjectURL(file);
    // 自动聚焦输入框
    nextTick(() => textareaRef.value?.focus());
  }
};

const clearFile = () => {
  selectedFile.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value); // 释放内存
    previewUrl.value = null;
  }
  if (fileInput.value) fileInput.value.value = '';
};

// 自动调整高度
const autoResize = () => {
  const el = textareaRef.value;
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
  if (el.scrollHeight > 120) {
    el.style.overflowY = 'auto';
  } else {
    el.style.overflowY = 'hidden';
  }
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage();
  }
};

const sendMessage = () => {
  if ((!text.value.trim() && !selectedFile.value) || props.isLoading) return;

  emit('send-composite', {
    text: text.value,
    file: selectedFile.value
  });

  // 重置
  text.value = '';
  clearFile();
  nextTick(() => {
    if(textareaRef.value) {
      textareaRef.value.style.height = 'auto';
    }
  });
};
</script>

<style scoped>
.input-container {
  position: relative;
  width: 100%;
  /* 增加底部内边距，把它“顶”上去 */
  padding: 0 20px 30px 20px; 
  max-width: 900px; 
  margin: 0 auto; 
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 20; 
}

/* === 1. 情绪快贴 === */
.quick-tags {
  display: flex; gap: 8px; margin-bottom: 12px; align-items: center;
  overflow-x: auto; max-width: 100%; padding-bottom: 4px;
}
.tag-label { font-size: 12px; color: var(--text-sub); margin-right: 4px; }
.tag-btn {
  background: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.6);
  padding: 6px 12px; border-radius: 20px;
  font-size: 12px; color: var(--text-main); cursor: pointer;
  transition: all 0.2s; white-space: nowrap;
}
.tag-btn:hover {
  background: var(--primary-color); color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(var(--primary-rgb), 0.3);
}

/* === 2. 图片预览栏 (新样式) === */
.image-preview-bar {
  width: 100%;
  display: flex; justify-content: flex-start;
  margin-bottom: 10px; padding-left: 10px;
}
.preview-item {
  position: relative;
  width: 80px; height: 80px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  background: white;
}
.preview-item img {
  width: 100%; height: 100%; object-fit: cover;
}
.remove-btn {
  position: absolute; top: 4px; right: 4px;
  width: 20px; height: 20px; border-radius: 50%;
  background: rgba(0,0,0,0.6); color: white;
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: 0.2s;
}
.remove-btn:hover { background: #ff4d4f; transform: scale(1.1); }

/* === 3. 核心输入栏 (悬浮玻璃) === */
.input-bar {
  width: 100%;
  display: flex; align-items: flex-end; gap: 10px;
  padding: 10px; border-radius: 24px;
  background: rgba(255, 255, 255, 0.65); 
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.input-bar.is-focus {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 12px 40px rgba(var(--primary-rgb), 0.15);
  border-color: var(--primary-color);
}

/* 工具按钮 */
.tool-btn-wrapper { position: relative; height: 40px; display: flex; align-items: center; }
.hidden-input { display: none; }
.tool-btn {
  width: 36px; height: 36px; border-radius: 50%;
  border: none; background: transparent; color: var(--text-sub);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: 0.2s;
}
.tool-btn:hover, .tool-btn.active { 
  background: rgba(var(--primary-rgb), 0.1); 
  color: var(--primary-color); 
}

/* 输入框 */
.chat-textarea {
  flex: 1; border: none; background: transparent; resize: none;
  font-family: inherit; font-size: 15px; line-height: 1.5;
  color: var(--text-main); max-height: 120px; padding: 8px 0;
}
.chat-textarea:focus { outline: none; }
.chat-textarea::placeholder { color: #a0aec0; }

/* 发送按钮 */
.send-btn {
  width: 40px; height: 40px; border-radius: 50%;
  border: none; 
  background: var(--primary-gradient); 
  color: white;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}
.send-btn:hover:not(:disabled) { transform: scale(1.1) rotate(-10deg); }
.send-btn:disabled { background: #cbd5e0; cursor: not-allowed; box-shadow: none; transform: none; }
.send-icon { margin-left: -2px; margin-top: 2px; }

/* 动画 */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(10px); }

.pop-in-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.pop-in-leave-active { transition: all 0.2s ease-in; }
.pop-in-enter-from { opacity: 0; transform: scale(0.8) translateY(10px); }
.pop-in-leave-to { opacity: 0; transform: scale(0.8); }

.scale-enter-active { transition: all 0.2s; }
.scale-enter-from { transform: scale(0); }

.spinner {
  width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
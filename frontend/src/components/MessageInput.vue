<template>
  <div class="input-area-container">
    
    <transition name="slide-up">
      <div v-if="previewUrl" class="image-preview-bar">
        <div class="preview-item">
          <img :src="previewUrl" alt="预览图" />
          <button class="remove-btn" @click="clearImage" title="移除图片">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="3" fill="none">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    </transition>

    <div class="input-capsule-wrapper">
      
      <input 
        type="file" 
        ref="fileInput"
        accept="image/*"
        style="display: none"
        @change="handleFileSelect"
      />

      <button 
        class="tool-btn" 
        @click="$refs.fileInput.click()" 
        :disabled="isLoading"
        title="上传图片"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
      </button>

      <textarea
        v-model="inputValue"
        placeholder="输入你的想法..."
        @keydown.enter.exact.prevent="handleSend"
        :disabled="isLoading"
        rows="1"
        ref="textareaRef"
        @input="autoResize"
        class="custom-textarea"
      ></textarea>
      
      <button 
        class="send-btn" 
        @click="handleSend" 
        :disabled="(!inputValue.trim() && !selectedFile) || isLoading"
        :class="{ 'is-loading': isLoading }"
      >
        <div v-if="isLoading" class="spinner"></div>
        <svg v-else class="send-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>

    <div class="footer-tip">AI 内容仅供参考，不代表专业医疗建议</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isLoading: Boolean
});

const emit = defineEmits(['send-composite']);

const inputValue = ref('');
const textareaRef = ref(null);
const fileInput = ref(null);
const selectedFile = ref(null);
const previewUrl = ref(null);

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
  event.target.value = '';
};

const clearImage = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
  selectedFile.value = null;
  previewUrl.value = null;
};

const autoResize = () => {
  const el = textareaRef.value;
  if (el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'; // 限制最大高度
  }
};

const handleSend = () => {
  if (props.isLoading) return;
  const text = inputValue.value.trim();
  if (!text && !selectedFile.value) return;

  emit('send-composite', { text: text, file: selectedFile.value });

  inputValue.value = '';
  clearImage();
  if (textareaRef.value) textareaRef.value.style.height = 'auto';
};
</script>

<style scoped>
/* === 1. 外部容器 === */
.input-area-container {
  /* 背景透明，依靠 ChatPage 的渐变 */
  background: transparent; 
  padding: 10px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

/* === 2. 核心胶囊外壳 === */
.input-capsule-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: #fff;
  padding: 8px;
  border-radius: 26px; /* 大圆角胶囊 */
  box-shadow: 0 4px 20px rgba(0,0,0,0.08); /* 悬浮阴影 */
  border: 1px solid rgba(0,0,0,0.02);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 聚焦时的高亮效果 */
.input-capsule-wrapper:focus-within {
  box-shadow: 0 8px 30px rgba(118, 75, 162, 0.15); /* 紫色微光 */
  transform: translateY(-2px);
}

/* === 3. 工具按钮 === */
.tool-btn {
  background: transparent;
  border: none;
  color: #a0aec0;
  width: 40px; height: 40px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.tool-btn:hover { background: #f7fafc; color: #764ba2; }

/* === 4. 输入框 === */
.custom-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.5;
  color: #2d3748;
  max-height: 120px;
  padding: 10px 4px;
  font-family: inherit;
}
.custom-textarea::placeholder { color: #cbd5e0; }

/* === 5. 发送按钮 (纸飞机) === */
.send-btn {
  /* 渐变背景 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50%; /* 圆形按钮 */
  width: 42px; height: 42px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); /* 弹性过渡 */
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05) rotate(-10deg); /* 悬停微动 */
  box-shadow: 0 6px 16px rgba(118, 75, 162, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn:disabled {
  background: #e2e8f0;
  color: #a0aec0;
  box-shadow: none;
  cursor: not-allowed;
}

.send-icon { margin-left: -2px; margin-top: 2px; /* 微调图标位置 */ }

/* === 6. 图片预览气泡 === */
.image-preview-bar {
  padding-left: 12px;
}
.preview-item {
  position: relative;
  display: inline-block;
  width: 70px; height: 70px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 2px solid #fff;
}
.preview-item img { width: 100%; height: 100%; object-fit: cover; }

.remove-btn {
  position: absolute; top: 2px; right: 2px;
  background: rgba(0,0,0,0.6); color: white;
  border: none; border-radius: 50%;
  width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: 0.2s;
}
.remove-btn:hover { background: #e53e3e; }

/* === 7. 底部提示 === */
.footer-tip {
  text-align: center;
  font-size: 11px;
  color: #a0aec0;
  margin-top: -4px;
}

/* === 8. 动画 === */
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}
</style>
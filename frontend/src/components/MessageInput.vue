<template>
  <div class="input-area">
    <div class="input-container">
      <textarea
        v-model="inputValue"
        placeholder="输入你的想法... (Shift + Enter 换行)"
        @keydown.enter.exact.prevent="handleSend"
        :disabled="isLoading"
        rows="1"
        ref="textareaRef"
        @input="autoResize"
      ></textarea>
      
      <button 
        class="send-btn" 
        @click="handleSend" 
        :disabled="!inputValue.trim() || isLoading"
      >
        <span v-if="isLoading" class="spinner"></span>
        <span v-else>发送</span>
      </button>
    </div>
    <div class="footer-tip">AI 生成内容仅供参考，不代表专业医疗建议。</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isLoading: Boolean
});

const emit = defineEmits(['send']);
const inputValue = ref('');
const textareaRef = ref(null);

// 自动调整文本框高度
const autoResize = () => {
  const el = textareaRef.value;
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
};

const handleSend = () => {
  const text = inputValue.value.trim();
  if (!text || props.isLoading) return;
  
  emit('send', text);
  inputValue.value = '';
  
  // 重置高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
  }
};
</script>

<style scoped>
.input-area {
  background: #fff;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.input-container:focus-within {
  background: #fff;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.5;
  color: #333;
  max-height: 120px; /* 限制最大高度 */
  padding: 4px;
}

.send-btn {
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.footer-tip {
  text-align: center;
  font-size: 12px;
  color: #bbb;
  margin-top: 8px;
}

/* 简单的 Spinner 动画 */
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
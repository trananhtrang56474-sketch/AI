<template>
  <div class="input-area">
    
    <div v-if="previewUrl" class="image-preview-bar">
      <div class="preview-item">
        <img :src="previewUrl" alt="预览图" />
        <button class="remove-btn" @click="clearImage" title="移除图片">×</button>
      </div>
    </div>

    <div class="input-container">
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
        title="选择图片"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
          <circle cx="12" cy="13" r="4"></circle>
        </svg>
      </button>

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
        :disabled="(!inputValue.trim() && !selectedFile) || isLoading"
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

// 🔥 定义向父组件发送的组合事件
const emit = defineEmits(['send-composite']);

const inputValue = ref('');
const textareaRef = ref(null);
const fileInput = ref(null);
const selectedFile = ref(null); // 存储实际的文件对象
const previewUrl = ref(null);   // 存储本地预览 URL

// 1. 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  selectedFile.value = file;
  // 创建本地 URL 用于预览
  previewUrl.value = URL.createObjectURL(file);
  
  // 重置 input 值，防止无法重复选同一张图
  event.target.value = '';
};

// 2. 清除选中的图片
const clearImage = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value); // 释放内存
  }
  selectedFile.value = null;
  previewUrl.value = null;
};

// 3. 自动调整文本框高度
const autoResize = () => {
  const el = textareaRef.value;
  if (el) {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
  }
};

// 4. 处理发送逻辑
const handleSend = () => {
  if (props.isLoading) return;
  const text = inputValue.value.trim();
  
  // 如果既没字也没图，不发送
  if (!text && !selectedFile.value) return;

  // 触发父组件事件，传递对象 { text, file }
  emit('send-composite', {
    text: text,
    file: selectedFile.value
  });

  // 发送后重置状态
  inputValue.value = '';
  clearImage();
  
  // 重置文本框高度
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
  display: flex;
  flex-direction: column; /* 垂直排列，为了放置图片预览栏 */
  gap: 10px;
}

/* 🖼️ 图片预览区样式 */
.image-preview-bar {
  padding: 0 4px;
  animation: fadeIn 0.2s ease-out;
}
.preview-item {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 1px solid #eee;
  background: #fafafa;
}
.preview-item img {
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
  border-radius: 8px;
}
.remove-btn {
  position: absolute;
  top: -8px; 
  right: -8px;
  background: #ff4d4f; 
  color: white;
  border: none; 
  border-radius: 50%;
  width: 18px; 
  height: 18px;
  font-size: 14px; 
  line-height: 1;
  cursor: pointer;
  display: flex; 
  align-items: center; 
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}
.remove-btn:hover {
  transform: scale(1.1);
  background: #ff7875;
}

.input-container {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  background: #f5f7fa;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.input-container:focus-within {
  background: #fff;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

/* 📷 工具按钮样式 */
.tool-btn {
  background: transparent;
  border: none;
  color: #8c8c8c;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  height: 36px;
  width: 36px;
  flex-shrink: 0;
}

.tool-btn:hover:not(:disabled) {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.tool-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tool-btn svg {
  width: 20px;
  height: 20px;
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
  max-height: 120px;
  padding: 6px 4px;
}

.send-btn {
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
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
  margin-top: 0;
}

.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
</style>
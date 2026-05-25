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

    <Teleport to="body">
      <transition name="modal-fade">
        <div v-if="showCrisisModal" class="modal-overlay" @click.self="showCrisisModal = false">
          <div class="glass-modal crisis-modal">
            <div class="crisis-icon">💙</div>
            <h3 class="crisis-title">你不是一个人</h3>
            <p class="crisis-text">
              我们注意到你现在的状态可能非常痛苦。<br>
              请记住，在这个艰难的时刻，有专业的支持随时可以帮助你。如果你感到无法承受，请不要独自面对。
            </p>
            <div class="hotline-box">
              <span class="hotline-label">全国24小时心理危机干预热线</span>
              <a href="tel:400-161-9995" class="hotline-number">400-161-9995</a>
            </div>
            <button class="crisis-close-btn" @click="showCrisisModal = false">我知道了，谢谢</button>
          </div>
        </div>
      </transition>
    </Teleport>

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
const previewUrl = ref(null);
const fileInput = ref(null);
const textareaRef = ref(null);
const isFocused = ref(false);
const showQuickTags = ref(true);

//  新增：危机干预状态与敏感词正则
const showCrisisModal = ref(false);
// 覆盖常见的高风险表达，可根据需要扩充
const crisisRegex = /(自杀|不想活了|想死|死掉|结束生命|活不下去|太绝望了|没意思了|一了百了)/;

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
    previewUrl.value = URL.createObjectURL(file);
    nextTick(() => textareaRef.value?.focus());
  }
};

const clearFile = () => {
  selectedFile.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
    previewUrl.value = null;
  }
  if (fileInput.value) fileInput.value.value = '';
};

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

  //  前端轻量级安全围栏拦截 
  if (text.value && crisisRegex.test(text.value)) {
    showCrisisModal.value = true; // 触发援助弹窗
  }

  // 消息依然照常发给后端，后端模型会根据 Prompt 做出深度共情和安抚
  emit('send-composite', {
    text: text.value,
    file: selectedFile.value
  });

  text.value = '';
  clearFile();
  nextTick(() => {
    if(textareaRef.value) {
      textareaRef.value.style.height = 'auto';
    }
  });
};

//  暴露 setText 方法，给外部组件（比如从文章页带参数过来）使用
const setText = (newText) => {
  text.value = newText;
  nextTick(() => {
    if(textareaRef.value) autoResize();
  });
};
defineExpose({ setText });
</script>

<style scoped>
/* 原有样式保持不变... */
.input-container { position: relative; width: 100%; padding: 0 20px 30px 20px; max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; z-index: 20; }
.quick-tags { display: flex; gap: 8px; margin-bottom: 12px; align-items: center; overflow-x: auto; max-width: 100%; padding-bottom: 4px; }
.tag-label { font-size: 12px; color: var(--text-sub); margin-right: 4px; }
.tag-btn { background: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.6); padding: 6px 12px; border-radius: 20px; font-size: 12px; color: var(--text-main); cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.tag-btn:hover { background: var(--primary-color); color: white; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(var(--primary-rgb), 0.3); }
.image-preview-bar { width: 100%; display: flex; justify-content: flex-start; margin-bottom: 10px; padding-left: 10px; }
.preview-item { position: relative; width: 80px; height: 80px; border-radius: 12px; overflow: hidden; border: 2px solid rgba(255, 255, 255, 0.8); box-shadow: 0 4px 12px rgba(0,0,0,0.1); background: white; }
.preview-item img { width: 100%; height: 100%; object-fit: cover; }
.remove-btn { position: absolute; top: 4px; right: 4px; width: 20px; height: 20px; border-radius: 50%; background: rgba(0,0,0,0.6); color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.remove-btn:hover { background: #ff4d4f; transform: scale(1.1); }
.input-bar { width: 100%; display: flex; align-items: flex-end; gap: 10px; padding: 10px; border-radius: 24px; background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.8); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05); transition: all 0.3s; }
.input-bar.is-focus { background: rgba(255, 255, 255, 0.9); box-shadow: 0 12px 40px rgba(var(--primary-rgb), 0.15); border-color: var(--primary-color); }
.tool-btn-wrapper { position: relative; height: 40px; display: flex; align-items: center; }
.hidden-input { display: none; }
.tool-btn { width: 36px; height: 36px; border-radius: 50%; border: none; background: transparent; color: var(--text-sub); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.tool-btn:hover, .tool-btn.active { background: rgba(var(--primary-rgb), 0.1); color: var(--primary-color); }
.chat-textarea { flex: 1; border: none; background: transparent; resize: none; font-family: inherit; font-size: 15px; line-height: 1.5; color: var(--text-main); max-height: 120px; padding: 8px 0; }
.chat-textarea:focus { outline: none; }
.chat-textarea::placeholder { color: #a0aec0; }
.send-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: var(--primary-gradient); color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3); }
.send-btn:hover:not(:disabled) { transform: scale(1.1) rotate(-10deg); }
.send-btn:disabled { background: #cbd5e0; cursor: not-allowed; box-shadow: none; transform: none; }
.send-icon { margin-left: -2px; margin-top: 2px; }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(10px); }
.pop-in-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.pop-in-leave-active { transition: all 0.2s ease-in; }
.pop-in-enter-from { opacity: 0; transform: scale(0.8) translateY(10px); }
.pop-in-leave-to { opacity: 0; transform: scale(0.8); }
.scale-enter-active { transition: all 0.2s; }
.scale-enter-from { transform: scale(0); }
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }

/* ✨✨✨ 新增：危机干预弹窗样式 ✨✨✨ */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(8px); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.crisis-modal { background: #fff; width: 90%; max-width: 400px; border-radius: 24px; padding: 30px 24px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.2); animation: pop 0.4s cubic-bezier(0.16, 1, 0.3, 1); border: 2px solid #e0e7ff; }
.crisis-icon { font-size: 48px; margin-bottom: 15px; animation: heartbeat 2s infinite ease-in-out; }
.crisis-title { margin: 0 0 10px 0; font-size: 20px; color: #1e293b; font-weight: 600; }
.crisis-text { margin: 0 0 20px 0; font-size: 14px; color: #475569; line-height: 1.6; }
.hotline-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 15px; margin-bottom: 25px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
.hotline-label { display: block; font-size: 12px; color: #166534; margin-bottom: 5px; font-weight: bold; }
.hotline-number { display: block; font-size: 28px; font-weight: bold; color: #15803d; text-decoration: none; letter-spacing: 1px; }
.crisis-close-btn { background: #f1f5f9; color: #475569; border: none; padding: 14px 0; width: 100%; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.crisis-close-btn:hover { background: #e2e8f0; color: #1e293b; transform: translateY(-2px); }

@keyframes pop { 0% { transform: scale(0.95); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes heartbeat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click="handleCancel">
      <div class="modal-box glass-modal" @click.stop>
        <div class="modal-icon">⚠️</div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-content">{{ content }}</p>
        
        <div class="modal-actions">
          <button class="btn cancel" @click="handleCancel">取消</button>
          <button class="btn confirm" @click="handleConfirm">确定删除</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  visible: Boolean,
  title: { type: String, default: '确认操作' },
  content: { type: String, default: '此操作无法撤销，是否继续？' }
});

const emit = defineEmits(['confirm', 'cancel']);

const handleConfirm = () => emit('confirm');
const handleCancel = () => emit('cancel');
</script>

<style scoped>
/* 遮罩层 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px); /* 背景模糊 */
}

/* 弹窗主体 */
.modal-box {
  width: 320px; padding: 24px; text-align: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.6);
  transform: translateY(-20px);
}

.modal-icon { font-size: 40px; margin-bottom: 12px; }
.modal-title { margin: 0 0 8px 0; font-size: 18px; color: #333; }
.modal-content { margin: 0 0 24px 0; font-size: 14px; color: #666; line-height: 1.5; }

.modal-actions { display: flex; gap: 12px; justify-content: center; }

/* 按钮样式 */
.btn {
  flex: 1; padding: 10px 0; border: none; border-radius: 10px;
  cursor: pointer; font-weight: 600; transition: 0.2s;
}
.btn.cancel { background: #f5f5f5; color: #666; }
.btn.cancel:hover { background: #e0e0e0; }

.btn.confirm { background: #ff4d4f; color: white; box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3); }
.btn.confirm:hover { background: #ff7875; transform: translateY(-1px); }

/* 动画 */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
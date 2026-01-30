<template>
  <transition name="toast-slide">
    <div v-if="state.show" class="toast-capsule glass-toast" :class="state.type">
      <span class="icon">{{ icon }}</span>
      <span class="text">{{ state.message }}</span>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';
import { toastState } from '../utils/toast.js';

const state = toastState;

const icon = computed(() => {
  switch (state.type) {
    case 'success': return '🎉';
    case 'error': return '❌';
    case 'warning': return '⚠️';
    default: return '💡';
  }
});
</script>

<style scoped>
.toast-capsule {
  position: fixed;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 99999; /* 确保在最上层 */
  
  padding: 12px 24px;
  border-radius: 50px;
  display: flex;
  align-items: center;
  gap: 10px;
  
  /* 玻璃拟态 */
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  min-width: 140px;
  justify-content: center;
  pointer-events: none; /* 让鼠标穿透 */
}

/* 类型配色 */
.toast-capsule.success { color: #52c41a; border-color: rgba(82, 196, 26, 0.3); }
.toast-capsule.error { color: #ff4d4f; border-color: rgba(255, 77, 79, 0.3); }
.toast-capsule.warning { color: #fa8c16; border-color: rgba(250, 140, 22, 0.3); }

/* 动画 */
.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-slide-enter-from, .toast-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px) scale(0.9);
}
</style>
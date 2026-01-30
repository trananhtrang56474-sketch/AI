// src/utils/toast.js
import { reactive } from 'vue';

// 定义响应式状态
export const toastState = reactive({
  show: false,
  message: '',
  type: 'info', // success, error, warning
  timer: null
});

// 导出控制函数
export const showToast = (message, type = 'info', duration = 3000) => {
  // 如果之前有定时器，先清除，防止冲突
  if (toastState.timer) {
    clearTimeout(toastState.timer);
  }
  
  // 设置内容
  toastState.message = message;
  toastState.type = type;
  toastState.show = true;

  // 3秒后自动关闭
  toastState.timer = setTimeout(() => {
    toastState.show = false;
  }, duration);
};
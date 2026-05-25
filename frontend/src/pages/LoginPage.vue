<template>
  <div class="login-container">
    
    <div class="apple-auth-card" :class="{ 'shake-anim': hasError }">
      
      <div class="card-header">
        <div class="logo-icon">⌘</div>
        <h1 class="app-title">{{ isRegister ? '创建您的账号。' : '登录 AI 心灵伴侣。' }}</h1>
        <p class="app-slogan">
          {{ isRegister ? '只需一步，开启内心的平静之旅。' : '欢迎回来，请输入您的凭据。' }}
        </p>
      </div>

      <div class="segmented-control">
        <div class="segment" :class="{ active: !isRegister }" @click="switchMode(false)">登录</div>
        <div class="segment" :class="{ active: isRegister }" @click="switchMode(true)">注册</div>
        <div class="active-bg" :class="isRegister ? 'right' : 'left'"></div>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        
        <div class="input-group">
          <input 
            v-model="username" 
            type="text" 
            class="apple-input"
            :class="{ 'input-error': errorField === 'username' }"
            placeholder="邮箱地址" 
            @focus="clearError"
          />
        </div>

        <transition name="expand">
          <div v-if="isRegister" class="input-group inline-group">
            <input 
              v-model="verifyCode" 
              type="text" 
              class="apple-input code-input"
              :class="{ 'input-error': errorField === 'code' }"
              placeholder="验证码" 
              @focus="clearError"
            />
            <button type="button" class="action-text-btn" :disabled="timer > 0" @click="sendCode">
              {{ timer > 0 ? `${timer}s 后重试` : '获取验证码' }}
            </button>
          </div>
        </transition>

        <div class="input-group">
          <input 
            v-model="password" 
            type="password" 
            class="apple-input"
            :class="{ 'input-error': errorField === 'password' }"
            placeholder="密码" 
            @focus="clearError"
          />
        </div>

        <transition name="fade">
          <div v-if="errorMsg" class="error-tip">
            {{ errorMsg }}
          </div>
        </transition>

        <button type="submit" class="apple-primary-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ isRegister ? '继续 ➔' : '登录' }}</span>
        </button>

      </form>

      <div class="card-footer">
        <a href="#" class="forgot-link" v-if="!isRegister">忘记密码？</a>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { authStore } from '../store';
// ✨ 引入全局 Toast
import { showToast } from '../utils/toast.js';

const router = useRouter();
const route = useRoute();

// 状态管理
const isRegister = ref(false);
const username = ref(''); 
const password = ref('');
const verifyCode = ref('');
const timer = ref(0);

// UI 状态
const loading = ref(false);
const errorMsg = ref('');
const errorField = ref(''); 
const hasError = ref(false); 

onMounted(() => {
  if (route.query.mode === 'register') {
    isRegister.value = true;
  }
});

const switchMode = (targetIsRegister) => {
  if (isRegister.value === targetIsRegister) return;
  isRegister.value = targetIsRegister;
  clearError();
  password.value = '';
  verifyCode.value = '';
};

const clearError = () => {
  errorMsg.value = '';
  errorField.value = '';
  hasError.value = false;
};

// 错误处理
const triggerError = (msg, field = '') => {
  errorMsg.value = msg;
  errorField.value = field;
  hasError.value = true;
  setTimeout(() => { hasError.value = false; }, 500); 
  showToast(msg, 'error');
};

const sendCode = async () => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(username.value)) {
    return triggerError("请输入有效的邮箱地址", 'username');
  }

  try {
    timer.value = 60;
    const interval = setInterval(() => {
      timer.value--;
      if (timer.value <= 0) clearInterval(interval);
    }, 1000);

    await axios.post('http://127.0.0.1:8080/api/send-code', { email: username.value });
    showToast("验证码已发送至您的邮箱", 'success');
  } catch (e) {
    timer.value = 0;
    triggerError(e.response?.data?.error || "发送失败，请检查邮箱", 'username');
  }
};

const handleSubmit = async () => {
  if (!username.value.trim()) return triggerError("请输入邮箱地址", 'username');
  if (isRegister.value && !verifyCode.value) return triggerError("请输入验证码", 'code');
  if (!password.value) return triggerError("请输入密码", 'password');
  
  loading.value = true;
  const url = isRegister.value 
    ? 'http://127.0.0.1:8080/api/register' 
    : 'http://127.0.0.1:8080/api/login';

  const payload = {
    username: username.value,
    email: username.value,
    password: password.value,
    code: verifyCode.value
  };

  try {
    const res = await axios.post(url, payload);

    if (authStore.login) {
      authStore.login(res.data.user_id, username.value);
    } else {
      localStorage.setItem('user_id', res.data.user_id);
      localStorage.setItem('username', username.value);
    }

    const welcomeText = isRegister.value ? "注册成功，欢迎加入！" : `欢迎回来，${username.value}`;
    showToast(welcomeText, 'success');
    
    router.push('/home'); 

  } catch (err) {
    console.error(err);
    triggerError(err.response?.data?.error || "账号或密码错误", 'password');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === 1. 容器 === */
.login-container {
  height: 100vh; width: 100%; display: flex; justify-content: center; align-items: center; 
  padding: 20px; font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* === 2. 苹果风毛玻璃卡片 === */
.apple-auth-card {
  width: 100%; max-width: 400px; 
  background: rgba(255, 255, 255, 0.7); 
  backdrop-filter: saturate(180%) blur(40px); -webkit-backdrop-filter: saturate(180%) blur(40px);
  border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.08), inset 0 0 0 1px rgba(255, 255, 255, 0.8); 
  padding: 48px 40px; display: flex; flex-direction: column; 
  position: relative; overflow: hidden;
  animation: scaleUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes scaleUp { 
  from { opacity: 0; transform: translateY(20px) scale(0.98); } 
  to { opacity: 1; transform: translateY(0) scale(1); } 
}

/* === 3. Header === */
.card-header { text-align: center; margin-bottom: 32px; }
.logo-icon {
  font-size: 36px; margin-bottom: 12px; color: #1d1d1f;
}
.app-title { margin: 0; font-size: 28px; color: #1d1d1f; font-weight: 700; letter-spacing: -0.5px; }
.app-slogan { margin: 8px 0 0; font-size: 15px; color: #86868b; }

/* === 4. iOS 风格分段控制器 === */
.segmented-control {
  display: flex; position: relative; background: rgba(0, 0, 0, 0.05);
  border-radius: 10px; padding: 3px; margin-bottom: 32px;
}
.segment {
  flex: 1; text-align: center; padding: 8px 0; font-size: 14px; font-weight: 500;
  color: #1d1d1f; cursor: pointer; z-index: 2; transition: color 0.3s;
}
.segment.active { color: #1d1d1f; font-weight: 600; }
.active-bg {
  position: absolute; top: 3px; bottom: 3px; width: calc(50% - 3px);
  background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1); z-index: 1;
}
.active-bg.left { transform: translateX(0); }
.active-bg.right { transform: translateX(100%); }

/* === 5. 极致极简输入框 === */
.auth-form { width: 100%; display: flex; flex-direction: column; gap: 16px; }

.input-group { position: relative; }
.apple-input {
  width: 100%; padding: 16px 16px; 
  background: rgba(0, 0, 0, 0.03); border: 1px solid transparent;
  border-radius: 12px; font-size: 16px; color: #1d1d1f;
  transition: all 0.3s ease; box-sizing: border-box; outline: none;
}
.apple-input::placeholder { color: #86868b; }
.apple-input:focus {
  background: #fff; border-color: #0071e3; 
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15);
}
.input-error { 
  border-color: #ff3b30 !important; background: #fff0f0 !important; 
}
.input-error:focus { box-shadow: 0 0 0 4px rgba(255, 59, 48, 0.15) !important; }

/* 验证码行内布局 */
.inline-group { display: flex; gap: 12px; align-items: center; }
.code-input { flex: 1; }
.action-text-btn {
  background: none; border: none; color: #0071e3; font-size: 15px; font-weight: 500;
  cursor: pointer; padding: 0 8px; white-space: nowrap; transition: opacity 0.2s;
}
.action-text-btn:hover:not(:disabled) { opacity: 0.7; }
.action-text-btn:disabled { color: #86868b; cursor: not-allowed; }

/* === 6. 按钮 === */
.apple-primary-btn {
  width: 100%; padding: 16px; margin-top: 8px; background: #0071e3;
  border: none; border-radius: 12px; color: white; font-size: 17px; font-weight: 600;
  cursor: pointer; transition: all 0.2s ease; display: flex; justify-content: center; align-items: center;
}
.apple-primary-btn:hover { background: #0077ed; transform: scale(1.02); }
.apple-primary-btn:active { transform: scale(0.98); }
.apple-primary-btn:disabled { background: #a1cffd; cursor: not-allowed; transform: none; }

/* === 7. 错误提示与底部链接 === */
.error-tip {
  font-size: 13px; color: #ff3b30; text-align: center;
  font-weight: 500; margin-top: -8px; margin-bottom: 4px;
}
.card-footer { margin-top: 24px; text-align: center; }
.forgot-link { color: #0071e3; font-size: 14px; text-decoration: none; font-weight: 500; }
.forgot-link:hover { text-decoration: underline; }

/* === 8. 动画 === */
.spinner { 
  width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.4); 
  border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; 
}
@keyframes spin { to { transform: rotate(360deg); } }

.shake-anim { animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both; }
@keyframes shake { 10%, 90% { transform: translate3d(-2px, 0, 0); } 20%, 80% { transform: translate3d(4px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); } }

/* 展开动画：避免突兀地闪现 */
.expand-enter-active, .expand-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; max-height: 60px; opacity: 1; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; margin-bottom: -16px; transform: translateY(-10px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
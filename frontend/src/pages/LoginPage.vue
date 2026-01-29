<template>
  <div class="login-container">
    <div class="glass-card auth-card" :class="{ 'shake-anim': hasError }">
      
      <div class="card-header">
        <div class="logo-circle">🧠</div>
        <h1 class="app-title">AI Counselor</h1>
        <p class="app-slogan">您的 24 小时专属心理伙伴</p>
      </div>

      <div class="form-body">
        <div class="mode-toggle">
          <h2 :class="{ active: !isRegister }" @click="switchMode(false)">登录</h2>
          <span class="divider">/</span>
          <h2 :class="{ active: isRegister }" @click="switchMode(true)">注册</h2>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          
          <div class="input-group">
            <div class="input-box">
              <span class="icon">📧</span>
              <input 
                v-model="username" 
                type="text" 
                :placeholder="isRegister ? '请输入常用邮箱 (用于接收验证码)' : '请输入邮箱 / 用户名'" 
                :class="{ 'input-error': errorField === 'username' }"
                @focus="clearError"
              />
            </div>
          </div>

          <transition name="slide-fade">
            <div v-if="isRegister" class="input-group">
              <div class="input-box code-box">
                <span class="icon">🔢</span>
                <input 
                  v-model="verifyCode" 
                  type="text" 
                  placeholder="邮件验证码" 
                  @focus="clearError"
                />
                <button type="button" class="code-btn" :disabled="timer > 0" @click="sendCode">
                  {{ timer > 0 ? `${timer}s后重发` : '获取验证码' }}
                </button>
              </div>
            </div>
          </transition>

          <div class="input-group">
            <div class="input-box">
              <span class="icon">🔒</span>
              <input 
                v-model="password" 
                type="password" 
                placeholder="请输入密码" 
                :class="{ 'input-error': errorField === 'password' }"
                @focus="clearError"
              />
            </div>
          </div>

          <transition name="fade">
            <div v-if="errorMsg" class="error-tip">
              <span class="error-icon">⚠️</span> {{ errorMsg }}
            </div>
          </transition>

          <button type="submit" class="submit-btn pulse-hover" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>{{ isRegister ? '✨ 立即注册' : '🚀 进入空间' }}</span>
          </button>

        </form>
      </div>

      <div class="card-footer">
        <p v-if="!isRegister">还没有账号？ <span class="link" @click="switchMode(true)">去注册</span></p>
        <p v-else>已有账号？ <span class="link" @click="switchMode(false)">直接登录</span></p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { authStore } from '../store'; 

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
  // 不清空用户名，方便用户切回来
  password.value = '';
  verifyCode.value = '';
};

const clearError = () => {
  errorMsg.value = '';
  errorField.value = '';
  hasError.value = false;
};

const triggerError = (msg, field = '') => {
  errorMsg.value = msg;
  errorField.value = field;
  hasError.value = true;
  setTimeout(() => { hasError.value = false; }, 500); 
};

// 发送验证码
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
    console.log("验证码已发送"); 
  } catch (e) {
    timer.value = 0;
    triggerError(e.response?.data?.error || "发送失败，请检查邮箱", 'username');
  }
};

// 提交
const handleSubmit = async () => {
  if (!username.value.trim()) return triggerError("请输入邮箱/用户名", 'username');
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

    if (isRegister.value) {
      // 注册成功后，不弹窗，直接丝滑进入
    }
    
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
/* === 1. 容器：全透明，让 App.vue 背景透出来 === */
.login-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: transparent; 
}

/* === 2. 核心玻璃卡片 (使用全局变量) === */
.glass-card {
  width: 100%;
  max-width: 420px; 
  background: var(--glass-bg); /* ✅ 全局背景 */
  backdrop-filter: blur(24px); 
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  border: var(--glass-border); /* ✅ 全局边框 */
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.05), 
              0 0 0 1px rgba(255, 255, 255, 0.2) inset; 
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  overflow: hidden;
  animation: floatUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

@keyframes floatUp {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* === 3. Header === */
.card-header { text-align: center; margin-bottom: 30px; }
.logo-circle {
  width: 64px; height: 64px;
  background: var(--primary-gradient); /* ✅ 使用全局渐变 */
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px;
  margin: 0 auto 16px;
  /* 阴影使用主色调 RGB */
  box-shadow: 0 8px 20px rgba(var(--primary-rgb), 0.4);
  animation: float 6s ease-in-out infinite;
}
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }

.app-title { margin: 0; font-size: 24px; color: var(--text-main); font-weight: 700; letter-spacing: 0.5px; }
.app-slogan { margin: 6px 0 0; font-size: 14px; color: var(--text-sub); }

/* === 4. 表单切换 === */
.form-body { width: 100%; }
.mode-toggle { display: flex; justify-content: center; align-items: center; gap: 16px; margin-bottom: 24px; }
.mode-toggle h2 {
  margin: 0; font-size: 18px; cursor: pointer; color: var(--text-sub); transition: 0.3s;
}
.mode-toggle h2.active { 
  color: var(--primary-color); /* ✅ 激活色变主色 */
  font-weight: 700; 
  transform: scale(1.05); 
}
.divider { color: #cbd5e0; font-size: 14px; }

/* === 5. 输入框 === */
.input-group { margin-bottom: 16px; }
.input-box {
  position: relative;
  background: rgba(255,255,255,0.6);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 12px;
  transition: all 0.3s;
  display: flex; align-items: center;
}
.input-box:focus-within {
  background: #fff;
  border-color: var(--primary-color); /* ✅ 聚焦变主色 */
  box-shadow: 0 0 0 4px rgba(var(--primary-rgb), 0.1); /* ✅ 聚焦光晕 */
}
.icon { padding: 0 12px; font-size: 18px; color: var(--text-sub); }
input {
  width: 100%; padding: 14px 12px 14px 0;
  border: none; background: transparent; outline: none;
  font-size: 15px; color: var(--text-main);
}
.input-error { border-color: var(--danger-color) !important; background: #fff1f0 !important; }

/* 验证码特殊样式 */
.code-box { padding-right: 6px; }
.code-btn {
  background: rgba(var(--primary-rgb), 0.1); /* ✅ 浅主色背景 */
  color: var(--primary-color); /* ✅ 主色文字 */
  border: none; padding: 8px 12px; border-radius: 8px;
  font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
  transition: 0.2s;
}
.code-btn:hover:not(:disabled) { 
  background: var(--primary-color); 
  color: #fff; 
}
.code-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* 提交按钮 */
.submit-btn {
  width: 100%; padding: 14px;
  margin-top: 10px;
  background: var(--primary-gradient); /* ✅ 全局渐变 */
  border: none; border-radius: 12px;
  color: white; font-size: 16px; font-weight: 600;
  cursor: pointer; 
  box-shadow: 0 8px 20px rgba(var(--primary-rgb), 0.3); /* ✅ 主色阴影 */
  transition: all 0.2s; display: flex; justify-content: center; align-items: center;
}
.submit-btn:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 12px 25px rgba(var(--primary-rgb), 0.4); 
}
.submit-btn:active { transform: scale(0.98); }
.submit-btn:disabled { background: #cbd5e0; cursor: not-allowed; box-shadow: none; }

/* === 6. 辅助 UI === */
.error-tip {
  font-size: 13px; color: var(--danger-color); margin-bottom: 16px;
  background: rgba(255, 77, 79, 0.1); padding: 8px 12px; border-radius: 8px;
  display: flex; align-items: center; gap: 6px;
}
.card-footer { margin-top: 24px; font-size: 14px; color: var(--text-sub); }
.link { color: var(--primary-color); font-weight: 600; cursor: pointer; margin-left: 4px; }
.link:hover { text-decoration: underline; }

/* 动画 */
.spinner { width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.shake-anim { animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both; }
@keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } }

/* Vue Transitions */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; position: absolute; }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
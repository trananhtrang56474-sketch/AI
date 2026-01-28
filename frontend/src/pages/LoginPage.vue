<template>
  <div class="auth-wrapper">
    <div class="bg-circle circle-1"></div>
    <div class="bg-circle circle-2"></div>

    <div class="auth-card">
      
      <div class="brand-side">
        <div class="brand-content">
          <div class="logo">🧠</div>
          <h1>AI Counselor</h1>
          <p>您的 24 小时专属心理健康伙伴</p>
          <p class="desc">基于情感计算与认知行为疗法 (CBT) <br> 为您提供安全、私密的倾诉空间。</p>
        </div>
        <svg class="waves" viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg">
          <path fill="#ffffff" fill-opacity="0.2" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,224C672,245,768,267,864,261.3C960,256,1056,224,1152,197.3C1248,171,1344,149,1392,138.7L1440,128L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
        </svg>
      </div>

      <div class="form-side">
        <div class="form-header">
          <h2>{{ isRegister ? '邮箱注册' : '欢迎回来' }}</h2>
          <p>{{ isRegister ? '使用 163/126 等常用邮箱注册' : '使用邮箱或用户名登录' }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form" :class="{ 'shake-anim': hasError }">
          
          <div class="input-wrapper">
            <span class="input-icon">📧</span>
            <input 
              v-model="username" 
              type="text" 
              :placeholder="isRegister ? '请输入邮箱地址' : '请输入邮箱/用户名'" 
              :class="{ 'input-error': errorField === 'username' }"
              @focus="clearError"
            />
          </div>

          <div v-if="isRegister" class="input-wrapper code-wrapper slide-in">
            <span class="input-icon">🔢</span>
            <input 
              v-model="verifyCode" 
              type="text" 
              placeholder="邮件验证码" 
              class="code-input"
              @focus="clearError"
            />
            <button type="button" class="btn-code" :disabled="timer > 0" @click="sendCode">
              {{ timer > 0 ? `${timer}s后重发` : '获取验证码' }}
            </button>
          </div>

          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input 
              v-model="password" 
              type="password" 
              placeholder="请输入密码" 
              :class="{ 'input-error': errorField === 'password' }"
              @focus="clearError"
            />
          </div>

          <div v-if="errorMsg" class="error-banner">
            ⚠️ {{ errorMsg }}
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '处理中...' : (isRegister ? '立即注册' : '登 录') }}
          </button>

        </form>

        <div class="form-footer">
          <p>
            {{ isRegister ? '已有账号？' : '还没有账号？' }}
            <span class="link" @click="toggleMode">{{ isRegister ? '去登录' : '去注册' }}</span>
          </p>
        </div>
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
const username = ref(''); // 兼做登录名和注册邮箱
const password = ref('');
const verifyCode = ref(''); // ✨ 验证码
const timer = ref(0);       // ✨ 倒计时

// UI 状态
const loading = ref(false);
const errorMsg = ref('');
const errorField = ref(''); 
const hasError = ref(false); 

// 初始化检查 URL 参数
onMounted(() => {
  if (route.query.mode === 'register') {
    isRegister.value = true;
  }
});

// 切换模式
const toggleMode = () => {
  isRegister.value = !isRegister.value;
  clearError();
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

// ✨✨✨ 发送验证码逻辑 ✨✨✨
const sendCode = async () => {
  // 简单的邮箱正则验证
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(username.value)) {
    return triggerError("请输入有效的邮箱地址", 'username');
  }

  try {
    // 立即开始倒计时 (优化体验)
    timer.value = 60;
    const interval = setInterval(() => {
      timer.value--;
      if (timer.value <= 0) clearInterval(interval);
    }, 1000);

    // 请求后端接口
    // 如果是毕设演示，后端可能只是模拟发送，请留意后端控制台输出
    await axios.post('http://127.0.0.1:8080/api/send-code', { email: username.value });
    
    // 如果没有报错，说明发送成功(或模拟成功)
    console.log("验证码请求已发送"); 

  } catch (e) {
    timer.value = 0; // 失败重置倒计时
    triggerError(e.response?.data?.error || "发送失败，请检查邮箱", 'username');
  }
};

// 提交逻辑
const handleSubmit = async () => {
  // 1. 前端校验
  if (!username.value.trim()) return triggerError("请输入邮箱/用户名", 'username');
  if (isRegister.value && !verifyCode.value) return triggerError("请输入验证码", 'code');
  if (!password.value) return triggerError("请输入密码", 'password');
  
  // 2. 发起请求
  loading.value = true;
  const url = isRegister.value 
    ? 'http://127.0.0.1:8080/api/register' 
    : 'http://127.0.0.1:8080/api/login';

  // 构造数据包
  const payload = {
    username: username.value, // 登录接口用
    email: username.value,    // 注册接口用
    password: password.value,
    code: verifyCode.value    // 注册接口用
  };

  try {
    const res = await axios.post(url, payload);

    // 成功处理
    if (authStore.login) {
      authStore.login(res.data.user_id, username.value);
    } else {
      localStorage.setItem('user_id', res.data.user_id);
      localStorage.setItem('username', username.value);
    }

    if (isRegister.value) {
      alert("🎉 注册成功！欢迎加入。");
    }
    
    router.push('/chat'); // 跳转到聊天

  } catch (err) {
    console.error(err);
    triggerError(err.response?.data?.error || "服务器连接失败", 'password');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 全局容器：使用更专业的蓝紫色调 */
.auth-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;
}

/* 动态背景球 */
.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  z-index: 0;
  animation: float 10s infinite ease-in-out;
}
.circle-1 { width: 300px; height: 300px; background: rgba(102, 126, 234, 0.4); top: -50px; left: -50px; }
.circle-2 { width: 400px; height: 400px; background: rgba(118, 75, 162, 0.4); bottom: -100px; right: -100px; animation-delay: -5s; }

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

/* 核心卡片 */
.auth-card {
  width: 900px;
  height: 550px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  display: flex;
  overflow: hidden;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

/* 左侧：品牌区 (配色调整为商务蓝紫) */
.brand-side {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  position: relative;
  text-align: center;
}
.logo { font-size: 60px; margin-bottom: 20px; text-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.brand-side h1 { font-size: 32px; font-weight: bold; margin-bottom: 10px; }
.brand-side p { font-size: 16px; opacity: 0.9; margin: 5px 0; }
.desc { margin-top: 20px !important; font-size: 14px !important; opacity: 0.7 !important; line-height: 1.6; }
.waves { position: absolute; bottom: 0; left: 0; width: 100%; height: auto; }

/* 右侧：表单区 */
.form-side {
  flex: 1;
  padding: 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.form-header h2 { font-size: 28px; color: #333; margin-bottom: 8px; }
.form-header p { color: #888; font-size: 14px; margin-bottom: 30px; }

/* 输入框样式 */
.input-wrapper { position: relative; margin-bottom: 20px; }
.input-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #a1a1a1; font-size: 18px; }
.input-wrapper input {
  width: 100%;
  padding: 12px 12px 12px 45px;
  border: 2px solid #eee;
  border-radius: 12px;
  font-size: 15px;
  background: #f9f9f9;
  transition: all 0.3s;
  box-sizing: border-box;
}
.input-wrapper input:focus {
  background: #fff;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  outline: none;
}
.input-error { border-color: #ff6b6b !important; background: #fff0f0 !important; }

/* 验证码特定样式 */
.code-wrapper { display: flex; gap: 10px; }
.code-input { flex: 1; }
.btn-code {
  width: 110px;
  padding: 0;
  border: 1px solid #ddd;
  background: #fff;
  color: #666;
  border-radius: 12px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}
.btn-code:hover:not(:disabled) { border-color: #667eea; color: #667eea; }
.btn-code:disabled { background: #f5f5f5; color: #bbb; cursor: not-allowed; }

/* 错误提示 */
.error-banner { color: #ff6b6b; font-size: 13px; margin-bottom: 15px; text-align: left; animation: fadeIn 0.3s; }

/* 提交按钮 (配色调整为商务蓝紫) */
.btn-submit {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}
.btn-submit:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(118, 75, 162, 0.4); }
.btn-submit:disabled { background: #e0e0e0; color: #999; transform: none; cursor: not-allowed; }

/* 底部链接 */
.form-footer { margin-top: 25px; text-align: center; font-size: 14px; color: #666; }
.link { color: #667eea; font-weight: 600; cursor: pointer; margin-left: 5px; }
.link:hover { text-decoration: underline; }

/* 动画 */
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: #fff; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.shake-anim { animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both; }
@keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); } }
.slide-in { animation: slideUp 0.3s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 768px) {
  .auth-card { width: 100%; height: 100vh; border-radius: 0; flex-direction: column; }
  .brand-side { flex: 0 0 200px; padding: 20px; }
  .logo { font-size: 40px; margin-bottom: 10px; }
  .waves { display: none; }
  .form-side { flex: 1; padding: 30px; }
}
</style>
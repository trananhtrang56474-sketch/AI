<template>
  <div class="login-container">
    <button class="back-btn" @click="goBack">← 返回首页</button>

    <div class="login-box">
      <div class="icon-header">❤️</div>
      <h2 class="title">{{ isRegister ? '注册新账号' : '心理互助小助手' }}</h2>
      <p class="subtitle">{{ isRegister ? '开启您的治愈之旅' : '欢迎回来，这里很安全' }}</p>

      <div class="input-group">
        <input 
          v-model="username" 
          type="text" 
          placeholder="请输入用户名" 
          class="custom-input"
        />
      </div>
      <div class="input-group">
        <input 
          v-model="password" 
          type="password" 
          placeholder="请输入密码" 
          @keyup.enter="handleSubmit" 
          class="custom-input"
        />
      </div>

      <button class="btn-submit" @click="handleSubmit" :disabled="loading">
        {{ loading ? '处理中...' : (isRegister ? '立即注册' : '进 入 系 统') }}
      </button>

      <div class="footer-links">
        <p class="switch-text" @click="toggleMode">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </p>
      </div>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'; // 引入 onMounted
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router'; // 引入 useRoute
import { authStore } from '../store'; 

const router = useRouter();
const route = useRoute(); // 🔥 获取当前路由参数

const isRegister = ref(false);
const username = ref('');
const password = ref('');
const loading = ref(false);
const errorMsg = ref('');

// 🔥 核心修复：页面加载时检查 URL 是否带有 ?mode=register
onMounted(() => {
  if (route.query.mode === 'register') {
    isRegister.value = true;
  }
});

const toggleMode = () => {
  isRegister.value = !isRegister.value;
  errorMsg.value = '';
};

const goBack = () => {
  router.push('/');
};

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    errorMsg.value = "用户名和密码不能为空";
    return;
  }
  
  loading.value = true;
  errorMsg.value = '';

  const url = isRegister.value 
    ? 'http://127.0.0.1:8080/api/register' 
    : 'http://127.0.0.1:8080/api/login';

  try {
    const res = await axios.post(url, {
      username: username.value,
      password: password.value
    });

    if (isRegister.value) {
      alert("注册成功！请直接登录");
      // 注册完自动切回登录模式
      isRegister.value = false; 
      // 可选：自动填好用户名
      // username.value = ''; 
      password.value = '';
    } else {
      // 登录成功 -> 更新全局状态
      authStore.login(res.data.user_id, res.data.username);
      router.push('/home');
    }
  } catch (err) {
    console.error(err);
    errorMsg.value = err.response?.data?.error || "服务连接失败";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 保持你之前的样式不变，这里省略样式代码以节省空间 */
/* 请确保保留之前的 style 标签内容，或者直接复制上一版的样式 */
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
  position: relative;
}
.back-btn {
  position: absolute; top: 20px; left: 20px;
  background: rgba(255, 255, 255, 0.3); border: none; padding: 10px 20px;
  border-radius: 20px; color: white; cursor: pointer; font-weight: bold;
  backdrop-filter: blur(5px); transition: 0.3s;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.5); }
.login-box {
  background: rgba(255, 255, 255, 0.95); padding: 40px 50px; border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1); width: 100%; max-width: 400px;
  text-align: center; animation: fadeIn 0.5s ease-out;
}
.icon-header { font-size: 48px; margin-bottom: 10px; }
.title { color: #2c3e50; margin-bottom: 5px; font-weight: 700; }
.subtitle { color: #7f8c8d; margin-bottom: 30px; font-size: 14px; }
.input-group { margin-bottom: 20px; }
.custom-input {
  width: 100%; padding: 14px 16px; border: 2px solid #f0f2f5; border-radius: 12px;
  font-size: 16px; outline: none; transition: all 0.3s ease; background: #f9f9f9;
}
.custom-input:focus { border-color: #fbc2eb; background: white; box-shadow: 0 0 0 4px rgba(251, 194, 235, 0.1); }
.btn-submit {
  width: 100%; padding: 14px; background: linear-gradient(to right, #a18cd1, #fbc2eb);
  color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600;
  cursor: pointer; transition: 0.3s; margin-top: 10px;
}
.btn-submit:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(161, 140, 209, 0.4); }
.btn-submit:disabled { background: #ccc; cursor: not-allowed; transform: none; }
.footer-links { margin-top: 20px; }
.switch-text { color: #888; cursor: pointer; font-size: 14px; transition: 0.3s; }
.switch-text:hover { color: #a18cd1; text-decoration: underline; }
.error-msg { color: #ff6b6b; margin-top: 15px; font-size: 13px; background: #fff0f0; padding: 8px; border-radius: 8px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
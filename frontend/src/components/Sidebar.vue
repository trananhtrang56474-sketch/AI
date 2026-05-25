<template>
  <nav class="sidebar-nav glass-sidebar" :class="{ collapsed: isCollapsed }">
    
    <div class="sidebar-header">
      <transition name="fade">
        <div v-show="!isCollapsed" class="logo-box">
          <svg class="logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            <path d="M12 8v4"></path>
            <path d="M12 16h.01"></path>
          </svg>
          <h3 class="logo-text">AI 心灵伴侣</h3>
        </div>
      </transition>
      
      <div v-show="isCollapsed" class="logo-box-mini">
        <svg class="logo-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <path d="M12 8v4"></path>
          <path d="M12 16h.01"></path>
        </svg>
      </div>

      <button class="toggle-btn" @click="toggleSidebar" :title="isCollapsed ? '展开菜单' : '收起菜单'">
        <svg v-if="!isCollapsed" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        <svg v-else class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <div class="nav-content">
      
      <div 
        class="nav-item" 
        @click="$router.push('/home')" 
        :class="{ active: $route.path === '/home' }"
        title="仪表盘"
      >
        <div class="icon-wrapper">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"></rect>
            <rect x="14" y="3" width="7" height="7"></rect>
            <rect x="14" y="14" width="7" height="7"></rect>
            <rect x="3" y="14" width="7" height="7"></rect>
          </svg>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="nav-text">首页</span>
        </transition>
      </div>
      
      <div 
        class="nav-item" 
        @click="goToSingleChat" 
        :class="{ active: $route.path.includes('/chat') }"
        title="心灵对话"
      >
        <div class="icon-wrapper">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="nav-text">
            {{ isNavigating ? '加载中...' : '心灵对话' }}
          </span>
        </transition>
      </div>

      <div 
        class="nav-item" 
        @click="$router.push('/report')" 
        :class="{ active: $route.path.includes('/report') }"
        title="心理报告"
      >
        <div class="icon-wrapper">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="nav-text">心理报告</span>
        </transition>
      </div>
      
    </div>

    <div class="sidebar-footer" @click="handleLogout" title="退出登录">
      <div class="footer-btn">
        <svg class="logout-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
        <span v-show="!isCollapsed" class="logout-text">退出登录</span>
      </div>
    </div>

  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { showToast } from '../utils/toast.js'; 

const router = useRouter();
const route = useRoute();
const isCollapsed = ref(false);
const isNavigating = ref(false);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const toggleSidebar = () => { isCollapsed.value = !isCollapsed.value; };

// ✨ 核心逻辑：全局只维系一条长对话
const goToSingleChat = async () => {
  // 1. 如果已经在聊天页，就不重新刷了，避免打断用户当前的操作
  if (route.path.includes('/chat')) return; 

  if (isNavigating.value) return;
  isNavigating.value = true;

  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      router.push('/login');
      return;
    }

    // 2. 去后端拉取会话列表（即使有多个，我们也只认最近的一个当做“全局会话”）
    // 请确保这里请求的接口路径和你后端的历史记录接口一致
    const res = await axios.get(`${API_BASE}/api/sessions?user_id=${userId}`);
    
    if (res.data && res.data.length > 0) {
      // 如果有过记录，强制拿着第一条（最新的）ID 进去，就能衔接上
      const latestSessionId = res.data[0].id; // 或者 res.data[0].session_id，取决于你后端的字段名
      router.push(`/chat?session_id=${latestSessionId}`);
    } else {
      // 只有在新号完全没有发过言的情况下，才进入没有 ID 的初始状态
      router.push('/chat');
    }
  } catch (error) {
    console.error("获取专属对话失败:", error);
    router.push('/chat'); // 接口挂了做兜底
  } finally {
    isNavigating.value = false;
  }
};

const handleLogout = () => {
  localStorage.removeItem('user_id');
  localStorage.removeItem('username');
  router.push('/login');
  showToast('已退出登录', 'info');
};
</script>

<style scoped>
/* 注入治愈系莫兰迪绿色，统一整个项目的视觉语言 */
.glass-sidebar {
  --primary-color: #6B9080; 
  --primary-rgb: 107, 144, 128;
  --text-main: #333d39;
  --danger-color: #e79f72;

  width: 260px;
  height: 100%;
  background: transparent; 
  display: flex;
  flex-direction: column;
  padding: 32px 16px 20px;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  color: var(--text-main); 
  border-right: 1px solid rgba(0,0,0,0.03); 
}

.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 40px; min-height: 40px; padding: 0 8px;
}
.logo-box { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.logo-text { 
  margin: 0; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;
  color: var(--primary-color);
}
.logo-svg { width: 22px; height: 22px; color: var(--primary-color); }
.logo-box-mini { margin: 0 auto; display: flex; align-items: center; justify-content: center; }

.toggle-btn {
  width: 32px; height: 32px;
  border: none; background: rgba(255,255,255,0.5); 
  border-radius: 50%; color: #8a9691;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}
.toggle-btn:hover { 
  background: #fff; 
  color: var(--primary-color);
  transform: scale(1.1); 
}
.toggle-btn .icon { width: 16px; height: 16px; }

.nav-content { flex: 1; display: flex; flex-direction: column; gap: 12px; }

.nav-item {
  display: flex; align-items: center; padding: 14px 16px;
  color: #5a6b64; border-radius: 16px; cursor: pointer; transition: 0.2s;
  white-space: nowrap; font-size: 15px; font-weight: 500;
}
.nav-item:hover { 
  background: rgba(255,255,255,0.6); 
  color: var(--primary-color);
}
.nav-item.active { 
  background: rgba(255,255,255,0.9); 
  color: var(--primary-color);
  font-weight: 600; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}
.icon-wrapper { width: 24px; display: flex; justify-content: center; margin-right: 14px; }
.nav-icon { width: 20px; height: 20px; }

.sidebar-footer { margin-top: auto; padding-top: 16px; }
.footer-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px; border-radius: 12px; color: #8a9691; cursor: pointer;
  transition: 0.2s; white-space: nowrap; font-size: 14px; font-weight: 500;
}
.footer-btn:hover { 
  background: rgba(231, 159, 114, 0.1); 
  color: var(--danger-color);
}
.logout-icon { opacity: 0.8; }

.sidebar-nav.collapsed { width: 88px; padding: 32px 16px 20px; }
.sidebar-nav.collapsed .nav-item { justify-content: center; padding: 14px 0; }
.sidebar-nav.collapsed .icon-wrapper { margin: 0; }
.sidebar-nav.collapsed .sidebar-header { justify-content: center; padding: 0; }
.sidebar-nav.collapsed .toggle-btn { margin: 0 auto; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
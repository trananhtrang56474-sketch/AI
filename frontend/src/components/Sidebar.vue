<template>
  <nav class="sidebar-nav" :class="{ collapsed: isCollapsed }">
    
    <div class="sidebar-header">
      <div v-show="!isCollapsed" class="logo-box">
        <span class="logo-emoji">🧠</span>
        <h3 class="logo-text">AI 心灵伴侣</h3>
      </div>
      
      <div v-show="isCollapsed" class="logo-box-mini">
        <span class="logo-emoji">🧠</span>
      </div>

      <button class="toggle-btn" @click="toggleSidebar" :title="isCollapsed ? '展开菜单' : '收起菜单'">
        <svg v-if="!isCollapsed" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 12h5v7L18 10h-5z" /> </svg>
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
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
        </div>
        <span class="nav-text">仪表盘</span>
      </div>
      
      <div class="action-area">
        <button class="new-chat-btn" @click="handleNewChat" :title="isCollapsed ? '新对话' : ''">
          <span class="plus-icon">+</span>
          <span class="btn-text">开始新对话</span>
        </button>
      </div>

      <div class="history-group" v-show="!isCollapsed">
        <div class="group-title" @click="isHistoryOpen = !isHistoryOpen">
          <span>🕒 历史对话</span>
          <svg class="arrow" :class="{ rotated: isHistoryOpen }" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
        
        <div v-show="isHistoryOpen" class="history-list">
          <div v-if="sessions.length === 0" class="empty-tip">暂无记录</div>
          
          <div 
            v-for="item in sessions" 
            :key="item.id" 
            class="history-item"
            :class="{ active: currentSessionId == item.id }"
            @click="handleSelectSession(item.id)"
          >
            <span class="dot"></span>
            <span class="title">{{ item.title }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer" @click="handleLogout" title="退出登录">
      <span class="logout-icon">🚪</span>
      <span class="logout-text">退出登录</span>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { bus } from '../eventBus';

const router = useRouter();
const route = useRoute();

const sessions = ref([]);
const isHistoryOpen = ref(true);
const currentSessionId = ref(null);

// 🔥 新增：控制侧边栏折叠状态
const isCollapsed = ref(false);
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// ... 原有的逻辑保持不变 ...
const loadSessions = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) return;
  try {
    const res = await axios.get(`http://127.0.0.1:8080/api/sessions?user_id=${userId}`);
    sessions.value = res.data;
  } catch (e) { console.error(e); }
};

const handleSelectSession = (id) => {
  currentSessionId.value = id;
  router.push(`/chat?session_id=${id}`);
};

const handleNewChat = () => {
  currentSessionId.value = null;
  router.push('/chat');
};

const handleLogout = () => {
  localStorage.clear();
  router.push('/login');
};

watch(() => bus.refreshSessions, () => loadSessions());
watch(() => route.query.session_id, (val) => {
  currentSessionId.value = val || null;
}, { immediate: true });

onMounted(() => loadSessions());
</script>

<style scoped>
/* 基础容器 */
.sidebar-nav {
  width: 240px; /* 默认宽度 */
  height: 100%;
  background: #fff;
  border-right: 1px solid #eef0f5;
  display: flex;
  flex-direction: column;
  padding: 16px;
  transition: width 0.3s cubic-bezier(0.25, 0.8, 0.5, 1); /* 丝滑动画 */
  overflow: hidden; /* 隐藏溢出内容 */
}

/* --- 1. 顶部 Header --- */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  height: 40px;
}

.logo-box {
  display: flex; align-items: center; gap: 8px; white-space: nowrap;
}
.logo-text { margin: 0; font-size: 18px; color: #1890ff; font-weight: 700; }
.logo-emoji { font-size: 24px; }
.logo-box-mini { font-size: 24px; margin-right: auto; }

/* 切换按钮样式 */
.toggle-btn {
  width: 32px; height: 32px;
  border: none; background: #f5f7fa; color: #64748b;
  border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.toggle-btn:hover { background: #e6f7ff; color: #1890ff; }
.toggle-btn .icon { width: 18px; height: 18px; }

/* --- 2. 导航内容 --- */
.nav-content { flex: 1; overflow-y: auto; overflow-x: hidden; }

/* 通用导航项 */
.nav-item {
  display: flex; align-items: center; padding: 12px;
  color: #555; border-radius: 10px; cursor: pointer; transition: 0.2s; margin-bottom: 5px;
  white-space: nowrap; /* 防止文字换行 */
}
.nav-item:hover { background: #f5f7fa; color: #333; }
.nav-item.active { background: #e6f7ff; color: #1890ff; font-weight: 600; }

.icon-wrapper { width: 24px; display: flex; justify-content: center; }
.nav-icon { width: 20px; height: 20px; }
.nav-text { margin-left: 12px; transition: opacity 0.2s; }

/* 新建按钮 */
.action-area { margin: 15px 0 20px 0; }
.new-chat-btn {
  width: 100%; padding: 12px; background: #1890ff; color: white; border: none; border-radius: 8px;
  cursor: pointer; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: 0.2s; white-space: nowrap; overflow: hidden;
}
.new-chat-btn:hover { background: #40a9ff; }
.plus-icon { font-size: 18px; line-height: 1; }

/* 历史列表 (收起时会被 v-show 隐藏) */
.history-group { margin-top: 10px; }
.group-title {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 5px;
  color: #999; font-size: 13px; cursor: pointer; white-space: nowrap;
}
.arrow { width: 16px; transition: transform 0.3s; }
.arrow.rotated { transform: rotate(180deg); }
.history-item {
  padding: 10px 12px; font-size: 14px; color: #666; cursor: pointer; border-radius: 6px;
  display: flex; align-items: center; gap: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.history-item:hover { background: #fafafa; }
.history-item.active { background: #f0f9ff; color: #1890ff; }
.dot { width: 6px; height: 6px; background: #ddd; border-radius: 50%; flex-shrink: 0; }
.history-item.active .dot { background: #1890ff; }
.empty-tip { font-size: 12px; color: #ccc; text-align: center; margin-top: 10px; }

/* --- 3. 底部 --- */
.sidebar-footer {
  margin-top: auto; padding-top: 15px; border-top: 1px solid #f0f0f0;
  text-align: center; color: #999; cursor: pointer; font-size: 14px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  white-space: nowrap;
}
.sidebar-footer:hover { color: #ff4d4f; }

/* =========================================
   🔥 折叠状态 (.collapsed) 的样式覆写
   ========================================= */
.sidebar-nav.collapsed {
  width: 72px; /* 收起后的宽度 */
  padding: 16px 12px; /* 调整内边距 */
}

/* 隐藏文字 */
.sidebar-nav.collapsed .logo-text,
.sidebar-nav.collapsed .nav-text,
.sidebar-nav.collapsed .btn-text,
.sidebar-nav.collapsed .logout-text {
  display: none;
  opacity: 0;
}

/* 调整布局居中 */
.sidebar-nav.collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}
.sidebar-nav.collapsed .icon-wrapper {
  margin: 0;
}
.sidebar-nav.collapsed .new-chat-btn {
  padding: 10px;
  border-radius: 50%; /* 变成圆形按钮 */
  width: 40px; height: 40px;
  margin: 0 auto; /* 居中 */
}
.sidebar-nav.collapsed .toggle-btn {
  margin: 0 auto; /* 按钮居中 */
}
.sidebar-nav.collapsed .sidebar-header {
  justify-content: center;
}
/* 收起时隐藏 Logo 盒子，只留 toggle 按钮 (或者你可以调整逻辑保留小图标) */
.sidebar-nav.collapsed .logo-box {
  display: none;
}
.sidebar-nav.collapsed .sidebar-footer {
  justify-content: center;
}
</style>
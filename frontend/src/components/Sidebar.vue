<template>
  <nav class="sidebar-nav glass-sidebar" :class="{ collapsed: isCollapsed }">
    
    <div class="sidebar-header">
      <transition name="fade">
        <div v-show="!isCollapsed" class="logo-box">
          <span class="logo-emoji">🧠</span>
          <h3 class="logo-text">AI 心灵伴侣</h3>
        </div>
      </transition>
      
      <div v-show="isCollapsed" class="logo-box-mini">
        <span class="logo-emoji">🧠</span>
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
      
      <div class="action-area">
        <button class="new-chat-btn pulse-hover" @click="handleNewChat" :class="{ 'collapsed-btn': isCollapsed }" :title="isCollapsed ? '新对话' : ''">
          <span class="plus-icon">✨</span>
          <span v-if="!isCollapsed" class="btn-text">开启新对话</span>
        </button>
      </div>

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
          <span v-show="!isCollapsed" class="nav-text">仪表盘</span>
        </transition>
      </div>
      
      <div class="history-group">
        <div v-show="!isCollapsed" class="group-title" @click="isHistoryOpen = !isHistoryOpen">
          <span>🕒 历史对话</span>
          <svg class="arrow" :class="{ rotated: isHistoryOpen }" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
        
        <div v-show="isCollapsed" class="divider"></div>

        <transition name="slide-fade">
          <div v-show="isHistoryOpen || isCollapsed" class="history-list">
            <div v-if="sessions.length === 0 && !isCollapsed" class="empty-tip">暂无记录</div>
            
            <div 
              v-for="item in sessions" 
              :key="item.id" 
              class="history-item"
              :class="{ active: currentSessionId == item.id }"
              @click="handleSelectSession(item.id)"
              :title="item.title"
            >
              <span class="session-icon">💬</span>
              <span v-show="!isCollapsed" class="title">{{ item.title || '未命名对话' }}</span>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <div class="sidebar-footer" @click="handleLogout" title="退出登录">
      <div class="footer-btn">
        <span class="logout-icon">🚪</span>
        <span v-show="!isCollapsed" class="logout-text">退出登录</span>
      </div>
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
const isCollapsed = ref(false);

const toggleSidebar = () => { isCollapsed.value = !isCollapsed.value; };

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
/* === 1. 玻璃态容器 === */
.glass-sidebar {
  width: 260px;
  height: 100%;
  background: transparent; 
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  color: var(--text-main); /* ✅ 使用全局文字色 */
}

/* === 2. Header === */
.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 24px; min-height: 40px;
}
.logo-box { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.logo-text { 
  margin: 0; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;
  color: var(--primary-color); /* ✅ 使用全局主色 */
}
.logo-emoji { font-size: 22px; }
.logo-box-mini { margin: 0 auto; font-size: 24px; }

/* 切换按钮 */
.toggle-btn {
  width: 32px; height: 32px;
  border: none; background: rgba(255,255,255,0.5); 
  border-radius: 50%; color: #64748b;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.toggle-btn:hover { 
  background: #fff; 
  color: var(--primary-color); /* ✅ 悬停变主色 */
  transform: scale(1.1); 
}
.toggle-btn .icon { width: 16px; height: 16px; }

/* === 3. 导航内容 === */
.nav-content { flex: 1; overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column; gap: 8px; }

/* 新建按钮 */
.action-area { margin-bottom: 16px; }
.new-chat-btn {
  width: 100%; padding: 12px; 
  background: var(--primary-gradient); /* ✅ 使用全局渐变 */
  color: white; border: none; border-radius: 12px;
  cursor: pointer; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.3s; white-space: nowrap;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3); /* ✅ 阴影跟随主色 */
}
.new-chat-btn:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.4); 
}
.new-chat-btn.collapsed-btn { width: 44px; height: 44px; padding: 0; border-radius: 50%; margin: 0 auto; }

/* 导航项 */
.nav-item {
  display: flex; align-items: center; padding: 10px 12px;
  color: #555; border-radius: 12px; cursor: pointer; transition: 0.2s;
  white-space: nowrap;
}
.nav-item:hover { 
  background: rgba(255,255,255,0.5); 
  color: var(--primary-color); /* ✅ 悬停变主色 */
}
.nav-item.active { 
  background: rgba(255,255,255,0.8); 
  color: var(--primary-color); /* ✅ 激活变主色 */
  font-weight: 600; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.icon-wrapper { width: 24px; display: flex; justify-content: center; margin-right: 12px; }
.nav-icon { width: 20px; height: 20px; }

/* 历史列表 */
.history-group { margin-top: 12px; flex: 1; display: flex; flex-direction: column; }
.group-title {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  color: #999; font-size: 12px; cursor: pointer; white-space: nowrap; font-weight: 600;
}
.arrow { width: 14px; transition: transform 0.3s; }
.arrow.rotated { transform: rotate(180deg); }

.history-list { overflow-y: auto; padding-right: 4px; }
.history-item {
  padding: 10px 12px; font-size: 14px; color: #666; cursor: pointer; border-radius: 10px;
  display: flex; align-items: center; gap: 10px; white-space: nowrap; overflow: hidden; margin-bottom: 2px;
  transition: all 0.2s;
}
.history-item:hover { background: rgba(255,255,255,0.4); transform: translateX(2px); }
.history-item.active { 
  background: rgba(var(--primary-rgb), 0.1); /* ✅ 激活背景变淡主色 */
  color: var(--primary-color); 
  font-weight: 500;
  border-left: 3px solid var(--primary-color); /* ✅ 左侧条 */
}
.session-icon { font-size: 16px; opacity: 0.7; }
.empty-tip { font-size: 12px; color: #ccc; text-align: center; margin-top: 20px; }
.divider { height: 1px; background: rgba(0,0,0,0.05); margin: 8px 0; }

/* === 4. Footer === */
.sidebar-footer { margin-top: auto; padding-top: 16px; }
.footer-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px; border-radius: 10px; color: #888; cursor: pointer;
  transition: 0.2s; white-space: nowrap;
}
.footer-btn:hover { 
  background: rgba(255, 77, 79, 0.1); 
  color: var(--danger-color); /* ✅ 使用危险色变量 */
}

/* === 5. 折叠适配 === */
.sidebar-nav.collapsed { width: 80px; padding: 20px 10px; }
.sidebar-nav.collapsed .nav-item { justify-content: center; padding: 12px 0; }
.sidebar-nav.collapsed .icon-wrapper { margin: 0; }
.sidebar-nav.collapsed .history-item { justify-content: center; padding: 12px 0; border-left: none; }
.sidebar-nav.collapsed .history-item.active { 
  background: rgba(var(--primary-rgb), 0.2); /* ✅ 折叠时背景稍微深一点 */
  border-radius: 12px; 
}
.sidebar-nav.collapsed .sidebar-header { justify-content: center; }
.sidebar-nav.collapsed .toggle-btn { margin: 0 auto; }

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.pulse-hover:hover { animation: pulse 1s infinite; }
@keyframes pulse { 
  0% { box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0.4); } 
  70% { box-shadow: 0 0 0 10px rgba(var(--primary-rgb), 0); } 
  100% { box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0); } 
}

/* 滚动条 */
.nav-content::-webkit-scrollbar { width: 4px; }
.nav-content::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 4px; }
.nav-content::-webkit-scrollbar-track { background: transparent; }
</style>
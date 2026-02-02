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
              <div class="item-content">
                <span class="session-icon">💬</span>
                <span v-show="!isCollapsed" class="title">{{ item.title || '未命名对话' }}</span>
              </div>

              <button 
                v-show="!isCollapsed" 
                class="delete-btn" 
                @click.stop="openDeleteConfirm(item.id)"
                title="删除会话"
              >
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
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

    <ConfirmModal 
      :visible="showDeleteModal" 
      title="删除确认"
      content="删除后，这段对话记忆将永远消失，确定要继续吗？"
      @confirm="executeDelete" 
      @cancel="showDeleteModal = false" 
    />

  </nav>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import { bus } from '../eventBus'; 

// ✨ 引入工具和组件
import { showToast } from '../utils/toast.js'; 
import ConfirmModal from './ConfirmModal.vue'; 

const router = useRouter();
const route = useRoute();

const sessions = ref([]);
const isHistoryOpen = ref(true);
const currentSessionId = ref(null);
const isCollapsed = ref(false);

// ✨ 弹窗状态管理
const showDeleteModal = ref(false);
const sessionToDelete = ref(null);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const toggleSidebar = () => { isCollapsed.value = !isCollapsed.value; };

const loadSessions = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) return;
  try {
    const res = await axios.get(`${API_BASE}/api/sessions?user_id=${userId}`);
    sessions.value = res.data;
  } catch (e) { console.error("加载侧边栏失败:", e); }
};

const handleSelectSession = (id) => {
  currentSessionId.value = id;
  router.push(`/chat?session_id=${id}`);
};

const handleNewChat = () => {
  currentSessionId.value = null;
  router.push('/chat');
};

// ✨ 修改点 3：打开弹窗，而不是直接删除
const openDeleteConfirm = (sessionId) => {
  sessionToDelete.value = sessionId;
  showDeleteModal.value = true;
};

// ✨ 修改点 4：执行删除逻辑 (接入 Toast)
const executeDelete = async () => {
  if (!sessionToDelete.value) return;
  
  const sessionId = sessionToDelete.value;
  showDeleteModal.value = false; // 先关弹窗

  try {
    await axios.delete(`${API_BASE}/api/sessions/${sessionId}`);
    
    // 从 UI 移除
    sessions.value = sessions.value.filter(s => s.id !== sessionId);

    // 如果删的是当前会话，跳走
    if (currentSessionId.value == sessionId) {
      handleNewChat();
    }

    // 🎉 成功提示
    showToast('删除成功', 'success');

  } catch (e) {
    console.error("删除失败:", e);
    // ❌ 失败提示
    showToast('删除失败，请稍后重试', 'error');
  }
};

const handleLogout = () => {
  localStorage.removeItem('user_id');
  localStorage.removeItem('username');
  router.push('/login');
  // 💡 退出提示
  showToast('已退出登录', 'info');
};

watch(() => bus.refreshSessions, () => loadSessions());
watch(() => route.query.session_id, (val) => {
  currentSessionId.value = val || null;
}, { immediate: true });

onMounted(() => loadSessions());
</script>

<style scoped>
/* 样式保持不变，完美复用之前的 */
.glass-sidebar {
  width: 260px;
  height: 100%;
  background: transparent; 
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  color: var(--text-main); 
}

.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 24px; min-height: 40px;
}
.logo-box { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.logo-text { 
  margin: 0; font-size: 18px; font-weight: 700; letter-spacing: 0.5px;
  color: var(--primary-color);
}
.logo-emoji { font-size: 22px; }
.logo-box-mini { margin: 0 auto; font-size: 24px; }

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
  color: var(--primary-color);
  transform: scale(1.1); 
}
.toggle-btn .icon { width: 16px; height: 16px; }

.nav-content { flex: 1; overflow-y: auto; overflow-x: hidden; display: flex; flex-direction: column; gap: 8px; }

.action-area { margin-bottom: 16px; }
.new-chat-btn {
  width: 100%; padding: 12px; 
  background: var(--primary-gradient); 
  color: white; border: none; border-radius: 12px;
  cursor: pointer; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.3s; white-space: nowrap;
  box-shadow: 0 4px 12px rgba(var(--primary-rgb), 0.3);
}
.new-chat-btn:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 6px 16px rgba(var(--primary-rgb), 0.4); 
}
.new-chat-btn.collapsed-btn { width: 44px; height: 44px; padding: 0; border-radius: 50%; margin: 0 auto; }

.nav-item {
  display: flex; align-items: center; padding: 10px 12px;
  color: #555; border-radius: 12px; cursor: pointer; transition: 0.2s;
  white-space: nowrap;
}
.nav-item:hover { 
  background: rgba(255,255,255,0.5); 
  color: var(--primary-color);
}
.nav-item.active { 
  background: rgba(255,255,255,0.8); 
  color: var(--primary-color);
  font-weight: 600; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.icon-wrapper { width: 24px; display: flex; justify-content: center; margin-right: 12px; }
.nav-icon { width: 20px; height: 20px; }

.history-group { margin-top: 12px; flex: 1; display: flex; flex-direction: column; }
.group-title {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
  color: #999; font-size: 12px; cursor: pointer; white-space: nowrap; font-weight: 600;
}
.arrow { width: 14px; transition: transform 0.3s; }
.arrow.rotated { transform: rotate(180deg); }

.history-list { overflow-y: auto; padding-right: 4px; }

.history-item {
  padding: 10px 12px; 
  font-size: 14px; color: #666; 
  cursor: pointer; border-radius: 10px; 
  display: flex; align-items: center; justify-content: space-between;
  white-space: nowrap; overflow: hidden; margin-bottom: 2px; 
  transition: all 0.2s;
  position: relative;
}
.history-item:hover { background: rgba(255,255,255,0.4); transform: translateX(2px); }
.history-item.active { 
  background: rgba(var(--primary-rgb), 0.1); 
  color: var(--primary-color); 
  font-weight: 500; 
  border-left: 3px solid var(--primary-color); 
}

.item-content { display: flex; align-items: center; gap: 10px; overflow: hidden; flex: 1; }
.session-icon { font-size: 16px; opacity: 0.7; }
.title { overflow: hidden; text-overflow: ellipsis; }

.delete-btn {
  background: transparent; border: none; color: #999;
  cursor: pointer; padding: 4px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; 
  transition: all 0.2s;
}
.delete-btn:hover { background: #fee2e2; color: #ef4444; } 
.history-item:hover .delete-btn { opacity: 1; }

.empty-tip { font-size: 12px; color: #ccc; text-align: center; margin-top: 20px; }
.divider { height: 1px; background: rgba(0,0,0,0.05); margin: 8px 0; }

.sidebar-footer { margin-top: auto; padding-top: 16px; }
.footer-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px; border-radius: 10px; color: #888; cursor: pointer;
  transition: 0.2s; white-space: nowrap;
}
.footer-btn:hover { 
  background: rgba(255, 77, 79, 0.1); 
  color: var(--danger-color);
}

.sidebar-nav.collapsed { width: 80px; padding: 20px 10px; }
.sidebar-nav.collapsed .nav-item { justify-content: center; padding: 12px 0; }
.sidebar-nav.collapsed .icon-wrapper { margin: 0; }
.sidebar-nav.collapsed .history-item { justify-content: center; padding: 12px 0; border-left: none; }
.sidebar-nav.collapsed .history-item.active { 
  background: rgba(var(--primary-rgb), 0.2);
  border-radius: 12px; 
}
.sidebar-nav.collapsed .sidebar-header { justify-content: center; }
.sidebar-nav.collapsed .toggle-btn { margin: 0 auto; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.pulse-hover:hover { animation: pulse 1s infinite; }
@keyframes pulse { 
  0% { box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0.4); } 
  70% { box-shadow: 0 0 0 10px rgba(var(--primary-rgb), 0); } 
  100% { box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0); } 
}

.nav-content::-webkit-scrollbar { width: 4px; }
.nav-content::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 4px; }
.nav-content::-webkit-scrollbar-track { background: transparent; }
</style>
<template>
  <nav class="sidebar-nav">
    <div class="logo">
      <div class="logo-icon">🧠</div> <h3>AI 心灵伴侣</h3>
    </div>
    
    <ul class="nav-list">
      <li class="nav-item">
        <router-link to="/home">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span>仪表盘</span>
        </router-link>
      </li>
      
      <li class="nav-item">
        <router-link to="/chat">
          <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span>开始新对话</span>
        </router-link>
      </li>

      <li class="nav-item expandable">
        <a @click="toggleHistory" class="expand-toggle" :class="{ 'active': isHistoryOpen }">
          <div class="toggle-content">
            <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>历史对话</span>
          </div>
          <svg class="arrow" :class="{ 'arrow-down': isHistoryOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </a>
        
        <div v-if="isHistoryOpen" class="submenu">
          <HistoryList />
        </div>
      </li>
    </ul>

    <div class="sidebar-footer">
      <router-link to="/help" class="help-link">
        <svg class="mini-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        使用指引 & 申诉
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import HistoryList from './HistoryList.vue'; 

const isHistoryOpen = ref(true); 

const toggleHistory = () => {
  isHistoryOpen.value = !isHistoryOpen.value;
};
</script>

<style scoped>
.sidebar-nav {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 16px;
  background-color: #ffffff;
  /* 字体优化 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 8px 20px 8px;
  margin-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.logo-icon {
  font-size: 24px;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1890ff; /* 品牌色 */
  letter-spacing: 0.5px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto; /* 防止导航太长溢出 */
}

.nav-item {
  margin-bottom: 6px;
}

/* 链接基础样式 */
.nav-item a, .expand-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 箭头靠右 */
  padding: 12px;
  text-decoration: none;
  color: #555;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  user-select: none;
}

.toggle-content {
  display: flex;
  align-items: center;
}

/* 图标样式 */
.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: #888;
  transition: color 0.2s;
}

/* 悬停效果 */
.nav-item a:hover, .expand-toggle:hover {
  background-color: #f5f7fa;
  color: #333;
}
.nav-item a:hover .nav-icon, .expand-toggle:hover .nav-icon {
  color: #1890ff;
}

/* 激活状态 (Vue Router 自动添加) */
.nav-item a.router-link-active {
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: 600;
}
.nav-item a.router-link-active .nav-icon {
  color: #1890ff;
}

/* 折叠箭头 */
.arrow {
  width: 16px;
  height: 16px;
  color: #ccc;
  transition: transform 0.3s ease;
}
.arrow-down {
  transform: rotate(90deg);
}

/* 子菜单样式 */
.submenu {
  margin-top: 4px;
  padding-left: 12px; /* 缩进 */
  /* 可以添加一个淡入动画 */
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 底部 Footer */
.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

.help-link {
  font-size: 12px;
  color: #999;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: color 0.2s;
}
.help-link:hover {
  color: #1890ff;
}
.mini-icon {
  width: 14px;
  height: 14px;
}
</style>
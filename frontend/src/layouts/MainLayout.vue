<template>
  <div class="main-layout">
    <aside class="layout-sidebar glass-panel-left">
      <Sidebar />
    </aside>

    <main class="layout-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <aside class="layout-aside glass-panel-right">
      <AsidePanel />
    </aside>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue';
import AsidePanel from '@/components/AsidePanel.vue';
</script>

<style scoped>
/* === 1. 布局容器 === */
.main-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  /* ✨ 核心：透明背景，让 App.vue 的渐变透出来 */
  background-color: transparent; 
}

/* === 2. 左侧侧边栏 (玻璃特效) === */
.layout-sidebar {
  flex: 0 0 auto;
  width: auto;
  z-index: 10;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}

.glass-panel-left {
  /* ✨ 优化：使用全局变量，方便统一调整透明度 */
  background: var(--glass-bg); 
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.02);
}

/* === 3. 中间内容区 === */
.layout-content {
  flex: 1;
  padding: 0; /* 全屏布局 */
  overflow-y: auto;
  position: relative;
  transition: all 0.3s ease;
  scrollbar-width: none; 
}
.layout-content::-webkit-scrollbar {
  display: none;
}

/* === 4. 右侧辅助栏 (玻璃特效) === */
.layout-aside {
  flex: 0 0 280px;
  z-index: 5;
  padding: 24px;
  overflow-y: auto;
}

.glass-panel-right {
  /* ✨ 优化：右侧稍微淡一点，突出中间内容 */
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.02);
}

/* === 5. 响应式适配 === */
@media (max-width: 1200px) {
  .layout-aside { display: none; }
}

@media (max-width: 768px) {
  .layout-sidebar { display: none; }
  .layout-content { width: 100%; }
}

/* 页面切换动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
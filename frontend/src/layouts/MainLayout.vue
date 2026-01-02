<template>
  <div class="main-layout">
    <aside class="layout-sidebar">
      <Sidebar />
    </aside>

    <main class="layout-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <aside class="layout-aside">
      <AsidePanel />
    </aside>
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue';
import AsidePanel from '@/components/AsidePanel.vue';
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #f4f7f9;
}

/* 🔥 关键修改：取消固定宽度，让它随子组件 Sidebar 自动伸缩 */
.layout-sidebar {
  flex: 0 0 auto; /* 宽度由内容决定 */
  width: auto;
  background-color: #ffffff;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
  z-index: 10;
  display: flex;
  flex-direction: column;
  /* 加上过渡动画，配合 Sidebar 的收缩 */
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}

.layout-content {
  flex: 1; /* 自动占满剩余空间 */
  padding: 24px 32px;
  overflow-y: auto;
  position: relative;
  /* 让右侧内容的挤压也带有平滑动画 */
  transition: all 0.3s ease;
}

.layout-aside {
  flex: 0 0 280px;
  background-color: #ffffff;
  padding: 24px;
  border-left: 1px solid #f0f0f0;
  overflow-y: auto;
  z-index: 5;
}

/* --- 📱 响应式适配 --- */
@media (max-width: 1200px) {
  .layout-aside { display: none; }
}

@media (max-width: 768px) {
  .layout-sidebar { display: none; }
  .layout-content { padding: 16px; }
}

/* 滚动条美化 */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #dcdfe6; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #c0c4cc; }

/* 页面切换动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
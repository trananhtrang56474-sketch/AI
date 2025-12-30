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
  overflow: hidden; /* 防止整个页面出现双滚动条 */
  background-color: #f4f7f9;
}

.layout-sidebar {
  flex: 0 0 220px; /* 左侧固定宽度 */
  background-color: #ffffff;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03); /* 更柔和的阴影 */
  z-index: 10;
  display: flex;
  flex-direction: column;
}

.layout-content {
  flex: 1; /* 占据剩余空间 */
  padding: 24px 32px;
  overflow-y: auto; /* 内容区独立滚动 */
  position: relative;
}

.layout-aside {
  flex: 0 0 280px; /* 右侧固定宽度 */
  background-color: #ffffff;
  padding: 24px;
  border-left: 1px solid #f0f0f0;
  overflow-y: auto; /* 右侧独立滚动 */
  z-index: 5;
}

/* --- 📱 响应式适配 --- */

/* 当屏幕宽度小于 1200px (普通笔记本) 时，隐藏右侧栏 */
@media (max-width: 1200px) {
  .layout-aside {
    display: none;
  }
}

/* 当屏幕宽度小于 768px (手机/平板) 时，隐藏左侧栏(变成单页应用模式)，调整内边距 */
@media (max-width: 768px) {
  .layout-sidebar {
    display: none; /* 实际项目中通常会变成汉堡菜单，这里暂时隐藏 */
  }
  .layout-content {
    padding: 16px; /* 减小手机上的内边距 */
  }
}

/* --- 🎨 滚动条美化 (Webkit内核: Chrome, Edge, Safari) --- */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* --- 页面切换动画 (可选) --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
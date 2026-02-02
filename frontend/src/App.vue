<template>
  <div class="app-layout">
    <div class="global-background-layer"></div>

    <GlobalToast />

    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        
        <keep-alive include="ChatPage">
          <component :is="Component" />
        </keep-alive>
        
      </transition>
    </router-view>
  </div>
</template>

<script setup>
// ✨ 引入全局提示组件
import GlobalToast from '@/components/GlobalToast.vue';
</script>

<style>
/* === 1. 全局变量定义 (中央调色板) === */
:root {
  /* --- 🎨 主色调 (核心) --- */
  --primary-color: #764ba2; /* 治愈紫 */
  
  /* 主色的 RGB 值 (用于 rgba 透明度计算) */
  --primary-rgb: 118, 75, 162; 

  /* 渐变色 */
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  /* --- 🌈 状态色 --- */
  --success-color: #52c41a; /* 绿色 - 平静 */
  --warning-color: #fa8c16; /* 橙色 - 焦虑 */
  --danger-color:  #ff4d4f; /* 红色 - 危机 */

  /* --- 📄 文字颜色 --- */
  --text-main: #2c3e50;
  --text-sub:  #718096;

  /* --- 🪟 玻璃质感标准 --- */
  --glass-bg: rgba(255, 255, 255, 0.4);
  --glass-border: 1px solid rgba(255, 255, 255, 0.6);
  --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
}

/* === 2. 基础重置 === */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
 
  color: var(--text-main);
  overflow: hidden; /* 防止双重滚动条 */
}

#app { width: 100%; height: 100%; }

.app-layout {
  position: relative;
  width: 100%; height: 100%;
  overflow: hidden; 
}

* { box-sizing: border-box; }

/* === 3. 全局动态背景 (暖阳呼吸) === */
.global-background-layer {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  /* 柔和的粉紫蓝渐变循环 */
  background: linear-gradient(-45deg, #fff1eb, #ace0f9, #fff1eb);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  z-index: -1; 
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* === 4. 全局滚动条美化 === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  transition: background 0.3s;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0, 0, 0, 0.2); }

/* === 5. ✨ 页面丝滑转场动画 (Page Fade) === */
/* 进入和离开的过渡状态 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 进入前状态：稍微缩小 + 下沉 + 透明 */
.page-fade-enter-from {
  opacity: 0;
  transform: scale(0.96) translateY(15px);
}

/* 离开后状态：稍微放大 + 透明 */
.page-fade-leave-to {
  opacity: 0;
  transform: scale(1.02);
}
</style>
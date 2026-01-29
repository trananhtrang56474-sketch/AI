<template>
  <div class="app-layout">
    <div class="global-background-layer"></div>

    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
// 逻辑层保持干净，样式全靠 CSS
</script>

<style>
/* === 1. 全局变量定义 (中央调色板) === */
:root {
  /* --- 🎨 主色调 (核心) --- */
  /* 想要换肤，改这里就行 */
  --primary-color: #764ba2; /* 治愈紫 */
  
  /* ✨ 新增：主色的 RGB 值 (用于 rgba 透明度计算) */
  /* 比如：background: rgba(var(--primary-rgb), 0.1); */
  --primary-rgb: 118, 75, 162; 

  /* 渐变色 */
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  /* --- 🌈 状态色 (用于标签、图表) --- */
  --success-color: #52c41a; /* 绿色 - 平静 */
  --warning-color: #fa8c16; /* 橙色 - 焦虑 */
  --danger-color:  #ff4d4f; /* 红色 - 危机 */

  /* --- 📄 文字颜色 --- */
  --text-main: #2c3e50;
  --text-sub:  #718096;

  /* --- 🪟 玻璃质感标准 --- */
  --glass-bg: rgba(255, 255, 255, 0.);
  --glass-border: 1px solid rgba(255, 255, 255, 0.6);
  --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
}

/* === 2. 基础重置 === */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  /* 使用系统级字体，清晰现代 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased; /* Mac字体抗锯齿 */
  -moz-osx-font-smoothing: grayscale;
 
  color: var(--text-main);
  overflow: hidden; /* 防止双重滚动条 */
}

#app {
  width: 100%;
  height: 100%;
}

.app-layout {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden; /* 确保背景不溢出 */
}

* {
  box-sizing: border-box;
}

/* === 3. 全局动态背景 (暖阳呼吸) === */
.global-background-layer {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  /* 柔和的粉紫蓝渐变循环 */
  background: linear-gradient(-45deg, #fff1eb, #ace0f9, #fff1eb);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
  z-index: -1; /* 永远在最底层 */
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* === 4. 全局滚动条美化 (Webkit) === */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  transition: background 0.3s;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2); /* 悬停加深 */
}

/* === 5. 页面切换动画 (Fade) === */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
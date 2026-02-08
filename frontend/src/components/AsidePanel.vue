<template>
  <div class="aside-panel">
    
    <transition name="fade-slide">
      <div 
        class="aside-card glass-card psych-card clickable" 
        v-if="analysis.emotion"
        @click="showPortraitModal = true"
      >
        <div class="card-header">
          <div class="header-left">
            <span class="icon-circle">🧠</span>
            <h3>心理映像</h3>
          </div>
          <span class="live-badge">✨ 展开</span>
        </div>
        
        <div class="monitor-grid">
          <div class="monitor-row">
            <span class="label">当前主导情绪</span>
            <span class="value" :style="{ color: emotionColor }">{{ analysis.emotion }}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ backgroundColor: emotionColor, width: (analysis.score || 60) + '%' }"></div>
          </div>
        </div>
        <div class="hover-hint">点击解读 👉</div>
      </div>
    </transition>

    <div class="aside-card glass-card emergency-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle alert-bg">🆘</span>
          <h3 class="alert-text">紧急帮助</h3>
        </div>
      </div>
      <a href="tel:12345678" class="emergency-btn">拨打援助热线</a>
    </div>

    <div class="aside-card glass-card toolbox-card clickable" @click="showToolboxModal = true">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle tool-icon">🧰</span>
          <h3>心理工具箱</h3>
        </div>
        <span class="arrow-icon">→</span>
      </div>
      <p class="toolbox-desc">
        心理调节工具<br>
        <span class="sub-desc">无需“情况严重”才能使用 💙</span>
      </p>
    </div>

    <PsychPortraitModal 
      :show="showPortraitModal" 
      :analysis="analysis"
      @close="showPortraitModal = false"
    />

    <PsychToolboxModal
      :show="showToolboxModal"
      @close="showToolboxModal = false"
    />

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { authStore as store } from '../store.js';

// 引入刚刚创建的两个组件
import PsychPortraitModal from './PsychPortraitModal.vue';
import PsychToolboxModal from './PsychToolboxModal.vue';

const showPortraitModal = ref(false);
const showToolboxModal = ref(false);

const analysis = computed(() => store.analysisState || {});

const emotionColor = computed(() => {
  const map = { '危机': '#ff4d4f', '愤怒': '#ff7875', '焦虑': '#fa8c16', '抑郁': '#8c8c8c', '平静': '#52c41a', '积极': '#fadb14' };
  return map[analysis.value.emotion] || '#722ed1';
});
</script>

<style scoped>
.aside-panel { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: var(--glass-bg); backdrop-filter: blur(12px); border: var(--glass-border); border-radius: 16px; padding: 18px; box-shadow: var(--glass-shadow); transition: all 0.3s; position: relative; overflow: hidden; }
.clickable { cursor: pointer; }
.clickable:hover { transform: translateY(-4px) scale(1.02); background: rgba(255, 255, 255, 0.9); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-left h3 { margin: 0; font-size: 15px; color: var(--text-main); font-weight: 600; }
.icon-circle { width: 28px; height: 28px; background: rgba(255,255,255,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.psych-card { background: linear-gradient(145deg, var(--glass-bg) 0%, rgba(var(--primary-rgb), 0.08) 100%); }
.live-badge { background: var(--primary-gradient); color: white; font-size: 11px; padding: 4px 10px; border-radius: 20px; font-weight: 500; }
.monitor-grid { display: flex; flex-direction: column; }
.monitor-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.label { color: var(--text-sub); }
.value { font-weight: 600; }
.progress-bar-bg { width: 100%; height: 6px; background: rgba(0,0,0,0.05); border-radius: 3px; margin-top: 6px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.hover-hint { position: absolute; right: 15px; bottom: 15px; opacity: 0; transform: translateX(-10px); transition: 0.3s; font-size: 12px; color: var(--primary-color); font-weight: bold; background: rgba(255,255,255,0.8); padding: 4px 8px; border-radius: 4px; }
.psych-card:hover .hover-hint { opacity: 1; transform: translateX(0); }
.emergency-card { background: rgba(255, 241, 240, 0.65); border-color: rgba(255, 204, 199, 0.5); }
.alert-bg { background: rgba(255, 77, 79, 0.1); }
.alert-text { color: var(--danger-color); }
.emergency-btn { display: block; width: 100%; text-align: center; padding: 8px 0; background: var(--danger-color); color: white; border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: 500; }
.toolbox-card { padding: 18px; }
.tool-icon { background: rgba(250, 173, 20, 0.1); }
.arrow-icon { font-weight: bold; color: #ccc; }
.toolbox-desc { font-size: 12px; color: #888; margin: 0; }
.sub-desc { font-size: 11px; color: #999; display: block; margin-top: 4px; }
</style>
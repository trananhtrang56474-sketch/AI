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
            <span class="icon-circle"></span>
            <h3>心理映像</h3>
          </div>
          <span class="live-badge">✨ 展开</span>
        </div>
        <div class="monitor-grid">
          <div class="monitor-row">
            <span class="label">当前实时情绪</span>
            <span class="value" :style="{ color: emotionColor }">{{ analysis.emotion }}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ backgroundColor: emotionColor, width: (analysis.score || 60) + '%' }"></div>
          </div>
        </div>
       
      </div>
    </transition>

    <div class="aside-card glass-card growth-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle growth-icon">📈</span>
          <h3>成长记录</h3>
        </div>
      </div>
      <div class="growth-stats">
        <div class="stat-box">
          <span class="stat-value">{{ userStats.days }}<small>天</small></span>
          <span class="stat-name">陪伴</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-box">
          <span class="stat-value">{{ userStats.diary }}<small>篇</small></span>
          <span class="stat-name">日记</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-box">
          <span class="stat-value">{{ userStats.meditation }}<small>次</small></span>
          <span class="stat-name">练习</span>
        </div>
      </div>
    </div>

    <div class="aside-card glass-card emergency-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle alert-bg">🆘</span>
          <h3 class="alert-text">紧急帮助</h3>
        </div>
      </div>
      <a href="tel:12345678" class="emergency-btn">拨打援助热线</a>
    </div>

    <div class="aside-card glass-card toolbox-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle tool-icon">🧰</span>
          <h3>心理工具箱</h3>
        </div>
      </div>
      <div class="tool-list">
        <button class="tool-btn" @click="router.push('/article/1')">
          <div class="btn-icon-wrapper info-bg"><span class="btn-icon">📚</span></div>
          <div class="btn-text">
            <span class="btn-title">心理百科</span>
            <span class="btn-desc">探索心理学知识库</span>
          </div>
        </button>

        <button class="tool-btn" @click="router.push('/meditation')">
          <div class="btn-icon-wrapper success-bg"><span class="btn-icon">🧘</span></div>
          <div class="btn-text">
            <span class="btn-title">冥想练习</span>
            <span class="btn-desc">5分钟放松引导练习</span>
          </div>
        </button>
        
        <button class="tool-btn" @click="router.push('/diary')">
          <div class="btn-icon-wrapper warning-bg"><span class="btn-icon">📝</span></div>
          <div class="btn-text">
            <span class="btn-title">情绪日记</span>
            <span class="btn-desc">记录当下真实的心情</span>
          </div>
        </button>

        <button class="tool-btn" @click="showToolboxModal = true">
          <div class="btn-icon-wrapper primary-bg"><span class="btn-icon">🔧</span></div>
          <div class="btn-text">
            <span class="btn-title">应急调节</span>
            <span class="btn-desc">快捷心理调节指南</span>
          </div>
        </button>
      </div>
    </div>

    <PsychPortraitModal 
      :show="showPortraitModal" 
      :analysis="analysis" 
      :chart-data="historyChartData" 
      @close="showPortraitModal = false" 
    />
    <PsychToolboxModal :show="showToolboxModal" @close="showToolboxModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'; // ✨ 引入 onMounted
import { useRouter } from 'vue-router';
import axios from 'axios'; // ✨ 引入 axios
import { authStore as store } from '../store.js';

import PsychPortraitModal from './PsychPortraitModal.vue';
import PsychToolboxModal from './PsychToolboxModal.vue';

// ✨ 配置接口基础地址
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

const router = useRouter();
const showPortraitModal = ref(false);
const showToolboxModal = ref(false);

const analysis = computed(() => store.analysisState || {});
const userStats = ref({ days: 12, diary: 8, meditation: 5 });

const emotionColor = computed(() => {
  const map = { '危机': '#ff4d4f', '愤怒': '#ff7875', '焦虑': '#fa8c16', '抑郁': '#8c8c8c', '平静': '#52c41a', '积极': '#fadb14' };
  return map[analysis.value.emotion] || '#722ed1';
});

// ==========================================
// ✨ 核心逻辑：获取当前用户的真实图表数据
// ==========================================
const historyChartData = ref({ dates: [], scores: [], arousals: [], valences: [], tags: [], contents: [] });

const fetchChartData = async () => {
  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;
    
    // 调用后端我们写好的那个返回完整双维度数据的接口
    const res = await axios.get(`${API_BASE}/api/chart-data?user_id=${userId}`);
    if (res.data && res.data.scores) {
      historyChartData.value = res.data;
    }
  } catch (error) {
    console.error("弹窗图表数据获取失败:", error);
  }
};

// 组件挂载时自动获取数据
onMounted(() => {
  fetchChartData();
});
</script>

<style scoped>
/* 保持原有AsidePanel样式，新增info-bg配色 */
.aside-panel { display: flex; flex-direction: column; gap: 16px; } 
.glass-card { background: var(--glass-bg); backdrop-filter: blur(12px); border: var(--glass-border); border-radius: 16px; padding: 18px; box-shadow: var(--glass-shadow); transition: all 0.3s; position: relative; overflow: hidden; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.header-left { display: flex; align-items: center; gap: 8px; }
.header-left h3 { margin: 0; font-size: 15px; color: var(--text-main); font-weight: 600; }
.icon-circle { width: 28px; height: 28px; background: rgba(255,255,255,0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; }

/* 心理工具列表样式 */
.tool-list { display: flex; flex-direction: column; gap: 10px; margin-top: 8px; }
.tool-btn { 
  display: flex; align-items: center; gap: 12px; padding: 10px 14px; 
  background: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.8); 
  border-radius: 14px; cursor: pointer; transition: all 0.2s; text-align: left;
}
.tool-btn:hover { background: white; transform: translateX(4px); border-color: var(--primary-color); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.btn-icon-wrapper { width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.info-bg { background: rgba(0, 145, 255, 0.1); }
.success-bg { background: rgba(82, 196, 26, 0.1); }
.warning-bg { background: rgba(250, 140, 22, 0.1); }
.primary-bg { background: rgba(118, 75, 162, 0.1); }

.btn-text { display: flex; flex-direction: column; }
.btn-title { font-size: 13px; font-weight: 600; color: var(--text-main); }
.btn-desc { font-size: 11px; color: var(--text-sub); }

/* 原有卡片交互样式 */
.psych-card.clickable { cursor: pointer; border: 1px solid rgba(123, 97, 255, 0.2); }
.psych-card.clickable:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(123, 97, 255, 0.15); border-color: var(--primary-color); }
.live-badge { font-size: 11px; font-weight: bold; color: var(--primary-color); background: rgba(123, 97, 255, 0.1); padding: 3px 8px; border-radius: 12px; }
.hover-hint { position: absolute; right: -100px; bottom: 15px; font-size: 12px; color: white; background: var(--primary-gradient); padding: 4px 12px; border-radius: 20px 0 0 20px; transition: 0.3s; font-weight: bold; }
.psych-card.clickable:hover .hover-hint { right: 0; }

.monitor-grid { background: rgba(255, 255, 255, 0.4); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.5); }
.monitor-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; margin-bottom: 8px; }
.label { color: var(--text-sub); font-weight: 500; }
.value { font-weight: 600; font-size: 14px; }

.progress-bar-bg { width: 100%; height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease, background-color 0.4s; }

/* 其余卡片样式保持不变... */
.growth-stats { display: flex; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.4); padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.5); }
.stat-box { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--primary-color); display: flex; align-items: baseline; gap: 2px; line-height: 1; }
.stat-name { font-size: 11px; color: var(--text-sub); }
.stat-divider { width: 1px; height: 20px; background: rgba(0, 0, 0, 0.05); }
.emergency-card { background: rgba(255, 241, 240, 0.65); border-color: rgba(255, 204, 199, 0.5); }
.emergency-btn { display: block; width: 100%; text-align: center; padding: 8px 0; background: var(--danger-color); color: white; border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: 500; }
</style>
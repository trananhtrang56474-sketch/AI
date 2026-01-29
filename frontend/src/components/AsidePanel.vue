<template>
  <div class="aside-panel">
    
    <transition name="fade-slide">
      <div class="aside-card glass-card psych-card" v-if="analysis.emotion">
        <div class="card-header">
          <div class="header-left">
            <span class="icon-circle">🧠</span>
            <h3>心理映像</h3>
          </div>
          <span class="live-badge">LIVE</span>
        </div>
        
        <div class="monitor-grid">
          <div class="monitor-row">
            <span class="label">当前情绪</span>
            <span class="value" :style="{ color: emotionColor }">{{ analysis.emotion }}</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ backgroundColor: emotionColor, width: '60%' }"></div>
          </div>
          
          <div class="monitor-row mt-3">
            <span class="label">AI 策略</span>
            <span class="value strategy-text">{{ strategyName }}</span>
          </div>
          
          <div class="monitor-row mt-2">
            <span class="label">趋势</span>
            <span class="value trend-text">{{ trendName }}</span>
          </div>
        </div>
      </div>
    </transition>

    <div class="aside-card glass-card emergency-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle alert-bg">🆘</span>
          <h3 class="alert-text">紧急帮助</h3>
        </div>
      </div>
      <p class="emergency-desc">如果你正处于危机中，请不要独自承受。</p>
      <a href="tel:12345678" class="emergency-btn">
        拨打援助热线
      </a>
    </div>

    <div class="aside-card glass-card info-card">
      <div class="card-header">
        <div class="header-left">
          <span class="icon-circle">📚</span>
          <h3>资源与教程</h3>
        </div>
      </div>
      <ul class="link-list">
        <li><a href="#">如何理解情绪图表？</a></li>
        <li><a href="#">正念呼吸 5 步法</a></li>
        <li><a href="#">推荐：中国心理卫生协会</a></li>
      </ul>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { authStore as store } from '../store.js';

const analysis = computed(() => store.analysisState || {});

const emotionColor = computed(() => {
  // 💡 注意：情绪颜色通常是固定的（比如愤怒是红，平静是绿）
  // 不建议随主题变色，否则会失去语义
  const map = {
    '危机': '#ff4d4f', '愤怒': '#ff7875', '焦虑': '#fa8c16',
    '抑郁': '#8c8c8c', '悲伤': '#69c0ff', '愧疚': '#b37feb',
    '迷茫': '#85a5ff', '积极': '#fadb14', '平静': '#52c41a'
  };
  // ✅ 修正：兜底颜色改为透明或默认文本色，避免出现突兀的蓝
  return map[analysis.value.emotion] || '#764ba2'; 
});

const strategyName = computed(() => {
  const map = {
    "CRISIS_INTERVENTION": "🚨 危机干预", "DEEP_VALIDATION": "❤️ 深度共情",
    "EMPATHY_SUPPORT": "🤝 情感支持", "COGNITIVE_RESTRUCTURING": "🧠 认知重构",
    "DISTRESS_TOLERANCE": "🛡️ 痛苦耐受", "DE_ESCALATION": "🧊 情绪降温",
    "STRENGTH_BUILDING": "🌟 优势探索", "GENERAL_SUPPORT": "☕ 一般陪伴",
    "VISUAL_ANALYSIS": "👁️ 视觉分析"
  };
  return map[analysis.value.strategy] || "一般陪伴";
});

const trendName = computed(() => {
  const map = {
    "FIRST_CONTACT": "初次接触", "FLUCTUATING": "波动中 ~",
    "IMPROVING": "正在好转 📈", "WORSENING": "需关注 📉",
    "PERSISTENT_NEGATIVE": "持续低落 🌧️"
  };
  return map[analysis.value.trend] || "分析中...";
});
</script>

<style scoped>
.aside-panel {
  display: flex; flex-direction: column; gap: 20px;
}

/* === 通用玻璃卡片 === */
.glass-card {
  background: var(--glass-bg); 
  backdrop-filter: blur(12px);
  border: var(--glass-border); 
  border-radius: 16px;
  padding: 18px;
  box-shadow: var(--glass-shadow); 
  transition: transform 0.2s;
}
.glass-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.8);
}

/* Header */
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.header-left h3 { margin: 0; font-size: 15px; color: var(--text-main); font-weight: 600; }
.icon-circle {
  width: 28px; height: 28px; background: rgba(255,255,255,0.6);
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px;
}

/* === 1. 心理映像卡片 === */
.psych-card {
  /* ✅ 关键：使用 var(--primary-rgb) 让光晕随主题变色 */
  background: linear-gradient(145deg, var(--glass-bg) 0%, rgba(var(--primary-rgb), 0.08) 100%);
}
.live-badge {
  background: var(--danger-color); color: white; font-size: 10px; padding: 2px 6px; border-radius: 4px;
  font-weight: bold; animation: pulse 2s infinite;
}
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

.monitor-grid { display: flex; flex-direction: column; }
.monitor-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.label { color: var(--text-sub); }
.value { font-weight: 600; }

.strategy-text { color: var(--primary-color); /* ✅ 随主题变 */ }
.trend-text { color: var(--primary-color); /* ✅ 修正：随主题变，不再是死板的蓝色 */ }

.mt-3 { margin-top: 12px; }
.mt-2 { margin-top: 8px; }

/* 进度条 */
.progress-bar-bg {
  width: 100%; height: 6px; background: rgba(0,0,0,0.05); border-radius: 3px;
  margin-top: 6px; overflow: hidden;
}
.progress-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }

/* === 2. 紧急卡片 === */
.emergency-card {
  background: rgba(255, 241, 240, 0.65);
  border-color: rgba(255, 204, 199, 0.5);
}
.alert-bg { background: rgba(255, 77, 79, 0.1); }
.alert-text { color: var(--danger-color); }
.emergency-desc { font-size: 12px; color: #820014; margin: 0 0 12px 0; opacity: 0.8; }
.emergency-btn {
  display: block; width: 100%; text-align: center;
  padding: 8px 0; 
  background: var(--danger-color); 
  color: white;
  border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: 500;
  transition: 0.2s;
}
.emergency-btn:hover { opacity: 0.8; }

/* === 3. 链接列表 === */
.link-list { list-style: none; padding: 0; margin: 0; }
.link-list li { margin-bottom: 8px; }
.link-list a {
  display: block; padding: 6px 8px; border-radius: 6px;
  color: var(--text-sub); text-decoration: none; font-size: 13px;
  transition: 0.2s;
}
.link-list a:hover { 
  background: rgba(255,255,255,0.6); 
  color: var(--primary-color); /* ✅ 随主题变 */
}

/* 动画 */
.fade-slide-enter-active { transition: all 0.4s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(-10px); }
</style>
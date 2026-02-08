<template>
  <div class="page-container">
    <div class="content-wrapper">
      
      <div class="page-header slide-in-down">
        <button class="back-btn glass-btn" @click="router.back()">
          ← 返回对话
        </button>
        <div class="header-text">
          <h2>🧰 心理急救箱</h2>
          <p>不需要“情况严重”才能使用，随时回来充个电 💙</p>
        </div>
      </div>

      <div class="recommend-section slide-in-up" v-if="recommendedResource">
        <div class="section-title">
          <span>💡 AI 此时为你推荐</span>
        </div>
        <div class="rec-card glass-card" @click="openResource(recommendedResource)">
          <div class="rec-left">
            <span class="rec-icon">{{ recommendedResource.icon }}</span>
            <div class="rec-info">
              <h4>{{ recommendedResource.title }}</h4>
              <p>因为检测到你可能感到 <strong>{{ currentEmotion }}</strong></p>
            </div>
          </div>
          <button class="rec-btn">立即开始</button>
        </div>
      </div>

      <div class="tools-grid slide-in-up">
        <div 
          v-for="res in resources" 
          :key="res.id" 
          class="tool-card glass-card"
          @click="openResource(res)"
        >
          <div class="tool-icon-box">{{ res.icon }}</div>
          <h3>{{ res.title }}</h3>
          <p>{{ res.subtitle }}</p>
        </div>
      </div>

      <transition name="modal-fade">
        <div v-if="activeModal === 'KNOWLEDGE'" class="modal-overlay" @click.self="closeResourceModal">
          <div class="glass-modal knowledge-modal">
            <button class="close-btn" @click="closeResourceModal">×</button>
            <div class="k-header">
              <span class="k-icon">{{ knowledgeData.icon }}</span>
              <h3>{{ knowledgeData.title }}</h3>
            </div>
            <div class="k-content">
              <div v-for="(card, i) in knowledgeData.cards" :key="i" class="k-card" :class="{highlight: card.highlight}">
                <h4>{{ card.title }}</h4>
                <p v-html="card.content"></p>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="activeModal === 'BREATH'" class="modal-overlay immersive-overlay">
          <div class="breath-container">
            <div class="breath-circle" :class="breathState.phase">
              <span class="breath-text">{{ breathState.text }}</span>
              <span class="breath-timer">{{ breathState.timer }}s</span>
            </div>
            <p class="breath-guide">{{ breathState.guide }}</p>
            <button class="exit-breath-btn" @click="closeResourceModal">结束练习</button>
          </div>
        </div>
      </transition>

      <transition name="modal-fade">
        <div v-if="activeModal === 'EXTERNAL'" class="modal-overlay" @click.self="closeResourceModal">
          <div class="glass-modal auth-modal">
            <button class="close-btn" @click="closeResourceModal">×</button>
            <div class="auth-header">
              <img :src="externalData.logo" class="auth-logo">
              <h3>{{ externalData.title }}</h3>
            </div>
            <div class="auth-body">
              <div v-for="(info, i) in externalData.intro" :key="i" class="info-row">
                <span class="label">{{ info.label }}</span>
                <p v-html="info.text"></p>
              </div>
            </div>
            <a :href="externalData.link" target="_blank" class="auth-link-btn">访问官网 ↗</a>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { authStore as store } from '../store.js';

const router = useRouter();
const analysis = computed(() => store.analysisState || {});
const currentEmotion = computed(() => analysis.value.emotion || '平静');
const activeModal = ref(null);

// ==========================================
// 📝 在这里直接修改数据 (Data Area)
// ==========================================

// 1. 工具箱列表
const resources = [
  { 
    id: 'chart', 
    type: 'KNOWLEDGE', 
    title: '如何理解情绪图表？', 
    subtitle: '读懂心的痕迹', 
    icon: '📈',
    targetEmotion: ['平静', '开心', '迷茫', '积极'] 
  },
  { 
    id: 'breath', 
    type: 'BREATH', 
    title: '正念呼吸 5 步法', 
    subtitle: '3分钟快速减压', 
    icon: '🌬️',
    targetEmotion: ['焦虑', '愤怒', '紧张', '危机'] 
  },
  { 
    id: 'camh', 
    type: 'EXTERNAL', 
    title: '中国心理卫生协会', 
    subtitle: '权威医疗资源索引', 
    icon: '🏥',
    targetEmotion: ['危机', '抑郁', '痛苦', '悲伤'] 
  }
];

// 2. 知识卡片内容
const knowledgeData = {
  title: '如何理解情绪图表？',
  icon: '📈',
  cards: [
    { title: '🧐 曲线代表什么？', content: '它不是对你的“打分”，而是你心流的<strong>痕迹</strong>。就像心电图一样，有起伏才代表鲜活。' },
    { title: '🌊 为什么会波动？', content: '情绪是流动的能量。对话中的一个词、一段回忆，都会引起涟漪。<strong>波动 = 正在处理信息</strong>。' },
    { title: '💡 什么时候值得关注？', content: '当曲线<strong>持续长时间</strong>处于低谷，或者像过山车一样<strong>剧烈震荡</strong>时，AI 会提醒你停下来休息。', highlight: true }
  ]
};

// 3. 呼吸节奏 (单位：秒)
const breathCycleData = [
  { phase: 'inhale', text: '吸气', duration: 4, guide: '用鼻子深深吸气，感受腹部隆起...' },
  { phase: 'hold',   text: '保持', duration: 2, guide: '感受气流在体内的停留...' },
  { phase: 'exhale', text: '呼气', duration: 6, guide: '用嘴缓慢呼气，发出嘶嘶声...' }
];

// 4. 外部资源数据
const externalData = {
  logo: 'https://www.camh.org.cn/images/logo.png', // 示意图
  title: '中国心理卫生协会',
  intro: [
    { label: '它是谁？', text: '中国心理卫生领域最权威的学术组织之一，汇集了全国顶尖的精神科医生与心理咨询师。' },
    { label: '能帮你什么？', text: '提供科普文章、寻找正规医院资源、心理援助热线查询。' },
    { label: '适合情况', text: '当你觉得 AI 的帮助不够，需要<strong>现实医疗介入</strong>或<strong>专业人工咨询</strong>时。' }
  ],
  link: 'https://www.camh.org.cn/'
};

// ==========================================
// ⚙️ 逻辑区域 (Logic Area)
// ==========================================

// 智能推荐
const recommendedResource = computed(() => {
  return resources.find(r => r.targetEmotion.includes(currentEmotion.value));
});

// 打开资源
const openResource = (res) => {
  activeModal.value = res.type;
  if (res.type === 'BREATH') startBreathing();
};

const closeResourceModal = () => {
  activeModal.value = null;
  stopBreathing();
};

// 呼吸训练逻辑
const breathState = reactive({ phase: 'prepare', text: '准备', timer: 3, guide: '' });
let breathInterval = null;

const startBreathing = () => {
  breathState.phase = 'prepare'; breathState.text = '准备'; breathState.timer = 3; breathState.guide = '坐稳...';
  
  const runCycle = async () => {
    for (const step of breathCycleData) {
      if (activeModal.value !== 'BREATH') return;
      breathState.phase = step.phase; breathState.text = step.text; breathState.timer = step.duration; breathState.guide = step.guide;
      await new Promise(r => {
        const t = setInterval(() => {
          breathState.timer--;
          if (breathState.timer <= 0 || activeModal.value !== 'BREATH') { clearInterval(t); r(); }
        }, 1000);
      });
    }
    if (activeModal.value === 'BREATH') runCycle();
  };

  const prepTimer = setInterval(() => {
    breathState.timer--;
    if (breathState.timer <= 0) { clearInterval(prepTimer); runCycle(); }
  }, 1000);
  breathInterval = prepTimer;
};

const stopBreathing = () => { if (breathInterval) clearInterval(breathInterval); };
onUnmounted(() => stopBreathing());
</script>

<style scoped>
/* 页面容器 */
.page-container { min-height: 100vh; padding: 40px 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
.content-wrapper { max-width: 800px; margin: 0 auto; }

/* 头部 */
.page-header { display: flex; align-items: center; gap: 20px; margin-bottom: 40px; }
.back-btn { border: none; padding: 10px 20px; border-radius: 30px; background: white; cursor: pointer; font-weight: 500; transition: 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.back-btn:hover { transform: translateX(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
.header-text h2 { margin: 0; color: #333; }
.header-text p { margin: 5px 0 0 0; color: #666; font-size: 14px; }

/* 智能推荐 */
.recommend-section { margin-bottom: 40px; }
.section-title { margin-bottom: 15px; font-weight: bold; color: #555; display: flex; align-items: center; gap: 8px; }
.rec-card { display: flex; justify-content: space-between; align-items: center; cursor: pointer; border: 2px solid rgba(var(--primary-rgb), 0.3); background: linear-gradient(to right, rgba(var(--primary-rgb), 0.05), #fff); }
.rec-left { display: flex; align-items: center; gap: 15px; }
.rec-icon { font-size: 32px; background: #fff; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 12px; }
.rec-info h4 { margin: 0; font-size: 16px; color: #333; }
.rec-info p { margin: 4px 0 0 0; font-size: 13px; color: #666; }
.rec-btn { background: var(--primary-color); color: white; border: none; padding: 8px 20px; border-radius: 20px; cursor: pointer; }

/* 工具网格 */
.tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.tool-card { text-align: center; cursor: pointer; transition: 0.3s; display: flex; flex-direction: column; align-items: center; padding: 30px; }
.tool-card:hover { transform: translateY(-5px); background: #fff; }
.tool-icon-box { font-size: 40px; margin-bottom: 15px; background: rgba(0,0,0,0.03); width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
.tool-card h3 { margin: 0 0 8px 0; font-size: 16px; color: #333; }
.tool-card p { margin: 0; font-size: 13px; color: #888; }

/* 通用玻璃卡片 */
.glass-card { background: rgba(255,255,255,0.6); backdrop-filter: blur(12px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.5); box-shadow: 0 4px 20px rgba(0,0,0,0.05); }

/* 模态框基础 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); backdrop-filter: blur(5px); z-index: 999; display: flex; justify-content: center; align-items: center; }
.glass-modal { background: #fff; width: 90%; max-width: 500px; border-radius: 20px; padding: 30px; position: relative; animation: pop 0.3s; }
.close-btn { position: absolute; right: 20px; top: 20px; border: none; background: none; font-size: 24px; cursor: pointer; }

/* 知识卡片 */
.k-header { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.k-icon { font-size: 30px; }
.k-card { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
.k-card.highlight { background: #e6f7ff; border: 1px solid #91d5ff; }

/* 呼吸训练 */
.immersive-overlay { background: #000; color: white; }
.breath-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; }
.breath-circle { width: 200px; height: 200px; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 1s; background: rgba(255,255,255,0.1); margin-bottom: 40px; }
.breath-circle.inhale { transform: scale(1.6); background: rgba(255,255,255,0.2); }
.breath-text { font-size: 24px; font-weight: bold; }
.breath-timer { font-size: 30px; font-family: monospace; }
.exit-breath-btn { padding: 10px 30px; border-radius: 30px; background: transparent; border: 1px solid #fff; color: #fff; cursor: pointer; }
.exit-breath-btn:hover { background: #fff; color: #000; }

/* 权威资源 */
.auth-header { text-align: center; margin-bottom: 20px; }
.auth-logo { width: 60px; height: 60px; object-fit: contain; }
.info-row { margin-bottom: 15px; }
.label { font-size: 12px; color: #999; font-weight: bold; display: block; margin-bottom: 4px; }
.auth-link-btn { display: block; text-align: center; background: #1890ff; color: white; padding: 12px; border-radius: 8px; text-decoration: none; }

/* 动画 */
.slide-in-down { animation: slideDown 0.6s; }
.slide-in-up { animation: slideUp 0.6s; }
@keyframes pop { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes slideDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>
<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="show" class="modal-overlay" @click.self="close">
        
        <div class="glass-modal toolbox-modal">
          
          <div class="modal-header">
            <button v-if="currentView !== 'LIST'" class="nav-btn back-btn" @click="backToList">
              <span class="icon">‹</span> 返回
            </button>
            <div v-else class="header-placeholder"></div>

            <h3 class="header-title">{{ currentTitle }}</h3>
            <button class="nav-btn close-btn" @click="close">×</button>
          </div>

          <div class="modal-body" :class="{ 'no-padding': currentView === 'BREATH' }">
            
            <div v-if="currentView === 'LIST'" class="view-list slide-in">
              <p class="toolbox-intro">
                无需时刻坚强，这里是你的休息站 🌿
              </p>
              
              <div class="rec-card" v-if="recommendedResource" @click="openTool(recommendedResource)">
                <div class="rec-bg-decoration"></div>
                <div class="rec-header">
                  <span class="tag">✨ AI 此时推荐</span>
                  <span class="rec-arrow-icon">➔</span>
                </div>
                <div class="rec-content">
                  <div class="rec-icon-box">{{ recommendedResource.icon }}</div>
                  <div class="info">
                    <h4>{{ recommendedResource.title }}</h4>
                    <p>检测到你可能需要缓解情绪，试一试？</p>
                  </div>
                </div>
              </div>

              <div class="divider-text">全部工具</div>

              <div class="tools-list">
                <div 
                  v-for="res in resources" 
                  :key="res.id" 
                  class="tool-row"
                  @click="openTool(res)"
                >
                  <div class="tool-icon-circle">{{ res.icon }}</div>
                  <div class="tool-info">
                    <span class="tool-name">{{ res.title }}</span>
                    <span class="tool-desc">点击立即开始</span>
                  </div>
                  <span class="tool-arrow">›</span>
                </div>
              </div>
            </div>

            <div v-else-if="currentView === 'KNOWLEDGE'" class="view-content slide-in">
              <div class="k-header-banner">
                <span class="k-big-icon">📈</span>
                <p>情绪就像天气，有阴晴圆缺是自然的。</p>
              </div>
              <div class="k-scroll-area">
                <div v-for="(card, i) in knowledgeContent.cards" :key="i" class="k-card" :class="{highlight: card.highlight}">
                  <div class="k-card-title">
                    <span class="index-num">{{ i + 1 }}</span>
                    <h4>{{ card.title }}</h4>
                  </div>
                  <p v-html="card.content"></p>
                </div>
              </div>
            </div>

            <div v-else-if="currentView === 'BREATH'" class="view-content slide-in breath-view">
              <div class="breath-background-glow"></div>
              <div class="breath-circle" :class="breathState.phase">
                <span class="text">{{ breathState.text }}</span>
                <span class="timer">{{ breathState.timer }}</span>
              </div>
              <p class="guide-text">{{ breathState.guide }}</p>
              <button class="stop-breath-btn" @click="backToList">结束练习</button>
            </div>

            <div v-else-if="currentView === 'EXTERNAL'" class="view-content slide-in">
              <div class="auth-header">
                <div class="logo-circle">
                  <img :src="externalResourceInfo.logo" class="auth-logo">
                </div>
                <h3>{{ externalResourceInfo.title }}</h3>
                <span class="verified-badge">✓ 官方认证</span>
              </div>
              <div class="auth-list">
                <div v-for="(info, i) in externalResourceInfo.intro" :key="i" class="auth-item">
                  <span class="label">{{ info.label }}</span>
                  <p v-html="info.text"></p>
                </div>
              </div>
              <a :href="externalResourceInfo.link" target="_blank" class="primary-btn mt-auto">
                前往官方网站 ↗
              </a>
            </div>

          </div>
        </div>

      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, reactive, onUnmounted } from 'vue';
import { authStore as store } from '../store.js'; // 引入 store 获取情绪

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);

const currentView = ref('LIST');
const analysis = computed(() => store.analysisState || {}); // 获取真实情绪

// === 数据定义 ===
const resources = [
  { id: 'chart', type: 'KNOWLEDGE', title: '理解情绪图表', icon: '📈', targetEmotion: ['平静', '开心', '迷茫'] },
  { id: 'breath', type: 'BREATH', title: '正念呼吸', icon: '🌬️', targetEmotion: ['焦虑', '愤怒', '紧张'] },
  { id: 'camh', type: 'EXTERNAL', title: '权威资源', icon: '🏥', targetEmotion: ['危机', '抑郁', '痛苦'] }
];

const knowledgeContent = {
  title: '如何理解情绪图表？',
  cards: [
    { title: '曲线代表什么？', content: '它不是对你的“打分”，而是你心流的<strong>痕迹</strong>。就像心电图一样，有起伏才代表鲜活。' },
    { title: '为什么会波动？', content: '情绪是流动的能量。对话中的一个词、一段回忆，都会引起涟漪。<strong>波动 = 正在处理信息</strong>。' },
    { title: '何时需要关注？', content: '当曲线持续长时间处于低谷，或者像过山车一样剧烈震荡时，建议停下来休息。', highlight: true }
  ]
};

const externalResourceInfo = {
  logo: 'https://www.camh.org.cn/images/logo.png',
  title: '中国心理卫生协会',
  intro: [
    { label: '它是谁？', text: '中国心理卫生领域最权威的学术组织之一。' },
    { label: '能帮你什么？', text: '提供科普文章、寻找正规医院资源、心理援助热线查询。' }
  ],
  link: 'https://www.camh.org.cn/',
  linkText: '访问官方网站'
};

const breathCycle = [
  { phase: 'inhale', text: '吸气', duration: 4, guide: '用鼻子深深吸气，感受腹部隆起...' },
  { phase: 'hold', text: '保持', duration: 2, guide: '感受气流在体内的停留...' },
  { phase: 'exhale', text: '呼气', duration: 6, guide: '用嘴缓慢呼气，发出嘶嘶声...' }
];

// === 逻辑 ===
const currentTitle = computed(() => {
  if (currentView.value === 'LIST') return '🧰 心理工具箱';
  if (currentView.value === 'KNOWLEDGE') return '知识卡片';
  if (currentView.value === 'BREATH') return '正念呼吸';
  if (currentView.value === 'EXTERNAL') return '权威资源';
  return '';
});

// 智能推荐逻辑
const recommendedResource = computed(() => {
  const currentEmotion = analysis.value.emotion || '平静';
  return resources.find(r => r.targetEmotion?.includes(currentEmotion)) || resources[0];
});

const close = () => {
  stopBreathing();
  emit('close');
  setTimeout(() => { currentView.value = 'LIST'; }, 300);
};

const backToList = () => {
  stopBreathing();
  currentView.value = 'LIST';
};

const openTool = (res) => {
  currentView.value = res.type;
  if (res.type === 'BREATH') startBreathing();
};

// 呼吸逻辑
const breathState = reactive({ phase: 'prepare', text: '准备', timer: 3, guide: '' });
let breathInterval = null;

const startBreathing = () => {
  breathState.phase = 'prepare'; breathState.text = '准备'; breathState.timer = 3; breathState.guide = '请找一个舒适的坐姿...';
  const runCycle = async () => {
    for (const step of breathCycle) {
      if (currentView.value !== 'BREATH' || !props.show) return;
      breathState.phase = step.phase; breathState.text = step.text; breathState.timer = step.duration; breathState.guide = step.guide;
      await new Promise(r => {
        const t = setInterval(() => {
          breathState.timer--;
          if (breathState.timer <= 0 || currentView.value !== 'BREATH' || !props.show) { clearInterval(t); r(); }
        }, 1000);
      });
    }
    if (currentView.value === 'BREATH' && props.show) runCycle();
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
/* 基础模态框 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.3); backdrop-filter: blur(6px); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.toolbox-modal { width: 90%; max-width: 440px; height: 600px; background: #fff; border-radius: 24px; box-shadow: 0 25px 60px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; border: 1px solid rgba(255,255,255,0.8); }

/* 头部 */
.modal-header { height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid #f0f0f0; background: rgba(255,255,255,0.8); }
.header-title { font-size: 16px; font-weight: 600; color: #333; margin: 0; }
.nav-btn { border: none; background: none; cursor: pointer; color: #666; font-size: 14px; display: flex; align-items: center; gap: 4px; padding: 8px; border-radius: 8px; transition: 0.2s; }
.nav-btn:hover { background: #f5f5f5; color: #333; }
.close-btn { font-size: 22px; width: 36px; height: 36px; justify-content: center; }
.header-placeholder { width: 36px; }

/* 内容区 */
.modal-body { flex: 1; padding: 24px; overflow-y: auto; position: relative; background: #fafafa; }
.modal-body.no-padding { padding: 0; } /* 呼吸模式下无内边距 */

/* === 1. 列表视图 === */
.toolbox-intro { margin: 0 0 20px 0; font-size: 13px; color: #999; text-align: center; }

/* 推荐卡片 (重点装饰) */
.rec-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 20px; color: white; cursor: pointer; position: relative; overflow: hidden; box-shadow: 0 10px 20px rgba(118, 75, 162, 0.25); transition: transform 0.2s; }
.rec-card:hover { transform: translateY(-3px); box-shadow: 0 15px 25px rgba(118, 75, 162, 0.35); }
.rec-bg-decoration { position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; pointer-events: none; }
.rec-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.tag { font-size: 11px; font-weight: bold; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 20px; backdrop-filter: blur(4px); }
.rec-arrow-icon { font-size: 18px; font-weight: bold; opacity: 0.8; }
.rec-content { display: flex; align-items: center; gap: 15px; }
.rec-icon-box { font-size: 32px; background: rgba(255,255,255,0.9); width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.rec-content .info h4 { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; }
.rec-content .info p { margin: 0; font-size: 12px; opacity: 0.9; line-height: 1.4; }

.divider-text { margin: 25px 0 15px 0; font-size: 12px; color: #aaa; font-weight: bold; padding-left: 4px; }

/* 列表项 (改为长条形) */
.tools-list { display: flex; flex-direction: column; gap: 12px; }
.tool-row { background: #fff; padding: 12px 16px; border-radius: 12px; display: flex; align-items: center; gap: 12px; cursor: pointer; border: 1px solid #eee; transition: all 0.2s; }
.tool-row:hover { border-color: var(--primary-color); transform: translateX(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.tool-icon-circle { width: 36px; height: 36px; background: #f0f5ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; color: var(--primary-color); }
.tool-info { flex: 1; display: flex; flex-direction: column; }
.tool-name { font-size: 14px; color: #333; font-weight: 600; }
.tool-desc { font-size: 11px; color: #999; margin-top: 2px; }
.tool-arrow { color: #ccc; font-size: 18px; }

/* === 2. 知识视图 === */
.k-header-banner { text-align: center; margin-bottom: 20px; padding: 20px; background: #f0f7ff; border-radius: 12px; border: 1px dashed #adc6ff; }
.k-big-icon { font-size: 40px; display: block; margin-bottom: 10px; }
.k-header-banner p { margin: 0; font-size: 13px; color: #1d39c4; font-weight: 500; }
.k-card { background: #fff; border: 1px solid #eee; padding: 16px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.k-card.highlight { border-left: 4px solid var(--primary-color); background: #fffbf0; border-color: #ffe58f; }
.k-card-title { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.index-num { width: 20px; height: 20px; background: #eee; color: #666; border-radius: 50%; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.k-card h4 { margin: 0; font-size: 15px; color: #333; }
.k-card p { margin: 0; font-size: 13px; color: #666; line-height: 1.6; padding-left: 30px; }

/* === 3. 呼吸视图 (沉浸模式) === */
.breath-view { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle at center, #1a2a6c, #b21f1f, #fdbb2d); background: #1f2937; color: white; position: relative; }
.breath-background-glow { position: absolute; width: 100%; height: 100%; background: radial-gradient(circle, rgba(96,165,250,0.1) 0%, rgba(0,0,0,0) 70%); pointer-events: none; }
.breath-circle { width: 200px; height: 200px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 40px; transition: all 1s cubic-bezier(0.4, 0, 0.2, 1); position: relative; z-index: 10; }
.breath-circle.inhale { transform: scale(1.3); background: rgba(255,255,255,0.15); box-shadow: 0 0 40px rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.5); }
.breath-circle.hold { transform: scale(1.3); border-width: 4px; border-color: #fbbf24; }
.breath-circle.exhale { transform: scale(1); background: rgba(255,255,255,0.05); }
.breath-circle .text { font-size: 24px; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
.breath-circle .timer { font-size: 36px; font-family: monospace; font-weight: 300; margin-top: 5px; }
.guide-text { font-size: 15px; opacity: 0.8; height: 20px; margin-bottom: 40px; text-align: center; max-width: 80%; }
.stop-breath-btn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 10px 24px; border-radius: 30px; cursor: pointer; transition: 0.2s; font-size: 13px; }
.stop-breath-btn:hover { background: white; color: #333; }

/* === 4. 外部资源 === */
.auth-header { text-align: center; margin-bottom: 30px; margin-top: 10px; }
.logo-circle { width: 80px; height: 80px; background: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eee; }
.auth-logo { width: 50px; height: 50px; object-fit: contain; }
.auth-header h3 { margin: 0 0 5px 0; font-size: 18px; color: #333; }
.verified-badge { font-size: 11px; background: #e6f7ff; color: #1890ff; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
.auth-list { display: flex; flex-direction: column; gap: 20px; padding: 0 10px; }
.auth-item .label { font-size: 12px; color: #999; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; display: block; font-weight: bold; }
.auth-item p { margin: 0; font-size: 14px; color: #444; line-height: 1.5; background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #f0f0f0; }
.primary-btn { display: block; width: 100%; text-align: center; background: #1890ff; color: white; padding: 14px; border-radius: 12px; text-decoration: none; margin-top: 30px; font-weight: 600; box-shadow: 0 4px 15px rgba(24, 144, 255, 0.3); transition: 0.2s; }
.primary-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4); }
.mt-auto { margin-top: auto; }

/* 动画 */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.slide-in { animation: slideIn 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
@keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
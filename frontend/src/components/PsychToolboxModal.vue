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

          <div class="modal-body" :class="{ 'no-padding': currentView === 'GROUNDING' }">
            
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
                    <p>根据你的状态，试一试这个？</p>
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
                    <span class="tool-desc">{{ res.subtitle }}</span>
                  </div>
                  <span class="tool-arrow">›</span>
                </div>
              </div>
            </div>

            <div v-else-if="currentView === 'KNOWLEDGE'" class="view-content slide-in">
              <div class="k-header-banner">
                <span class="k-big-icon">{{ knowledgeContent.icon }}</span>
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

            <div v-else-if="currentView === 'GROUNDING'" class="view-content slide-in grounding-view">
              <div class="grounding-bg"></div>
              
              <div class="grounding-container" v-if="groundingStep < 5">
                <div class="g-progress-ring">
                  <span class="g-number">{{ 5 - groundingStep }}</span>
                </div>
                
                <transition name="fade-slide" mode="out-in">
                  <div class="g-card glass-card" :key="groundingStep">
                    <span class="g-icon">{{ groundingData[groundingStep].icon }}</span>
                    <h3 class="g-title">{{ groundingData[groundingStep].title }}</h3>
                    <p class="g-desc">{{ groundingData[groundingStep].desc }}</p>
                  </div>
                </transition>

                <button class="g-action-btn" @click="nextGroundingStep">
                  {{ groundingStep === 4 ? '完成练习' : '我找到了，下一步' }}
                </button>
              </div>

              <div class="grounding-container success-state" v-else>
                <div class="success-icon-box">✨</div>
                <h3 class="success-title">欢迎回到当下</h3>
                <p class="success-desc">你做得很棒。现在的你，是否感觉双脚更稳、内心更踏实了一些？</p>
                <button class="g-action-btn finish-btn" @click="backToList">回到工具箱</button>
              </div>
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
import { ref, computed } from 'vue';
import { authStore as store } from '../store.js';

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);

const currentView = ref('LIST');
const analysis = computed(() => store.analysisState || {});

// === 增强版数据 ===
const resources = [
  { id: 'chart', type: 'KNOWLEDGE', title: '理解情绪图表', subtitle: '读懂心的痕迹，接纳波动', icon: '📈', targetEmotion: ['平静', '开心', '迷茫'] },
  { id: 'ground', type: 'GROUNDING', title: '五感着陆练习', subtitle: '恐慌急救，拉回现实感', icon: '🌍', targetEmotion: ['焦虑', '愤怒', '紧张', '危机'] },
  { id: 'camh', type: 'EXTERNAL', title: '权威资源', subtitle: '寻找全国权威心理机构', icon: '🏥', targetEmotion: ['危机', '抑郁', '痛苦'] }
];

const knowledgeContent = {
  title: '如何理解情绪图表？', icon: '📈',
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

// === 新增：五感着陆法数据 ===
const groundingData = [
  { icon: '👁️', title: '寻找 5 样你看到的东西', desc: '环顾四周，在心里默默念出它们的名字。比如：白色的墙壁、桌子上的水杯、窗外的树...' },
  { icon: '✋', title: '感受 4 样你能触摸的东西', desc: '去摸一摸它们，感受温度和质地。比如：衣服柔软的布料、冰凉的桌面、椅子的扶手...' },
  { icon: '👂', title: '聆听 3 种你听到的声音', desc: '闭上眼睛，专注于耳朵。比如：远处的车流声、空调的嗡嗡声、时钟的滴答声...' },
  { icon: '👃', title: '辨认 2 种你闻到的气味', desc: '深吸一口气。比如：刚泡好的咖啡香、书本的纸张味、甚至衣服上的洗衣液味...' },
  { icon: '👅', title: '体会 1 种你嘴里的味道', desc: '感受口腔中的感觉，或者去喝一口清水，让水流过喉咙。' }
];

const groundingStep = ref(0);

const nextGroundingStep = () => {
  groundingStep.value++;
};

// === 逻辑 ===
const currentTitle = computed(() => {
  if (currentView.value === 'LIST') return '🧰 心理工具箱';
  if (currentView.value === 'KNOWLEDGE') return '知识科普';
  if (currentView.value === 'GROUNDING') return '着陆技术';
  if (currentView.value === 'EXTERNAL') return '权威资源';
  return '';
});

const recommendedResource = computed(() => {
  const currentEmotion = analysis.value.emotion || '平静';
  return resources.find(r => r.targetEmotion?.includes(currentEmotion)) || resources[1]; // 默认推荐着陆
});

const close = () => {
  emit('close');
  setTimeout(() => { 
    currentView.value = 'LIST'; 
    groundingStep.value = 0; // 重置练习进度
  }, 300);
};

const backToList = () => {
  currentView.value = 'LIST';
  setTimeout(() => { groundingStep.value = 0; }, 300); // 退出时重置进度
};

const openTool = (res) => {
  currentView.value = res.type;
};
</script>

<style scoped>
/* 基础模态框 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.toolbox-modal { width: 90%; max-width: 440px; height: 600px; background: #fff; border-radius: 24px; box-shadow: 0 25px 60px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; border: 1px solid rgba(255,255,255,0.8); animation: pop 0.4s cubic-bezier(0.16, 1, 0.3, 1); }

/* 头部 */
.modal-header { height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid #f0f0f0; background: rgba(255,255,255,0.9); z-index: 10; }
.header-title { font-size: 16px; font-weight: 600; color: #333; margin: 0; }
.nav-btn { border: none; background: none; cursor: pointer; color: #666; font-size: 14px; display: flex; align-items: center; gap: 4px; padding: 8px; border-radius: 8px; transition: 0.2s; }
.nav-btn:hover { background: #f5f5f5; color: #333; }
.close-btn { font-size: 22px; width: 36px; height: 36px; justify-content: center; }
.header-placeholder { width: 36px; }

/* 内容区 */
.modal-body { flex: 1; padding: 24px; overflow-y: auto; position: relative; background: #fafafa; }
.modal-body.no-padding { padding: 0; }

/* === 1. 列表视图 === */
.toolbox-intro { margin: 0 0 20px 0; font-size: 13px; color: #888; text-align: center; }

.rec-card { background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px; padding: 20px; color: white; cursor: pointer; position: relative; overflow: hidden; box-shadow: 0 10px 20px rgba(16, 185, 129, 0.25); transition: transform 0.2s; margin-bottom: 25px; }
.rec-card:hover { transform: translateY(-3px); box-shadow: 0 15px 25px rgba(16, 185, 129, 0.35); }
.rec-bg-decoration { position: absolute; top: -30px; right: -30px; width: 120px; height: 120px; background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%); border-radius: 50%; pointer-events: none; }
.rec-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; position: relative; z-index: 1; }
.tag { font-size: 11px; font-weight: bold; background: rgba(255,255,255,0.2); padding: 4px 10px; border-radius: 20px; backdrop-filter: blur(4px); }
.rec-arrow-icon { font-size: 16px; font-weight: bold; opacity: 0.8; }
.rec-content { display: flex; align-items: center; gap: 15px; position: relative; z-index: 1; }
.rec-icon-box { font-size: 32px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; border-radius: 14px; border: 1px solid rgba(255,255,255,0.3); }
.rec-content .info h4 { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.rec-content .info p { margin: 0; font-size: 12px; opacity: 0.9; line-height: 1.4; }

.divider-text { margin: 0 0 15px 0; font-size: 12px; color: #aaa; font-weight: bold; padding-left: 4px; }

.tools-list { display: flex; flex-direction: column; gap: 12px; }
.tool-row { background: #fff; padding: 14px 16px; border-radius: 12px; display: flex; align-items: center; gap: 14px; cursor: pointer; border: 1px solid #eee; transition: all 0.2s; }
.tool-row:hover { border-color: var(--primary-color); transform: translateX(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.tool-icon-circle { width: 40px; height: 40px; background: #f0f5ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; color: var(--primary-color); }
.tool-info { flex: 1; display: flex; flex-direction: column; }
.tool-name { font-size: 14px; color: #333; font-weight: 600; }
.tool-desc { font-size: 11px; color: #999; margin-top: 2px; }
.tool-arrow { color: #cbd5e1; font-size: 20px; font-weight: 300; transition: 0.3s; }
.tool-row:hover .tool-arrow { color: var(--primary-color); transform: translateX(4px); }

/* === 2. 知识视图 === */
.k-header-banner { text-align: center; margin-bottom: 20px; padding: 20px; background: #f0f7ff; border-radius: 12px; border: 1px dashed #adc6ff; }
.k-big-icon { font-size: 40px; display: block; margin-bottom: 10px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }
.k-header-banner p { margin: 0; font-size: 13px; color: #1d39c4; font-weight: 500; }
.k-card { background: #fff; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.k-card.highlight { border-left: 4px solid var(--primary-color); background: #fffbf0; border-color: #ffe58f; }
.k-card-title { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.index-num { width: 22px; height: 22px; background: #e2e8f0; color: #475569; border-radius: 50%; font-size: 11px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.k-card.highlight .index-num { background: #22c55e; color: white; }
.k-card h4 { margin: 0; font-size: 15px; color: #1e293b; }
.k-card p { margin: 0; font-size: 13px; color: #475569; line-height: 1.6; padding-left: 32px; }

/* === 3. 新增：五感着陆视图 (GROUNDING) === */
.grounding-view { height: 100%; display: flex; flex-direction: column; position: relative; background: #ecfdf5; overflow: hidden; }
.grounding-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at top right, #d1fae5 0%, #ecfdf5 60%, #f0fdf4 100%); pointer-events: none; }
.grounding-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; z-index: 1; padding: 0 30px; }

.g-progress-ring { width: 80px; height: 80px; border-radius: 50%; background: #fff; display: flex; justify-content: center; align-items: center; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15); border: 4px solid #34d399; }
.g-number { font-size: 36px; font-weight: 800; color: #059669; }

.glass-card.g-card { width: 100%; background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(12px); border-radius: 20px; padding: 30px 20px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.9); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05); margin-bottom: 40px; }
.g-icon { font-size: 48px; display: block; margin-bottom: 15px; }
.g-title { margin: 0 0 12px 0; font-size: 18px; color: #1e293b; font-weight: 700; }
.g-desc { margin: 0; font-size: 14px; color: #475569; line-height: 1.6; }

.g-action-btn { background: #10b981; color: white; border: none; padding: 16px 32px; border-radius: 30px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3); width: 80%; }
.g-action-btn:hover { background: #059669; transform: translateY(-2px); box-shadow: 0 12px 25px rgba(16, 185, 129, 0.4); }

.success-state { text-align: center; }
.success-icon-box { font-size: 60px; margin-bottom: 20px; animation: pop 0.5s ease; }
.success-title { font-size: 24px; color: #059669; margin: 0 0 15px 0; font-weight: 700; }
.success-desc { font-size: 15px; color: #475569; line-height: 1.6; margin-bottom: 40px; }
.finish-btn { background: #1e293b; box-shadow: 0 8px 20px rgba(30, 41, 59, 0.3); }
.finish-btn:hover { background: #0f172a; box-shadow: 0 12px 25px rgba(30, 41, 59, 0.4); }

/* === 4. 外部资源 === */
.auth-header { text-align: center; margin-bottom: 25px; margin-top: 10px; }
.logo-circle { width: 70px; height: 70px; background: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px auto; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eee; }
.auth-logo { width: 45px; height: 45px; object-fit: contain; }
.auth-header h3 { margin: 0 0 8px 0; font-size: 18px; color: #1e293b; }
.verified-badge { font-size: 11px; background: #dbeafe; color: #166534; padding: 3px 8px; border-radius: 12px; font-weight: 600; display: inline-block; }
.auth-list { display: flex; flex-direction: column; gap: 15px; }
.auth-item .label { font-size: 12px; color: #64748b; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; display: block; }
.auth-item p { margin: 0; font-size: 14px; color: #334155; line-height: 1.5; background: #fff; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; }
.primary-btn { display: block; width: 100%; text-align: center; background: #3b82f6; color: white; padding: 14px; border-radius: 12px; text-decoration: none; margin-top: 25px; font-weight: 600; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); transition: 0.3s; }
.primary-btn:hover { background: #2563eb; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4); }
.mt-auto { margin-top: auto; }

/* === 动画 === */
@keyframes pop { 0% { transform: scale(0.95) translateY(10px); opacity: 0; } 100% { transform: scale(1) translateY(0); opacity: 1; } }
.slide-in { animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideIn { 0% { opacity: 0; transform: translateX(15px); } 100% { opacity: 1; transform: translateX(0); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateX(20px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-20px); }
</style>
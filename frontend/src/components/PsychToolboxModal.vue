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

            <h3 class="header-title"></h3>
            <button class="nav-btn close-btn" @click="close">×</button>
          </div>

          <div class="modal-body" :class="{ 'no-padding': currentView === 'GROUNDING' }">
            
            <div v-if="currentView === 'LIST'" class="view-list slide-in">
              <div class="intro-banner">
                <span class="big-icon"></span>
                <p>无需时刻坚强，这里是你的休息站</p>
              </div>

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

                <div class="g-footer">
                  <div class="step-dots">
                    <span v-for="n in 5" :key="n" class="dot" :class="{ active: n - 1 === groundingStep, completed: n - 1 < groundingStep }"></span>
                  </div>
                  <button class="g-action-btn" @click="nextGroundingStep">
                    {{ groundingStep === 4 ? '完成练习' : '我找到了，下一步' }}
                  </button>
                </div>
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
                  <span style="font-size: 32px;">🏥</span>
                </div>
                <h3>{{ externalResourceInfo.title }}</h3>
                <span class="verified-badge">✓ 官方机构认证</span>
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

const props = defineProps({ show: Boolean });
const emit = defineEmits(['close']);

const currentView = ref('LIST');

// === 精简版核心数据 ===
const resources = [
  { id: 'chart', type: 'KNOWLEDGE', title: '理解情绪图表', subtitle: '读懂心的痕迹，接纳波动', icon: '📈' },
  { id: 'ground', type: 'GROUNDING', title: '五感着陆练习', subtitle: '恐慌急救，拉回现实感', icon: '🌍' },
  { id: 'camh', type: 'EXTERNAL', title: '权威医疗资源', subtitle: '寻找全国权威心理机构', icon: '🏥' }
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
  title: '中国心理卫生协会',
  intro: [
    { label: '它是谁？', text: '中国心理卫生领域最权威的学术组织之一。' },
    { label: '能帮你什么？', text: '提供科普文章、寻找正规医院资源、心理援助热线查询。' }
  ],
  link: 'https://www.camh.org.cn/'
};

const groundingData = [
  { icon: '👁️', title: '寻找 5 样你看到的东西', desc: '环顾四周，在心里默默念出它们的名字。比如：白色的墙壁、水杯、窗外的树...' },
  { icon: '✋', title: '感受 4 样你能触摸的东西', desc: '去摸一摸它们，感受温度和质地。比如：衣服的布料、冰凉的桌面...' },
  { icon: '👂', title: '聆听 3 种你听到的声音', desc: '闭上眼睛，专注于耳朵。比如：远处的车流声、空调的嗡嗡声...' },
  { icon: '👃', title: '辨认 2 种你闻到的气味', desc: '深吸一口气。比如：刚泡好的咖啡香、书本的纸张味...' },
  { icon: '👅', title: '体会 1 种你嘴里的味道', desc: '感受口腔中的感觉，或者去喝一口清水，让水流过喉咙。' }
];

const groundingStep = ref(0);

const nextGroundingStep = () => { groundingStep.value++; };

const currentTitle = computed(() => {
  if (currentView.value === 'LIST') return '🧰 心理工具箱';
  if (currentView.value === 'KNOWLEDGE') return '知识科普';
  if (currentView.value === 'GROUNDING') return '着陆急救技术';
  if (currentView.value === 'EXTERNAL') return '权威资源';
  return '';
});

const close = () => {
  emit('close');
  setTimeout(() => { currentView.value = 'LIST'; groundingStep.value = 0; }, 300);
};

const backToList = () => {
  currentView.value = 'LIST';
  setTimeout(() => { groundingStep.value = 0; }, 300);
};

const openTool = (res) => {
  currentView.value = res.type;
};
</script>

<style scoped>
/* 基础模态框 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(12px); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.toolbox-modal { width: 90%; max-width: 440px; height: 620px; background: #fff; border-radius: 24px; box-shadow: 0 25px 60px rgba(0,0,0,0.15); display: flex; flex-direction: column; overflow: hidden; border: 1px solid rgba(255,255,255,0.8); animation: pop 0.4s cubic-bezier(0.16, 1, 0.3, 1); }

/* 头部 */
.modal-header { height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; border-bottom: 1px solid #f0f0f0; background: rgba(255,255,255,0.9); z-index: 10; flex-shrink: 0;}
.header-title { font-size: 16px; font-weight: 600; color: #1d1d1f; margin: 0; }
.nav-btn { border: none; background: none; cursor: pointer; color: #666; font-size: 14px; display: flex; align-items: center; gap: 4px; padding: 8px; border-radius: 8px; transition: 0.2s; }
.nav-btn:hover { background: #f5f5f5; color: #1d1d1f; }
.close-btn { font-size: 22px; width: 36px; height: 36px; justify-content: center; }
.header-placeholder { width: 60px; }

/* 内容区 */
.modal-body { flex: 1; padding: 24px; overflow-y: auto; position: relative; background: #fafafa; }
.modal-body.no-padding { padding: 0; overflow: hidden; } 

/* === 1. 列表视图 (极简版) === */
.intro-banner { text-align: center; margin-bottom: 30px; margin-top: 10px; }
.intro-banner .big-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.intro-banner p { margin: 0; font-size: 14px; color: #86868b; }

.tools-list { display: flex; flex-direction: column; gap: 16px; }
.tool-row { background: #fff; padding: 20px 16px; border-radius: 16px; display: flex; align-items: center; gap: 16px; cursor: pointer; border: 1px solid #f0f0f0; transition: all 0.2s; box-shadow: 0 2px 10px rgba(0,0,0,0.02);}
.tool-row:hover { border-color: #0071e3; background: #fbfbfc; transform: translateX(4px); box-shadow: 0 4px 12px rgba(0, 113, 227, 0.05); }
.tool-icon-circle { width: 48px; height: 48px; background: #f5f5f7; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #0071e3; }
.tool-row:hover .tool-icon-circle { background: rgba(0, 113, 227, 0.1); }
.tool-info { flex: 1; display: flex; flex-direction: column; }
.tool-name { font-size: 16px; color: #1d1d1f; font-weight: 600; margin-bottom: 4px;}
.tool-desc { font-size: 13px; color: #86868b; }
.tool-arrow { color: #d2d2d7; font-size: 24px; font-weight: 300; transition: 0.3s; }
.tool-row:hover .tool-arrow { color: #0071e3; transform: translateX(4px); }

/* === 2. 知识视图 === */
.k-header-banner { text-align: center; margin-bottom: 24px; padding: 24px; background: #f0f5ff; border-radius: 16px; }
.k-big-icon { font-size: 48px; display: block; margin-bottom: 12px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }
.k-header-banner p { margin: 0; font-size: 14px; color: #0071e3; font-weight: 600; }
.k-card { background: #fff; border: 1px solid #e5e5ea; padding: 20px; border-radius: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.k-card.highlight { border-left: 4px solid #0071e3; background: #f8fbff; border-color: #cce4ff; }
.k-card-title { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.index-num { width: 24px; height: 24px; background: #e5e5ea; color: #1d1d1f; border-radius: 50%; font-size: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.k-card.highlight .index-num { background: #0071e3; color: white; }
.k-card h4 { margin: 0; font-size: 16px; color: #1d1d1f; }
.k-card p { margin: 0; font-size: 14px; color: #475569; line-height: 1.6; padding-left: 36px; }

/* === 3. 五感着陆视图 === */
.grounding-view { height: 100%; display: flex; flex-direction: column; position: relative; background: #ecfdf5; overflow: hidden; }
.grounding-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at top right, #d1fae5 0%, #ecfdf5 60%, #f0fdf4 100%); pointer-events: none; }
.grounding-container { display: flex; flex-direction: column; align-items: center; padding: 40px 30px; height: 100%; position: relative; z-index: 1; }

.g-progress-ring { width: 70px; height: 70px; border-radius: 50%; background: #fff; display: flex; justify-content: center; align-items: center; margin-bottom: 40px; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15); border: 4px solid #34d399; flex-shrink: 0;}
.g-number { font-size: 32px; font-weight: 800; color: #059669; }

.glass-card.g-card { width: 100%; background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); border-radius: 24px; padding: 40px 24px; text-align: center; border: 1px solid #fff; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.05); margin-bottom: auto; }
.g-icon { font-size: 56px; display: block; margin-bottom: 20px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));}
.g-title { margin: 0 0 16px 0; font-size: 20px; color: #1e293b; font-weight: 700; }
.g-desc { margin: 0; font-size: 15px; color: #475569; line-height: 1.6; }

.g-footer { width: 100%; display: flex; flex-direction: column; align-items: center; gap: 24px; margin-top: auto; padding-bottom: 20px; }
.step-dots { display: flex; gap: 10px; }
.step-dots .dot { width: 10px; height: 10px; border-radius: 50%; background: #a7f3d0; transition: 0.3s; }
.step-dots .dot.completed { background: #34d399; }
.step-dots .dot.active { background: #059669; transform: scale(1.3); }

.g-action-btn { background: #10b981; color: white; border: none; padding: 16px; border-radius: 16px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.25); width: 100%; }
.g-action-btn:hover { background: #059669; transform: translateY(-2px); box-shadow: 0 12px 25px rgba(16, 185, 129, 0.35); }

.success-state { justify-content: center; text-align: center; }
.success-icon-box { font-size: 70px; margin-bottom: 24px; animation: pop 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
.success-title { font-size: 24px; color: #059669; margin: 0 0 16px 0; font-weight: 700; }
.success-desc { font-size: 15px; color: #475569; line-height: 1.6; margin-bottom: 40px; }
.finish-btn { background: #1e293b; box-shadow: 0 8px 20px rgba(30, 41, 59, 0.2); }
.finish-btn:hover { background: #0f172a; box-shadow: 0 12px 25px rgba(30, 41, 59, 0.3); }

/* === 4. 外部资源 === */
.auth-header { text-align: center; margin-bottom: 30px; margin-top: 20px; }
.logo-circle { width: 80px; height: 80px; background: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f0f0f0; }
.auth-header h3 { margin: 0 0 10px 0; font-size: 20px; color: #1d1d1f; }
.verified-badge { font-size: 12px; background: #dbeafe; color: #166534; padding: 4px 12px; border-radius: 20px; font-weight: 600; display: inline-block; border: 1px solid #bbf7d0;}
.auth-list { display: flex; flex-direction: column; gap: 16px; }
.auth-item .label { font-size: 12px; color: #86868b; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; display: block; letter-spacing: 0.5px;}
.auth-item p { margin: 0; font-size: 15px; color: #1d1d1f; line-height: 1.6; background: #fff; padding: 16px; border-radius: 16px; border: 1px solid #f0f0f0; box-shadow: 0 2px 8px rgba(0,0,0,0.02);}
.primary-btn { display: block; width: 100%; text-align: center; background: #0071e3; color: white; padding: 16px; border-radius: 16px; text-decoration: none; margin-top: 30px; font-weight: 600; box-shadow: 0 8px 20px rgba(0, 113, 227, 0.25); transition: 0.3s; }
.primary-btn:hover { background: #0077ed; transform: translateY(-2px); box-shadow: 0 12px 25px rgba(0, 113, 227, 0.35); }

/* === 动画 === */
@keyframes pop { 0% { transform: scale(0.95) translateY(10px); opacity: 0; } 100% { transform: scale(1) translateY(0); opacity: 1; } }
.slide-in { animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideIn { 0% { opacity: 0; transform: translateX(20px); } 100% { opacity: 1; transform: translateX(0); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-slide-enter-from { opacity: 0; transform: translateX(30px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-30px); }
</style>
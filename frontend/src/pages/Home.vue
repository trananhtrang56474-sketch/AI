<template>
  <div class="home-container">
    <div class="content-wrapper">
      
      <section class="hero-section glass-card slide-in-down">
        <div class="hero-content">
          <div class="greeting-row">
            <div class="greeting-box">
              <span class="weather-icon">{{ timeIcon }}</span>
              <h1>{{ greeting }}，{{ username }}</h1>
            </div>
            <div class="mood-badge">
              <span class="pulse-dot"></span>
              <span>{{ currentStatus }}</span>
            </div>
          </div>
          
          <p class="subtitle">这里是你的心灵栖息地。所有的情绪，都值得被看见。</p>
          
          <div class="interactive-area">
            <div class="ai-care-box cloud-bubble">
              <span class="sparkle" :class="{ 'spin-anim': isMessageLoading }">✨</span>
              <div class="care-text">
                <strong class="gradient-title">AI 观测寄语：</strong>
                <transition name="fade" mode="out-in">
                  <span :key="displayedAiCareMessage">{{ displayedAiCareMessage }}</span>
                </transition>
              </div>
            </div>

            <div class="mood-checkin-box" v-if="!hasCheckedIn">
              <span class="mood-label">你此刻感觉如何？</span>
              <div class="mood-emojis">
                <button 
                  v-for="(mood, index) in moodOptions" 
                  :key="index"
                  class="mood-btn"
                  :title="mood.label"
                  @click="recordMood(mood.value, mood.label)"
                >
                  {{ mood.icon }}
                </button>
              </div>
            </div>
            
            <div class="mood-checkin-success" v-else>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
              <span>今日情绪已记录，感谢你的倾诉与分享。</span>
            </div>

            <div class="action-btn-group">
              <button class="continue-btn pulse-effect" @click="goToChat" :disabled="isNavigating">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                {{ isNavigating ? '正在前往...' : '去和 AI 聊聊' }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="hero-decoration floating-anim">
          <svg viewBox="0 0 24 24" width="100" height="100" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22V12"></path>
            <path d="M12 12C12 12 9 7 4 5"></path>
            <path d="M12 12C12 12 15 7 20 5"></path>
            <path d="M12 16C12 16 9.5 13 6 12"></path>
            <path d="M12 16C12 16 14.5 13 18 12"></path>
          </svg>
        </div>
      </section>

      <div class="main-grid">
        
        <div class="glass-card assessment-panel slide-in-up">
          <div class="assessment-section">
            <div class="section-header">
              <span class="label">当前心境评估 (V-A)</span>
              <div class="mini-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="11" r="3"/><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
            </div>
            <div class="section-body">
              <div class="score-row">
                <span class="score-num">{{ analytics.avg_v || '5.0' }}</span>
                <span class="score-divider">/</span>
                <span class="score-num">{{ analytics.avg_a || '3.0' }}</span>
              </div>
              <div class="status-tag" :class="statusClass">{{ statusLabel }}</div>
              <p class="desc">愉悦度 (V) / 激活度 (A)</p>
            </div>
          </div>

          <div class="divider"></div>

          <div class="assessment-section">
            <div class="section-header">
              <span class="label">PHQ-9 风险评估</span>
              <div class="mini-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/></svg></div>
            </div>
            <div class="section-body">
              <div class="risk-row">
                <span class="score-num">{{ phq9Score }}</span>
                <span class="risk-text">{{ riskLevelText }}</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (phq9Score / 27 * 100) + '%' }"></div>
              </div>
              <div class="progress-labels"><span>0</span><span>27</span></div>
            </div>
          </div>

          <div class="panel-footer">
             <button class="footer-btn" @click="$router.push('/report')">查看详细心理档案</button>
          </div>
        </div>

        <div class="glass-card trend-card slide-in-up" style="animation-delay: 0.1s">
          <div class="card-header">
            <div class="header-title">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              <h4>近期情绪波动</h4>
            </div>
          </div>
          
          <div class="chart-wrapper">
            <EmotionChart :chartData="homeChartData" />
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios'; 
import { authStore } from '../store.js'; 
import { showToast } from '../utils/toast.js'; 
import EmotionChart from '../components/EmotionChart.vue';

const router = useRouter();
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// ================= 1. 基础 UI 与状态 =================
const hour = new Date().getHours();
const username = computed(() => authStore.username || '朋友');
const greeting = computed(() => {
  if (hour < 5) return '夜深了';
  if (hour < 12) return '早上好';
  if (hour < 18) return '下午好';
  return '晚上好';
});
const timeIcon = computed(() => hour < 6 ? '🌙' : hour < 18 ? '☀️' : '✨');

const currentStatus = ref("平稳放松"); 

// ================= 2. 聊天与打卡交互 =================
const isNavigating = ref(false);
const goToChat = async () => {
  if (isNavigating.value) return;
  isNavigating.value = true;
  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) { router.push('/login'); return; }
    const res = await axios.get(`${API_BASE}/api/sessions?user_id=${userId}`);
    if (res.data && res.data.length > 0) {
      router.push(`/chat?session_id=${res.data[0].id}`);
    } else {
      router.push('/chat');
    }
  } catch (error) { router.push('/chat'); } 
  finally { isNavigating.value = false; }
};

const hasCheckedIn = ref(false);
const moodOptions = [
  { icon: '😄', label: '极好', value: 90 },
  { icon: '🙂', label: '平静', value: 70 },
  { icon: '😐', label: '一般', value: 50 },
  { icon: '😔', label: '低落', value: 30 },
  { icon: '😫', label: '焦虑', value: 10 }
];

const recordMood = async (val, label) => {
  try {
    hasCheckedIn.value = true;
    currentStatus.value = label; 
    showToast('打卡记录成功！', 'success');
    fetchHomeChartData();
  } catch (error) { console.error("情绪打卡失败", error); }
};

// ================= 3. AI 寄语与打字机 =================
const isMessageLoading = ref(true);
const displayedAiCareMessage = ref(""); 
let typewriterInterval = null;

const typeMessage = (message) => {
  if (typewriterInterval) clearInterval(typewriterInterval);
  displayedAiCareMessage.value = "";
  let currentIdx = 0;
  typewriterInterval = setInterval(() => {
    if (currentIdx < message.length) {
      displayedAiCareMessage.value += message[currentIdx];
      currentIdx++;
    } else {
      clearInterval(typewriterInterval);
    }
  }, 40); 
};

const fetchAiCareMessage = async () => {
  isMessageLoading.value = true;
  let fullMessage = "";
  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) { fullMessage = "静下心来，开启你的倾诉之旅吧。"; return; }
    const res = await axios.post(`${API_BASE}/api/chat`, {
      user_id: userId, message: "请写一句治愈寄语", is_silent: true 
    });
    fullMessage = res.data.reply || "今天也是充满希望的一天。";
  } catch (error) {
    fullMessage = "所有的情绪都是暂时的，给自己一点耐心。";
  } finally {
    isMessageLoading.value = false;
    typeMessage(fullMessage);
  }
};

// ================= 4. 新增的评估面板计算逻辑 =================
const analytics = ref({});

const phq9Score = computed(() => {
  if (!analytics.value.health_index) return 0;
  // 简单模拟 PHQ-9 得分 (0-27)
  return Math.round((100 - analytics.value.health_index) / 100 * 27);
});

const riskLevelText = computed(() => {
  const s = phq9Score.value;
  if (s <= 4) return '极低风险';
  if (s <= 9) return '轻度风险';
  if (s <= 14) return '中度风险';
  return '重度风险';
});

const statusLabel = computed(() => {
  const v = analytics.value.avg_v || 5;
  if (v >= 6.5) return '心态积极';
  if (v <= 4.5) return '内耗严重';
  return '状态平稳';
});

const statusClass = computed(() => {
  const v = analytics.value.avg_v || 5;
  if (v >= 6.5) return 'status-good';
  if (v <= 4.5) return 'status-bad';
  return 'status-neutral';
});

// ================= 5. 图表与数据加载 =================
// ✨ 1. 把所有需要的数组都初始化好，防止子组件报错
// ================= 5. 图表与数据加载 =================
const homeChartData = ref({ dates: [], scores: [], valences: [], arousals: [], tags: [], contents: [] });

const fetchHomeChartData = async () => {
  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;
    
    const res = await axios.get(`${API_BASE}/api/chart-data?user_id=${userId}`);
    
    if (res.data && res.data.dates) {
      // ✨✨✨ 修复1：使用 Object.assign 而不是重新赋值 `{}`
      // 这样能保留 Vue 的响应式追踪，ECharts 就不会从空白重绘，而是平滑延伸！
      Object.assign(homeChartData.value, {
        dates: res.data.dates || [],
        scores: res.data.scores || [],
        valences: res.data.valences || [],
        arousals: res.data.arousals || [],
        tags: res.data.tags || [],
        contents: res.data.contents || []
      });
      
      // 赋值左侧的评估面板数据
      if (res.data.analytics) {
        analytics.value = res.data.analytics;
      }
    }
  } catch (error) { 
    console.error("图表数据加载失败", error); 
  }
};

onMounted(() => {
  // ✨✨✨ 修复2：排队机制！
  // 先拉取超快的图表数据（0.1秒），确保画面瞬间出现。
  // 然后再去请求缓慢的 AI 寄语接口，彻底解决“变空白转圈”的交通阻塞！
  fetchHomeChartData().then(() => {
    fetchAiCareMessage(); 
  });
});
</script>

<style scoped>
@import '../assets/main.css';

.home-container {
  --primary-color: #7b61ff; 
  --primary-rgb: 123, 97, 255;
  --primary-gradient: linear-gradient(135deg, #9b84ff 0%, #6343ed 100%);
  --text-main: #334155; 
  --text-sub: #64748b;
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: 1px solid rgba(255, 255, 255, 0.5);
  --glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);

  min-height: 100%; position: relative; overflow-x: hidden;
  background: radial-gradient(circle at 10% 10%, rgba(123, 97, 255, 0.08) 0%, #e0f2fe 50%, rgba(123, 97, 255, 0.05) 100%);
  padding-bottom: 40px;
}

.content-wrapper { position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 40px 20px 0; }

.glass-card {
  background: var(--glass-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: var(--glass-border); border-radius: 20px; padding: 24px;
  box-shadow: var(--glass-shadow); transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
}
.glass-card:hover {
  transform: translateY(-3px); box-shadow: 0 12px 40px rgba(123, 97, 255, 0.12); background: rgba(255, 255, 255, 0.85);
}

/* --- 1. 顶部 Hero 区 --- */
.hero-section {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 30px; position: relative; overflow: hidden;
  background: linear-gradient(-45deg, rgba(255,255,255,0.9), rgba(224, 242, 254, 0.6), rgba(255,255,255,0.9));
  background-size: 400% 400%; animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

.hero-content { flex: 1; z-index: 2; }

.greeting-row { display: flex; align-items: center; gap: 16px; margin-bottom: 8px; flex-wrap: wrap; }
.greeting-box { display: flex; align-items: center; gap: 10px; }
.greeting-box h1 { margin: 0; font-size: 26px; color: var(--text-main); letter-spacing: 0.5px; }
.weather-icon { font-size: 28px; }

.mood-badge {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);
  color: #059669; padding: 4px 14px; border-radius: 50px;
  font-size: 13px; font-weight: 600;
}
.pulse-dot {
  width: 8px; height: 8px; background: #10b981; border-radius: 50%;
  box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
  animation: pulseGreen 2s infinite;
}
@keyframes pulseGreen {
  0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.subtitle { margin: 0 0 24px 0; color: var(--text-sub); font-size: 15px; }

.hero-decoration { position: absolute; right: 20px; top: 20px; width: 100px; height: 100px; color: var(--primary-color); opacity: 0.15; z-index: 1; }
.floating-anim { animation: float 6s ease-in-out infinite; }

.interactive-area { display: flex; flex-direction: column; gap: 16px; max-width: 600px; position: relative; z-index: 2; }
.ai-care-box { display: flex; align-items: flex-start; gap: 10px; background: rgba(123, 97, 255, 0.06); padding: 16px 20px; border-radius: 16px; border: 1px solid rgba(123, 97, 255, 0.1); position: relative; }
.ai-care-box::before { content: ''; position: absolute; left: 0; top: 16px; bottom: 16px; width: 4px; border-radius: 0 4px 4px 0; background: var(--primary-gradient); }
.sparkle { font-size: 16px; margin-top: 2px; }
.spin-anim { animation: slowSpin 2s linear infinite; opacity: 0.7; }
@keyframes slowSpin { 100% { transform: rotate(360deg); } }
.care-text { font-size: 14.5px; color: #4b5563; line-height: 1.6; padding-left: 8px; }
.gradient-title { background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; margin-right: 4px; }

.mood-checkin-box { display: flex; align-items: center; gap: 16px; padding: 8px 0; }
.mood-label { font-size: 14px; color: var(--text-sub); font-weight: 500; }
.mood-emojis { display: flex; gap: 10px; }
.mood-btn { background: white; border: 1px solid #e2e8f0; border-radius: 50%; width: 42px; height: 42px; font-size: 20px; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.mood-btn:hover { transform: translateY(-4px) scale(1.1); border-color: var(--primary-color); box-shadow: 0 6px 16px rgba(123, 97, 255, 0.2); }
.mood-checkin-success { display: flex; align-items: center; gap: 8px; color: #10b981; font-size: 14.5px; font-weight: 500; padding: 10px 0; animation: fadeIn 0.5s ease; }
.mood-checkin-success svg { width: 18px; height: 18px; color: #10b981; }

.action-btn-group { margin-top: 8px; }
.continue-btn { background: var(--primary-gradient); color: white; border: none; padding: 12px 32px; border-radius: 50px; font-size: 15px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(123, 97, 255, 0.3); display: inline-flex; align-items: center; gap: 8px; transition: all 0.3s; }
.continue-btn:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(123, 97, 255, 0.4); }
.continue-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-icon { width: 16px; height: 16px; }

/* --- 2. 中间网格区 (完全保持原来的布局结构) --- */
.main-grid { display: grid; grid-template-columns: minmax(280px, 1fr) 2.5fr; gap: 24px; align-items: stretch; margin-top: 10px; }

/* ✨ 新增的评估面板样式 (替换原来的 daily-quote) */
.assessment-panel {
  display: flex; flex-direction: column; justify-content: space-between;
  position: relative; overflow: hidden;
}

.assessment-section { display: flex; flex-direction: column; }
.section-header { display: flex; justify-content: space-between; align-items: center; color: var(--text-sub); font-size: 13px; font-weight: 600; margin-bottom: 12px; }
.mini-icon { width: 28px; height: 28px; background: rgba(123, 97, 255, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--primary-color); }
.mini-icon svg { width: 16px; height: 16px; }

.score-row { margin-bottom: 4px; display: flex; align-items: baseline; }
.score-num { font-size: 30px; font-weight: 800; color: var(--text-main); letter-spacing: -1px; line-height: 1.2; }
.score-divider { color: #cbd5e1; font-weight: 300; margin: 0 6px; font-size: 20px; }

.status-tag { display: inline-block; padding: 4px 12px; border-radius: 50px; font-size: 12px; font-weight: 700; margin: 8px 0; width: max-content; }
.status-good { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.status-bad { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.status-neutral { background: rgba(123, 97, 255, 0.1); color: var(--primary-color); border: 1px solid rgba(123, 97, 255, 0.2); }
.desc { font-size: 12px; color: var(--text-sub); margin: 0; }

.divider { height: 1px; background: rgba(0,0,0,0.06); margin: 16px 0; }

.risk-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
.risk-text { font-size: 14px; color: var(--text-sub); font-weight: 600; }
.progress-bar { height: 6px; background: rgba(0,0,0,0.05); border-radius: 10px; overflow: hidden; margin-bottom: 6px; }
.progress-fill { height: 100%; background: var(--primary-gradient); transition: width 0.5s ease; border-radius: 10px;}
.progress-labels { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; font-weight: 600; }

.panel-footer { margin-top: 16px; }
.footer-btn { width: 100%; padding: 10px; border-radius: 10px; border: 1px dashed rgba(123, 97, 255, 0.4); background: rgba(123, 97, 255, 0.02); color: var(--primary-color); font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.footer-btn:hover { background: var(--primary-color); color: white; border-style: solid; }

/* 右侧图表区域 */
.trend-card { display: flex; flex-direction: column; }
.header-title { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.header-title .icon { width: 20px; height: 20px; color: var(--primary-color); }
.header-title h4 { margin: 0; font-size: 17px; color: var(--text-main); font-weight: 600; }

.chart-wrapper { 
  flex: 1; 
  min-height: 340px; 
  width: 100%; 
  display: flex;
  flex-direction: column;
}

/* 动画 */
@keyframes float { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-15px) rotate(3deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.slide-in-down { animation: slideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-in-up { animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; } }

/* 响应式 */
@media (max-width: 850px) {
  .main-grid { grid-template-columns: 1fr; } 
  .hero-section { flex-direction: column; }
  .hero-decoration { display: none; }
}
</style>
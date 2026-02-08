<template>
  <div class="home-container">
    <div class="content-wrapper">
      
      <section class="hero-section glass-card slide-in-down">
        <div class="hero-content">
          <div class="greeting-box">
            <span class="weather-icon">{{ timeIcon }}</span>
            <h1>{{ greeting }}，{{ username }}</h1>
          </div>
          <p class="subtitle">这里是你的心灵栖息地。所有的情绪，都值得被看见。</p>
          
          <button class="primary-btn pulse-effect" @click="handleAction('chat', 'start')">
            <span class="btn-icon">✨</span> 开启一次心灵对话
          </button>
        </div>
        <div class="hero-decoration">🌱</div>
      </section>

      <div class="main-grid">
        
        <div class="left-column">
          
          <div class="glass-card daily-quote slide-in-up">
            <span class="quote-icon">❝</span>
            <transition name="fade" mode="out-in">
              <div :key="currentQuote.text">
                <p class="quote-text">{{ currentQuote.text }}</p>
                <span class="quote-author">—— {{ currentQuote.author }}</span>
              </div>
            </transition>
          </div>

          <div class="glass-card knowledge-hub slide-in-up" style="animation-delay: 0.1s">
            <div class="card-header">
              <div class="header-title">
                <span class="icon">🧩</span>
                <h4>心理锦囊</h4>
              </div>
              <button class="link-btn" @click="showRandomTip">换一批</button>
            </div>
            <div class="topic-grid">
              <div 
                v-for="tip in visibleTips" 
                :key="tip.title" 
                class="topic-pill"
                @click="openTipModal(tip)"
              >
                {{ tip.icon }} {{ tip.title }}
              </div>
              
              <div class="topic-pill highlight" @click="router.push('/article/1')">
                ✨ 探索更多
              </div>
            </div>
          </div>
        </div>
        
        <div class="right-column slide-in-right">
          
          <div class="action-list">
            
            <div class="glass-card action-item" @click="handleAction('chat', 'deep')">
              <div class="icon-box primary-icon">💬</div>
              <div class="text">
                <h5>深度咨询</h5>
                <span>解决复杂烦恼</span>
              </div>
            </div>

            <div class="glass-card action-item" @click="router.push('/meditation')">
              <div class="icon-box success-icon">🧘</div>
              <div class="text">
                <h5>冥想练习</h5>
                <span>5分钟放松引导</span>
              </div>
            </div>

            <div class="glass-card action-item" @click="router.push('/diary')">
              <div class="icon-box warning-icon">📝</div>
              <div class="text">
                <h5>情绪日记</h5>
                <span>记录当下心情</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="glass-modal tip-modal" @click.stop>
          <button class="close-btn" @click="closeModal">×</button>
          <div class="modal-header">
            <span class="modal-icon">{{ currentTip?.icon }}</span>
            <h3>{{ currentTip?.title }}</h3>
          </div>
          <div class="modal-body">
            <p v-for="(line, index) in formatContent(currentTip?.content)" :key="index">
              {{ line }}
            </p>
          </div>
          <button class="modal-action-btn" @click="handleAction('chat', 'practice')">
            让 AI 带我练习
          </button>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authStore } from '../store.js'; 

const router = useRouter();

// ================= 1. 动态问候语逻辑 =================
const hour = new Date().getHours();
const username = computed(() => authStore.username || '朋友');

const greeting = computed(() => {
  if (hour < 5) return '夜深了';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const timeIcon = computed(() => {
  if (hour < 6) return '🌙';
  if (hour < 18) return '☀️';
  return '✨';
});

// ================= 2. 每日治愈金句数据 =================
const quotesList = [
  { text: "接纳自己的不完美，是爱自己的开始。", author: "每日治愈" },
  { text: "万物皆有裂痕，那是光照进来的地方。", author: "莱昂纳德·科恩" },
  { text: "允许一切发生，你就是那个强大的观察者。", author: "海灵格" },
  { text: "生活不可能像你想象得那么好，但也不会像你想象得那么糟。", author: "莫泊桑" },
  { text: "你必须要精力充沛，才能抵挡世俗的万千琐事。", author: "查理·芒格" },
  { text: "慢慢来，谁还没有一个努力的过程。", author: "治愈君" }
];
const currentQuote = ref(quotesList[0]);

onMounted(() => {
  // 随机取一句
  const randomIndex = Math.floor(Math.random() * quotesList.length);
  currentQuote.value = quotesList[randomIndex];
});

// ================= 3. 心理锦囊数据 =================
const allTips = [
  { title: "缓解焦虑", icon: "🧘‍♀️", content: "尝试 '5-4-3-2-1' 着陆法：\n👀 寻找 5 样能看到的东西\n✋ 寻找 4 样能触碰的东西\n👂 寻找 3 样能听到的声音\n👃 寻找 2 样能闻到的气味\n👅 寻找 1 样能尝到的味道\n这能帮你快速回到当下。" },
  { title: "正念呼吸", icon: "🌬️", content: "4-7-8 呼吸法：\n1. 闭嘴，用鼻子吸气，心中默数 4 秒。\n2. 屏住呼吸，默数 7 秒。\n3. 用嘴呼气，发出'呼'的声音，默数 8 秒。\n重复 4 个循环。" },
  { title: "认知重构", icon: "🧠", content: "当你产生负面想法时，问自己三个问题：\n1. 我有证据支持这个想法吗？\n2. 有没有其他可能的解释？\n3. 即使这是真的，情况真的有那么糟吗？" },
  { title: "人际边界", icon: "🚧", content: "学会说'不'是自爱的表现。\n不需要为拒绝别人而感到内疚。你的感受和需求同样重要。\n温和而坚定地表达你的底线。" },
  { title: "助眠白噪音", icon: "💤", content: "睡不着时，试着想象自己是一块在阳光下慢慢融化的黄油，从头顶开始，放松额头、眼睛、下巴、肩膀...\n感受身体沉入床垫。" },
  { title: "停止内耗", icon: "🔋", content: "完成比完美更重要。\n很多时候，我们的焦虑来自于对结果的过度预设。\n试着只关注'当下这一步'，而不是'未来的一百步'。" }
];

const visibleTips = ref(allTips.slice(0, 5)); // 默认显示前5个

const showRandomTip = () => {
  // 随机洗牌
  visibleTips.value = [...allTips].sort(() => 0.5 - Math.random()).slice(0, 5);
};

// ================= 4. 模态框逻辑 (仅用于心理锦囊) =================
const showModal = ref(false);
const currentTip = ref(null);

const openTipModal = (tip) => {
  currentTip.value = tip;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const formatContent = (text) => {
  return text ? text.split('\n') : [];
};

// ================= 5. 通用跳转逻辑 =================
const handleAction = (route, mode) => {
  if (route === 'chat') {
    router.push('/chat');
    closeModal();
  }
};
</script>

<style scoped>
/* 样式部分完全保留，不做任何修改 */
@import '../assets/main.css';

.home-container {
  min-height: 100%; position: relative; overflow-x: hidden;
}

.content-wrapper {
  position: relative; z-index: 1; max-width: 1000px; margin: 0 auto; padding: 40px 20px;
}

.glass-card {
  background: var(--glass-bg); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: var(--glass-border); border-radius: 20px; padding: 24px;
  box-shadow: var(--glass-shadow); transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
}
.glass-card:hover {
  transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08); background: rgba(255, 255, 255, 0.8);
}

.hero-section {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;
  background: linear-gradient(120deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%);
}
.greeting-box { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.greeting-box h1 { margin: 0; font-size: 26px; color: var(--text-main); letter-spacing: 0.5px; }
.weather-icon { font-size: 28px; }
.subtitle { margin: 0 0 24px 0; color: var(--text-sub); font-size: 15px; }
.hero-decoration { font-size: 60px; opacity: 0.8; animation: float 6s ease-in-out infinite; }

.primary-btn {
  background: var(--primary-gradient); color: white; border: none; padding: 12px 32px; border-radius: 50px;
  font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(var(--primary-rgb), 0.3);
  display: flex; align-items: center; gap: 8px; transition: all 0.3s;
}
.primary-btn:hover { transform: scale(1.05); box-shadow: 0 6px 20px rgba(var(--primary-rgb), 0.4); }

.main-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px; }
.left-column, .right-column { display: flex; flex-direction: column; gap: 24px; }

.header-title { display: flex; align-items: center; gap: 8px; }
.header-title h4 { margin: 0; font-size: 17px; color: var(--text-main); }
.link-btn { background: none; border: none; color: var(--primary-color); cursor: pointer; font-size: 13px; }

.daily-quote {
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.5) 100%);
  border-left: 4px solid var(--primary-color); padding: 24px; min-height: 120px;
}
.quote-icon { font-size: 28px; color: var(--primary-color); opacity: 0.5; line-height: 1; display: block; margin-bottom: 8px; }
.quote-text { font-style: italic; color: #555; margin: 0 0 12px 0; font-size: 15px; line-height: 1.6; }
.quote-author { font-size: 13px; color: #999; display: block; text-align: right; }

.topic-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.topic-pill {
  padding: 10px 18px; border-radius: 12px;
  background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(255, 255, 255, 0.5);
  font-size: 14px; color: #555; cursor: pointer; transition: 0.2s;
}
.topic-pill:hover { background: #fff; color: var(--primary-color); border-color: var(--primary-color); transform: translateY(-2px); }
.topic-pill.highlight { background: rgba(var(--primary-rgb), 0.05); color: var(--primary-color); font-weight: 500; }

.action-list { display: flex; flex-direction: column; gap: 16px; }
.action-item {
  display: flex; align-items: center; gap: 16px; padding: 20px; cursor: pointer; background: rgba(255,255,255,0.7);
}
.icon-box {
  width: 46px; height: 46px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.primary-icon { background: rgba(var(--primary-rgb), 0.1); color: var(--primary-color); }
.success-icon { background: rgba(82, 196, 26, 0.1); color: var(--success-color); }
.warning-icon { background: rgba(250, 140, 22, 0.1); color: var(--warning-color); }

.text h5 { margin: 0 0 4px 0; font-size: 16px; color: var(--text-main); }
.text span { font-size: 13px; color: var(--text-sub); }

.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.3); z-index: 9999;
  display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px);
}
.glass-modal {
  width: 90%; max-width: 480px; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(16px);
  border-radius: 24px; padding: 32px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  position: relative; text-align: center;
}
.close-btn { position: absolute; top: 16px; right: 16px; background: none; border: none; font-size: 24px; color: #999; cursor: pointer; }
.modal-header { margin-bottom: 20px; }
.modal-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.modal-header h3 { margin: 0; font-size: 22px; color: var(--text-main); }
.modal-body { text-align: left; background: rgba(255,255,255,0.5); padding: 20px; border-radius: 12px; margin-bottom: 24px; }
.modal-body p { margin: 0 0 8px; font-size: 15px; line-height: 1.6; color: #555; }
.modal-action-btn {
  width: 100%; padding: 12px; background: var(--primary-color); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; transition: 0.2s;
}
.modal-action-btn:hover { opacity: 0.9; transform: scale(1.02); }

@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.slide-in-down { animation: slideDown 0.6s ease-out; }
.slide-in-up { animation: slideUp 0.6s ease-out backwards; }
.slide-in-right { animation: slideLeft 0.6s ease-out backwards; }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideLeft { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@media (max-width: 768px) {
  .main-grid { grid-template-columns: 1fr; }
  .hero-section { flex-direction: column; text-align: center; }
  .greeting-box { justify-content: center; }
  .hero-decoration { display: none; }
}
</style>
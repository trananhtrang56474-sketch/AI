<template>
  <div class="home-container">
    <div class="content-wrapper">
      
      <section class="hero-section glass-card slide-in-down">
        <div class="hero-content">
          <div class="greeting-box">
            <span class="weather-icon">{{ timeIcon }}</span>
            <h1>{{ greeting }}，朋友</h1>
          </div>
          <p class="subtitle">这里是你的心灵栖息地。所有的情绪，都值得被看见。</p>
          
          <button class="primary-btn pulse-effect" @click="startNewChat">
            <span class="btn-icon">✨</span> 开启一次心灵对话
          </button>
        </div>
        <div class="hero-decoration">🌱</div>
      </section>

      <div class="main-grid">
        
        <div class="left-column">
          
          <div class="glass-card daily-quote slide-in-up">
            <span class="quote-icon">❝</span>
            <p class="quote-text">接纳自己的不完美，是爱自己的开始。愿你今天拥有一份平和的心情。</p>
            <span class="quote-author">—— 每日治愈</span>
          </div>

          <div class="glass-card knowledge-hub slide-in-up" style="animation-delay: 0.1s">
            <div class="card-header">
              <div class="header-title">
                <span class="icon">🧩</span>
                <h4>心理锦囊</h4>
              </div>
              <button class="link-btn">查看全部</button>
            </div>
            <div class="topic-grid">
              <div class="topic-pill">🧘‍♀️ 缓解焦虑</div>
              <div class="topic-pill">🌬️ 正念呼吸</div>
              <div class="topic-pill">🧠 认知重构</div>
              <div class="topic-pill">🤝 人际关系</div>
              <div class="topic-pill">💤 助眠白噪音</div>
              <div class="topic-pill highlight">✨ 探索更多</div>
            </div>
          </div>
        </div>
        
        <div class="right-column slide-in-right">
          
          <div class="action-list">
            <div class="glass-card action-item" @click="startNewChat">
              <div class="icon-box primary-icon">💬</div>
              <div class="text">
                <h5>深度咨询</h5>
                <span>解决复杂烦恼</span>
              </div>
            </div>

            <div class="glass-card action-item">
              <div class="icon-box success-icon">🧘</div>
              <div class="text">
                <h5>冥想练习</h5>
                <span>5分钟放松</span>
              </div>
            </div>

            <div class="glass-card action-item">
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
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const hour = new Date().getHours();

const greeting = computed(() => {
  if (hour < 6) return '夜深了';
  if (hour < 11) return '早上好';
  if (hour < 13) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const timeIcon = computed(() => {
  if (hour < 6) return '🌙';
  if (hour < 18) return '☀️';
  return '✨';
});

const startNewChat = () => {
  router.push('/chat');
};
</script>

<style scoped>
/* === 1. 全局容器 === */
.home-container {
  min-height: 100%;
  position: relative;
  /* 字体继承 App.vue 设置 */
  overflow-x: hidden;
}

.content-wrapper {
  position: relative; z-index: 1;
  max-width: 1000px;
  margin: 0 auto; padding: 40px 20px;
}

/* === 2. 磨砂玻璃卡片通用类 (使用变量) === */
.glass-card {
  background: var(--glass-bg); /* ✅ 引用全局变量 */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: var(--glass-border); /* ✅ 引用全局变量 */
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--glass-shadow); /* ✅ 引用全局变量 */
  transition: transform 0.3s, box-shadow 0.3s, background 0.3s;
}
.glass-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.8);
}

/* === 3. Hero 区域 === */
.hero-section {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 30px;
  /* 稍微加一点白色渐变，增加层次感 */
  background: linear-gradient(120deg, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.4) 100%);
}
.greeting-box { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.greeting-box h1 { margin: 0; font-size: 26px; color: var(--text-main); letter-spacing: 0.5px; }
.weather-icon { font-size: 28px; }
.subtitle { margin: 0 0 24px 0; color: var(--text-sub); font-size: 15px; }
.hero-decoration { font-size: 60px; opacity: 0.8; animation: float 6s ease-in-out infinite; }

/* 主按钮 (使用变量) */
.primary-btn {
  background: var(--primary-gradient); /* ✅ 引用全局渐变 */
  color: white; border: none; padding: 12px 32px; border-radius: 50px;
  font-size: 16px; font-weight: 600; cursor: pointer;
  /* 阴影使用主色调的 RGB 变量 */
  box-shadow: 0 4px 15px rgba(var(--primary-rgb), 0.3);
  display: flex; align-items: center; gap: 8px; transition: all 0.3s;
}
.primary-btn:hover { 
  transform: scale(1.05); 
  box-shadow: 0 6px 20px rgba(var(--primary-rgb), 0.4); 
}

/* === 4. 布局 === */
.main-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px; }
.left-column, .right-column { display: flex; flex-direction: column; gap: 24px; }

/* 标题样式 */
.header-title { display: flex; align-items: center; gap: 8px; }
.header-title h4 { margin: 0; font-size: 17px; color: var(--text-main); }
.link-btn { background: none; border: none; color: var(--primary-color); cursor: pointer; font-size: 13px; }

/* 每日心语 */
.daily-quote {
  background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.5) 100%);
  border-left: 4px solid var(--primary-color); /* ✅ 跟随主色 */
  padding: 24px;
}
.quote-icon { font-size: 28px; color: var(--primary-color); opacity: 0.5; line-height: 1; display: block; margin-bottom: 8px; }
.quote-text { font-style: italic; color: #555; margin: 0 0 12px 0; font-size: 15px; line-height: 1.6; }
.quote-author { font-size: 13px; color: #999; display: block; text-align: right; }

/* 知识库 Pill */
.topic-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.topic-pill {
  padding: 10px 18px; border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.5);
  font-size: 14px; color: #555; cursor: pointer; transition: 0.2s;
}
.topic-pill:hover { 
  background: #fff; 
  color: var(--primary-color); /* ✅ 跟随主色 */
  border-color: var(--primary-color);
  transform: translateY(-2px); 
}
.topic-pill.highlight { 
  background: rgba(var(--primary-rgb), 0.05); /* ✅ 淡淡的主色背景 */
  color: var(--primary-color); 
  font-weight: 500; 
}

/* 功能列表 */
.action-list { display: flex; flex-direction: column; gap: 16px; }
.action-item {
  display: flex; align-items: center; gap: 16px; padding: 20px; cursor: pointer;
  background: rgba(255,255,255,0.7);
}
.icon-box {
  width: 46px; height: 46px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center; font-size: 22px;
}

/* ✨ 优化：使用语义化变量 */
.primary-icon { 
  background: rgba(var(--primary-rgb), 0.1); 
  color: var(--primary-color); 
}
.success-icon { 
  background: rgba(82, 196, 26, 0.1); /* 也可以定义 --success-rgb */
  color: var(--success-color); 
}
.warning-icon { 
  background: rgba(250, 140, 22, 0.1); 
  color: var(--warning-color); 
}

.text h5 { margin: 0 0 4px 0; font-size: 16px; color: var(--text-main); }
.text span { font-size: 13px; color: var(--text-sub); }

/* 动画 */
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.slide-in-down { animation: slideDown 0.6s ease-out; }
.slide-in-up { animation: slideUp 0.6s ease-out backwards; }
.slide-in-right { animation: slideLeft 0.6s ease-out backwards; }

@keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideLeft { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }

/* 手机适配 */
@media (max-width: 768px) {
  .main-grid { grid-template-columns: 1fr; }
  .hero-section { flex-direction: column; text-align: center; }
  .greeting-box { justify-content: center; }
  .hero-decoration { display: none; }
}
</style>
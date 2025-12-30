<template>
  <div class="landing-page">
    <div class="ambient-light">
      <div class="light-orb orb-1"></div>
      <div class="light-orb orb-2"></div>
      <div class="light-orb orb-3"></div>
    </div>

    <nav class="navbar" :class="{ 'scrolled': isScrolled }">
      <div class="nav-content">
        <div class="brand">
          <span class="brand-logo">🧠</span>
          <span class="brand-text">AI 心灵伴侣</span>
        </div>
        
        <div class="menu">
          <a 
            href="#vision" 
            :class="{ active: activeSection === 'vision' }"
            @click.prevent="scrollTo('#vision')"
          >
            愿景
          </a>
          <a 
            href="#features" 
            :class="{ active: activeSection === 'features' }"
            @click.prevent="scrollTo('#features')"
          >
            功能
          </a>
          <a 
            href="#process" 
            :class="{ active: activeSection === 'process' }"
            @click.prevent="scrollTo('#process')"
          >
            流程
          </a>
        </div>

        <button class="enter-btn" @click="goToApp">
          进入控制台
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </nav>

    <section class="screen hero-screen">
      <div class="screen-content">
        <div class="hero-text-wrapper reveal-item">
          <div class="tag">✨ 2025 毕业设计作品</div>
          <h1 class="hero-title">
            <span class="line">重塑内心的</span>
            <span class="line highlight">平静与秩序</span>
          </h1>
          <p class="hero-desc">
            结合多模态情绪识别与 RAG 知识库的 AI 心理顾问。<br>
            在这个喧嚣的数字世界，为你留一处私密、安全的心灵栖息地。
          </p>
          <div class="hero-actions">
            <button class="primary-btn big" @click="goToApp">立即体验</button>
            <button class="text-btn" @click="scrollTo('#vision')">了解更多 ↓</button>
          </div>
        </div>
        
        <div class="hero-visual reveal-item delay-200">
          <div class="glass-card main-card">
            <div class="chat-header">
              <div class="avatar ai">AI</div>
              <div class="status">正在输入...</div>
            </div>
            <div class="chat-body">
              <div class="msg ai">你好，我是你的 AI 心理顾问。今天遇到什么想聊聊的事了吗？</div>
              <div class="msg user">最近感觉压力很大，总是睡不着...</div>
              <div class="msg ai-reply">
                <div class="reply-line short"></div>
                <div class="reply-line long"></div>
              </div>
            </div>
            <div class="float-card float-1">
              <span>😊</span> 情绪指数 <strong>8.5</strong>
            </div>
            <div class="float-card float-2">
              <span>🔒</span> 隐私加密 <strong>ON</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="vision" class="screen vision-screen">
      <div class="screen-content column-layout">
        <div class="section-head reveal-item">
          <h2>现代人的隐形重担</h2>
          <p>我们都在寻找一个出口，却往往无处可去</p>
        </div>
        
        <div class="cards-row">
          <div class="hover-card reveal-item delay-100">
            <div class="card-icon">🌑</div>
            <h3>孤独感</h3>
            <p>通讯录里有几百人，深夜却找不到一个可以倾诉的对象。</p>
          </div>
          <div class="hover-card reveal-item delay-200">
            <div class="card-icon">💸</div>
            <h3>高昂成本</h3>
            <p>专业咨询单次费用高昂，预约周期长，难以应对突发情绪。</p>
          </div>
          <div class="hover-card reveal-item delay-300">
            <div class="card-icon">😶</div>
            <h3>难以启齿</h3>
            <p>担心秘密泄露，害怕被他人评判，选择将情绪压抑在心底。</p>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="screen feature-screen">
      <div class="screen-content row-layout">
        <div class="feature-text reveal-item">
          <h2>科技的温度</h2>
          <p class="big-desc">不仅仅是代码，更是懂你的拥抱。</p>
          
          <ul class="feature-list">
            <li>
              <span class="check">✓</span>
              <div>
                <strong>共情对话引擎</strong>
                <p>识别微表情与语调，给予真正温暖的回应。</p>
              </div>
            </li>
            <li>
              <span class="check">✓</span>
              <div>
                <strong>RAG 知识增强</strong>
                <p>基于 CBT (认知行为疗法) 知识库，建议科学有效。</p>
              </div>
            </li>
            <li>
              <span class="check">✓</span>
              <div>
                <strong>情绪可视化</strong>
                <p>生成情绪趋势图，看见每一次积极的改变。</p>
              </div>
            </li>
          </ul>
        </div>
        
        <div class="feature-visual reveal-item delay-200">
          <div class="data-vis-card">
            <div class="graph-bars">
              <div class="bar" style="height: 40%"></div>
              <div class="bar" style="height: 70%"></div>
              <div class="bar" style="height: 50%"></div>
              <div class="bar active" style="height: 90%">
                <div class="tooltip">Mood: Happy</div>
              </div>
              <div class="bar" style="height: 60%"></div>
            </div>
            <div class="graph-label">情绪积极度趋势</div>
          </div>
        </div>
      </div>
    </section>

    <section id="process" class="screen process-screen">
      <div class="screen-content column-layout">
        <div class="section-head reveal-item">
          <h2>开启治愈之旅</h2>
        </div>
        
        <div class="process-steps reveal-item">
          <div class="step">
            <div class="step-num">01</div>
            <h3>进入平台</h3>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-num">02</div>
            <h3>自由倾诉</h3>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-num">03</div>
            <h3>获得洞察</h3>
          </div>
        </div>

        <div class="final-cta reveal-item delay-200">
          <h2>准备好开始了吗？</h2>
          <button class="primary-btn huge" @click="goToApp">
            进入 AI 心理顾问控制台
          </button>
          <p class="copyright">© 2025 AI Counselor Project. Graduation Design.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isScrolled = ref(false);
const activeSection = ref(''); // 记录当前在哪个板块

const goToApp = () => {
  router.push('/home');
};

const scrollTo = (selector) => {
  const el = document.querySelector(selector);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
};

// --- 滚动显现动画 (Reveal Animation) ---
const setupRevealObserver = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal-item').forEach(el => observer.observe(el));
};

// --- 滚动监听高亮 (Scroll Spy) ---
const setupScrollSpy = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      // 当板块交叉进入视口中心线时，更新 activeSection
      if (entry.isIntersecting) {
        activeSection.value = entry.target.id;
      }
    });
  }, {
    // 关键参数：把视口缩小到中间一条线，实现精准判断
    rootMargin: "-50% 0px -50% 0px"
  });

  // 监听所有带 id 的 section
  document.querySelectorAll('section[id]').forEach(section => {
    observer.observe(section);
  });
};

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50;
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  setupRevealObserver();
  setupScrollSpy();
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* 引入字体 */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* --- 全局 --- */
.landing-page {
  font-family: 'Space Grotesk', -apple-system, sans-serif;
  background-color: #f8fafc;
  color: #1e293b;
  overflow-x: hidden;
  position: relative;
  /* 确保全屏宽度 */
  width: 100vw;
  min-height: 100vh;
}

/* 沉浸式背景光 */
.ambient-light {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 0; pointer-events: none; overflow: hidden;
}
.light-orb { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.6; }
.orb-1 { width: 60vw; height: 60vw; background: radial-gradient(circle, #e0f2fe 0%, transparent 70%); top: -20%; right: -20%; }
.orb-2 { width: 50vw; height: 50vw; background: radial-gradient(circle, #f0fdf4 0%, transparent 70%); bottom: -10%; left: -10%; }
.orb-3 { width: 30vw; height: 30vw; background: radial-gradient(circle, #f5f3ff 0%, transparent 70%); top: 40%; left: 30%; opacity: 0.3; }

/* --- 动画类 --- */
.reveal-item {
  opacity: 0;
  transform: translateY(60px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.reveal-item.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }
.delay-200 { transition-delay: 0.2s; }
.delay-300 { transition-delay: 0.3s; }

/* --- 屏幕通用布局 --- */
.screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  padding: 80px 40px;
  box-sizing: border-box;
}

.screen-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* --- 导航栏 (包含高亮逻辑) --- */
.navbar {
  position: fixed; top: 0; left: 0; width: 100%; height: 90px;
  z-index: 1000; transition: all 0.4s ease;
  display: flex; align-items: center; justify-content: center;
}
.navbar.scrolled {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  height: 70px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}
.nav-content {
  width: 100%; max-width: 1400px; padding: 0 40px;
  display: flex; justify-content: space-between; align-items: center;
}
.brand { font-size: 20px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px; }
.brand-logo { font-size: 24px; }

/* 菜单样式 */
.menu { display: flex; gap: 40px; }
.menu a { 
  text-decoration: none; 
  color: #64748b; 
  font-weight: 500; 
  font-size: 15px; 
  transition: all 0.3s; 
  position: relative;
  padding: 5px 0;
}

/* 激活或悬停状态 */
.menu a:hover,
.menu a.active { 
  color: #1890ff; 
  font-weight: 600;
}

/* 下划线动画 */
.menu a::after { 
  content: ''; 
  position: absolute; 
  bottom: 0; 
  left: 0; 
  width: 0; 
  height: 2px; 
  background: #1890ff; 
  transition: width 0.3s ease; 
  border-radius: 2px;
}
/* 激活时展开下划线 */
.menu a:hover::after,
.menu a.active::after { 
  width: 100%; 
}

.enter-btn {
  background: #0f172a; color: #fff; border: none; padding: 10px 20px; border-radius: 50px;
  font-weight: 600; cursor: pointer; transition: all 0.3s; display: flex; align-items: center; gap: 6px;
}
.enter-btn:hover { background: #1890ff; transform: scale(1.05); }
.icon { width: 16px; height: 16px; }

/* --- Screen 1: Hero --- */
.hero-screen .screen-content {
  display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center;
}
.tag {
  display: inline-block; padding: 6px 14px; background: rgba(24, 144, 255, 0.1); color: #1890ff;
  border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 24px;
}
.hero-title {
  font-size: 72px; line-height: 1.1; font-weight: 800; color: #0f172a; margin-bottom: 24px;
  letter-spacing: -2px;
}
.hero-title .line { display: block; }
.hero-title .highlight { 
  background: linear-gradient(120deg, #1890ff, #3b82f6); -webkit-background-clip: text; background-clip: text; color: transparent; 
}
.hero-desc { font-size: 20px; color: #64748b; line-height: 1.6; margin-bottom: 40px; max-width: 500px; }
.hero-actions { display: flex; gap: 20px; align-items: center; }
.primary-btn {
  background: #1890ff; color: #fff; border: none; padding: 16px 40px; border-radius: 12px;
  font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 20px 40px rgba(24, 144, 255, 0.3);
  transition: all 0.3s;
}
.primary-btn:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 25px 50px rgba(24, 144, 255, 0.4); }
.text-btn { background: none; border: none; font-size: 16px; color: #64748b; cursor: pointer; font-weight: 500; }
.text-btn:hover { color: #1890ff; }

/* 玻璃卡片 */
.hero-visual { position: relative; perspective: 1000px; }
.glass-card {
  background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 24px;
  padding: 24px; box-shadow: 0 40px 80px -10px rgba(0, 0, 0, 0.1);
  transform: rotateY(-10deg) rotateX(5deg); transition: transform 0.5s ease;
}
.glass-card:hover { transform: rotateY(0) rotateX(0); }
.chat-header { display: flex; justify-content: space-between; margin-bottom: 20px; align-items: center; }
.avatar.ai { width: 40px; height: 40px; background: #1890ff; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.status { font-size: 12px; color: #1890ff; }
.chat-body { display: flex; flex-direction: column; gap: 12px; }
.msg { padding: 12px 16px; border-radius: 12px; font-size: 14px; max-width: 80%; }
.msg.ai { background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); align-self: flex-start; }
.msg.user { background: #1890ff; color: #fff; align-self: flex-end; }
.reply-line { height: 8px; background: #e2e8f0; border-radius: 4px; margin-bottom: 6px; }
.reply-line.short { width: 60%; } .reply-line.long { width: 90%; }
.float-card {
  position: absolute; background: #fff; padding: 10px 16px; border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1); font-size: 13px; font-weight: 600;
  display: flex; gap: 8px; align-items: center; animation: float 6s infinite ease-in-out;
}
.float-1 { top: -20px; right: -20px; animation-delay: 0s; }
.float-2 { bottom: -20px; left: -20px; animation-delay: 2s; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }

/* --- Screen 2: Vision --- */
.vision-screen { background: #fff; }
.column-layout { text-align: center; }
.section-head h2 { font-size: 48px; margin-bottom: 16px; color: #0f172a; letter-spacing: -1px; }
.section-head p { font-size: 18px; color: #64748b; margin-bottom: 80px; }
.cards-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }
.hover-card {
  text-align: left; padding: 40px; border-radius: 24px; background: #f8fafc;
  transition: all 0.4s; border: 1px solid transparent;
}
.hover-card:hover { background: #fff; box-shadow: 0 30px 60px rgba(0,0,0,0.08); transform: translateY(-10px); border-color: #e2e8f0; }
.card-icon { font-size: 40px; margin-bottom: 24px; }
.hover-card h3 { font-size: 24px; margin-bottom: 12px; }
.hover-card p { color: #64748b; line-height: 1.6; }

/* --- Screen 3: Features --- */
.row-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
.big-desc { font-size: 24px; font-weight: 300; color: #475569; margin-bottom: 40px; }
.feature-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 30px; }
.feature-list li { display: flex; gap: 20px; }
.check { width: 24px; height: 24px; background: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-weight: bold; }
.feature-list strong { font-size: 18px; display: block; margin-bottom: 4px; }
.feature-list p { color: #64748b; margin: 0; }

.data-vis-card {
  background: #fff; padding: 40px; border-radius: 24px; box-shadow: 0 30px 60px rgba(0,0,0,0.08);
  height: 400px; display: flex; flex-direction: column; justify-content: flex-end; align-items: center;
}
.graph-bars { display: flex; align-items: flex-end; gap: 20px; height: 300px; width: 100%; justify-content: center; }
.bar { width: 40px; background: #e2e8f0; border-radius: 8px 8px 0 0; position: relative; transition: height 1s; }
.bar.active { background: #1890ff; box-shadow: 0 0 20px rgba(24, 144, 255, 0.4); }
.tooltip {
  position: absolute; top: -40px; left: 50%; transform: translateX(-50%);
  background: #0f172a; color: #fff; padding: 6px 12px; border-radius: 6px; font-size: 12px; white-space: nowrap;
}
.graph-label { margin-top: 20px; font-weight: 600; color: #64748b; }

/* --- Screen 4: Process & Footer --- */
.process-screen { background: #0f172a; color: #fff; text-align: center; }
.process-screen .section-head h2 { color: #fff; }
.process-steps { display: flex; justify-content: center; align-items: center; gap: 60px; margin-bottom: 100px; }
.step { position: relative; }
.step-num { font-size: 60px; font-weight: 900; color: rgba(255,255,255,0.1); margin-bottom: -30px; }
.step h3 { font-size: 24px; position: relative; z-index: 1; }
.step-line { width: 100px; height: 2px; background: rgba(255,255,255,0.1); }

.final-cta h2 { font-size: 48px; margin-bottom: 40px; }
.primary-btn.huge { font-size: 20px; padding: 20px 60px; border-radius: 50px; }
.copyright { margin-top: 80px; color: #475569; font-size: 14px; }
</style>
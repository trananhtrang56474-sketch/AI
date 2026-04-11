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
          <span class="brand-logo">⌘</span>
          <span class="brand-text">AI 心灵伴侣</span>
        </div>
        
        <div class="menu">
          <a href="#vision" @click.prevent="scrollTo('#vision')" :class="{ active: activeSection === 'vision' }">愿景</a>
          <a href="#features" @click.prevent="scrollTo('#features')" :class="{ active: activeSection === 'features' }">功能</a>
          
          <div v-if="isLoggedIn" class="user-menu">
            <span class="greeting">Hi, {{ username }}</span>
            <a href="#" @click.prevent="handleLogout" class="logout-link">退出</a>
          </div>
          <div v-else>
            <router-link to="/login" class="nav-item">登录</router-link>
          </div>
        </div>

        <button class="enter-btn" @click="handleMainAction">
          <span>{{ isLoggedIn ? '主页' : '注册账号' }}</span>
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </nav>

    <section class="screen hero-screen">
      <div class="screen-content">
        <div class="hero-text-wrapper reveal-item blur-reveal">
          <div class="tag-wrapper">
            <div class="tag">✨ 2026 毕业设计作品</div>
          </div>
          <h1 class="hero-title">
            <span class="line">重塑内心的</span>
            <span class="line highlight">平静与秩序。</span>
          </h1>
          <p class="hero-desc">
            结合多模态情绪识别与 RAG 知识库的 AI 心理顾问。<br>
            在这个喧嚣的数字世界，为你留一处私密、安全的栖息地。
          </p>
          <div class="hero-actions">
            <button class="primary-btn big" @click="handleMainAction">
              {{ isLoggedIn ? '继续咨询' : '立即体验' }}
            </button>
            <button class="text-btn" @click="scrollTo('#vision')">了解更多 <span class="arrow">↓</span></button>
          </div>
        </div>
        
        <div class="hero-visual reveal-item blur-reveal delay-200">
          <div class="glass-card main-card">
            <div class="chat-header">
              <div class="avatar ai">AI</div>
              <div class="status">
                <span class="pulse-dot"></span> 正在聆听...
              </div>
            </div>
            <div class="chat-body">
              <div class="msg ai">你好，我是你的专属 AI 顾问。今天遇到什么想聊聊的事了吗？</div>
              <div class="msg user">最近感觉面临毕业，压力很大，总是睡不着...</div>
              <div class="msg ai-reply">
                <div class="reply-line short"></div>
                <div class="reply-line long"></div>
              </div>
            </div>
            <div class="float-card float-1 glass-panel">
              <div class="icon-box blue">😊</div> 
              <div class="info"><span>情绪指数</span><strong>8.5</strong></div>
            </div>
            <div class="float-card float-2 glass-panel">
              <div class="icon-box green">🔒</div> 
              <div class="info"><span>隐私加密</span><strong>ON</strong></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="vision" class="screen vision-screen">
      <div class="screen-content column-layout">
        <div class="section-head reveal-item blur-reveal">
          <h2 class="section-title">现代人的隐形重担。</h2>
          <p class="section-subtitle">我们都在寻找一个出口，却往往无处可去。</p>
        </div>
        
        <div class="bento-grid">
          <div class="bento-card reveal-item blur-reveal delay-100">
            <div class="card-icon">🌑</div>
            <h3>无尽的孤独感</h3>
            <p>通讯录里有几百人，深夜却找不到一个可以毫无保留倾诉的对象。</p>
          </div>
          <div class="bento-card reveal-item blur-reveal delay-200">
            <div class="card-icon">💸</div>
            <h3>高昂的试错成本</h3>
            <p>专业心理咨询单次费用高昂，预约周期长，难以应对突发的崩溃情绪。</p>
          </div>
          <div class="bento-card reveal-item blur-reveal delay-300">
            <div class="card-icon">😶</div>
            <h3>难以启齿的秘密</h3>
            <p>担心隐私泄露，害怕被他人主观评判，最终选择将情绪死死压抑在心底。</p>
          </div>
        </div>
      </div>
    </section>

    <section id="features" class="screen feature-screen">
      <div class="screen-content row-layout">
        <div class="feature-text reveal-item blur-reveal">
          <h2 class="section-title">科技的温度。</h2>
          <p class="section-subtitle">不仅仅是冷冰冰的代码，更是懂你的拥抱。</p>
          
          <ul class="feature-list">
            <li>
              <div class="icon-wrapper"><span class="check">✓</span></div>
              <div class="text-content">
                <strong>共情对话引擎</strong>
                <p>精准识别微表情与语调，给予你当下最需要的温暖回应与情感支持。</p>
              </div>
            </li>
            <li>
              <div class="icon-wrapper"><span class="check">✓</span></div>
              <div class="text-content">
                <strong>RAG 知识增强</strong>
                <p>基于 CBT (认知行为疗法) 权威知识库，提供不仅温暖更具有科学性的建议。</p>
              </div>
            </li>
            <li>
              <div class="icon-wrapper"><span class="check">✓</span></div>
              <div class="text-content">
                <strong>情绪可视化追踪</strong>
                <p>生成专属情绪趋势图表，让你直观看见自己的每一次积极改变与成长。</p>
              </div>
            </li>
          </ul>
        </div>
        
        <div class="feature-visual reveal-item blur-reveal delay-200">
          <div class="data-vis-card glass-panel">
            <div class="graph-header">
              <span class="dot"></span> 情绪积极度趋势图
            </div>
            <div class="graph-bars">
              <div class="bar" style="height: 30%"></div>
              <div class="bar" style="height: 55%"></div>
              <div class="bar" style="height: 40%"></div>
              <div class="bar active" style="height: 85%">
                <div class="tooltip glass-tooltip">Status: Relieved</div>
              </div>
              <div class="bar" style="height: 65%"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="process" class="screen process-screen">
      <div class="screen-content column-layout">
        <div class="process-steps reveal-item blur-reveal">
          <div class="step">
            <div class="step-num">01</div>
            <h3>登录平台</h3>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-num">02</div>
            <h3>自由倾诉</h3>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-num">03</div>
            <h3>获得治愈</h3>
          </div>
        </div>

        <div class="final-cta reveal-item blur-reveal delay-200">
          <h2>准备好重新认识自己了吗？</h2>
          <button class="primary-btn ultra-huge" @click="handleMainAction">
            {{ isLoggedIn ? '进入主页' : '注册账号开启体验' }}
          </button>
          <p class="copyright">
            Designed & Engineered with ❤️<br>
            © 2026 AI Counselor Project. Graduation Design.
          </p>
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
const activeSection = ref(''); 
const isLoggedIn = ref(false);
const username = ref('');

const checkLoginStatus = () => {
  const userId = localStorage.getItem('user_id');
  const storedName = localStorage.getItem('username');
  if (userId) {
    isLoggedIn.value = true;
    username.value = storedName || 'User';
  } else {
    isLoggedIn.value = false;
    username.value = '';
  }
};

const handleMainAction = () => {
  if (isLoggedIn.value) {
    router.push('/home');
  } else {
    router.push('/login?mode=register');
  }
};

const handleLogout = () => {
  localStorage.removeItem('user_id');
  localStorage.removeItem('username');
  isLoggedIn.value = false;
  username.value = '';
};

const scrollTo = (selector) => {
  const el = document.querySelector(selector);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' });
  }
};

// 🔥 核心动画监听器优化
const setupRevealObserver = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { 
    threshold: 0.15, // 元素出现 15% 才触发，避免过早
    rootMargin: "0px 0px -50px 0px" // 底部提前量
  });

  document.querySelectorAll('.reveal-item').forEach(el => observer.observe(el));
};

const setupScrollSpy = () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        activeSection.value = entry.target.id;
      }
    });
  }, { rootMargin: "-40% 0px -60% 0px" });

  document.querySelectorAll('section[id]').forEach(section => observer.observe(section));
};

const handleScroll = () => {
  // Apple 风格通常很早就触发导航栏高斯模糊
  isScrolled.value = window.scrollY > 20; 
};

onMounted(() => {
  checkLoginStatus();
  window.addEventListener('scroll', handleScroll, { passive: true });
  // 延迟初始化动画，确保 DOM 渲染完毕
  setTimeout(() => {
    setupRevealObserver();
    setupScrollSpy();
  }, 100);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* 引入更现代的无衬线字体，类似 Apple 的 San Francisco */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* --- 全局重置与变量 --- */
.landing-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: #fbfbfd; /* Apple 经典灰白底色 */
  color: #1d1d1f;
  overflow-x: hidden;
  position: relative;
  width: 100vw;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* --- 动态高级氛围光 (更柔和、有呼吸感) --- */
.ambient-light {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 0; pointer-events: none; overflow: hidden;
}
.light-orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.5; animation: breathe 10s infinite alternate; }
.orb-1 { width: 60vw; height: 60vw; background: radial-gradient(circle, #e0f2fe 0%, transparent 70%); top: -10%; right: -20%; animation-delay: 0s; }
.orb-2 { width: 50vw; height: 50vw; background: radial-gradient(circle, #f0fdf4 0%, transparent 70%); bottom: -20%; left: -10%; animation-delay: -3s; }
.orb-3 { width: 40vw; height: 40vw; background: radial-gradient(circle, #e0e7ff 0%, transparent 70%); top: 30%; left: 20%; opacity: 0.4; animation-delay: -6s; }

@keyframes breathe {
  0% { transform: scale(1) translate(0, 0); opacity: 0.4; }
  100% { transform: scale(1.1) translate(-2%, 2%); opacity: 0.6; }
}

/* --- 顶级进场动画 (高斯模糊 + 缩放 + 弹簧曲线) --- */
.reveal-item.blur-reveal {
  opacity: 0;
  transform: translateY(40px) scale(0.98);
  filter: blur(12px);
  transition: opacity 1s cubic-bezier(0.2, 0.8, 0.2, 1),
              transform 1.2s cubic-bezier(0.2, 0.8, 0.2, 1),
              filter 1s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.reveal-item.blur-reveal.visible {
  opacity: 1; transform: translateY(0) scale(1); filter: blur(0);
}
.delay-100 { transition-delay: 0.1s; }
.delay-200 { transition-delay: 0.2s; }
.delay-300 { transition-delay: 0.3s; }

/* --- 屏幕通用布局 --- */
.screen {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; z-index: 1; padding: 120px 5%; box-sizing: border-box;
}
.screen-content { width: 100%; max-width: 1200px; margin: 0 auto; }

/* --- 导航栏 (极致毛玻璃) --- */
.navbar {
  position: fixed; top: 0; left: 0; width: 100%; height: 80px;
  z-index: 1000; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex; align-items: center; justify-content: center;
}
.navbar.scrolled {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  height: 60px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}
.nav-content {
  width: 100%; max-width: 1400px; padding: 0 40px;
  display: flex; justify-content: space-between; align-items: center;
}
.brand { font-size: 20px; font-weight: 700; color: #1d1d1f; display: flex; align-items: center; gap: 8px; letter-spacing: -0.5px; }

.menu { display: flex; gap: 32px; align-items: center; }
.menu a { 
  text-decoration: none; color: #86868b; font-size: 14px; font-weight: 500; 
  transition: color 0.3s ease; position: relative;
}
.menu a:hover, .menu a.active { color: #1d1d1f; }
.user-menu { display: flex; gap: 16px; align-items: center; }
.greeting { color: #1d1d1f; font-weight: 600; font-size: 14px; }
.logout-link { color: #ff3b30 !important; }

.enter-btn {
  background: #1d1d1f; color: #fff; border: none; padding: 8px 16px; border-radius: 20px;
  font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 6px;
}
.enter-btn:hover { background: #0071e3; transform: scale(1.02); }
.icon { width: 14px; height: 14px; }

/* --- Screen 1: Hero (排版质感) --- */
.hero-screen .screen-content { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 80px; align-items: center; }
.tag-wrapper { margin-bottom: 24px; }
.tag {
  display: inline-block; padding: 8px 16px; background: rgba(0, 113, 227, 0.08); color: #0071e3;
  border-radius: 20px; font-size: 13px; font-weight: 600; letter-spacing: 0.5px;
}
.hero-title {
  font-size: 80px; line-height: 1.05; font-weight: 800; color: #1d1d1f; margin-bottom: 24px;
  letter-spacing: -3px; /* 负字间距是 Apple 风格的灵魂 */
}
.hero-title .line { display: block; }
.hero-title .highlight { 
  background: linear-gradient(135deg, #0071e3 0%, #4facfe 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent; 
}
.hero-desc { font-size: 21px; color: #86868b; line-height: 1.5; margin-bottom: 48px; font-weight: 400; letter-spacing: -0.2px; }
.hero-actions { display: flex; gap: 24px; align-items: center; }
.primary-btn {
  background: #0071e3; color: #fff; border: none; padding: 18px 36px; border-radius: 30px;
  font-size: 17px; font-weight: 600; cursor: pointer; 
  box-shadow: 0 10px 20px rgba(0, 113, 227, 0.2); transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.primary-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 30px rgba(0, 113, 227, 0.3); }
.text-btn { background: none; border: none; font-size: 17px; color: #1d1d1f; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 4px; }
.text-btn:hover { color: #0071e3; }
.text-btn:hover .arrow { transform: translateY(3px); }
.arrow { transition: transform 0.3s ease; display: inline-block; }

/* 主视觉 3D 卡片 */
.hero-visual { position: relative; perspective: 1200px; }
.glass-card {
  background: rgba(255, 255, 255, 0.6); backdrop-filter: saturate(180%) blur(40px);
  -webkit-backdrop-filter: saturate(180%) blur(40px);
  border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 30px;
  padding: 30px; box-shadow: 0 50px 100px -20px rgba(0, 0, 0, 0.12), inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  transform: rotateY(-8deg) rotateX(4deg); transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.glass-card:hover { transform: rotateY(0) rotateX(0); }

/* 聊天气泡样式 */
.chat-header { display: flex; justify-content: space-between; margin-bottom: 24px; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.05); padding-bottom: 16px; }
.avatar.ai { width: 44px; height: 44px; background: linear-gradient(135deg, #0071e3, #4facfe); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; box-shadow: 0 4px 12px rgba(0,113,227,0.3); }
.status { font-size: 13px; color: #86868b; display: flex; align-items: center; gap: 6px;}
.pulse-dot { width: 8px; height: 8px; background: #34c759; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.4); } 70% { box-shadow: 0 0 0 6px rgba(52, 199, 89, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 199, 89, 0); } }

.chat-body { display: flex; flex-direction: column; gap: 16px; }
.msg { padding: 14px 18px; border-radius: 18px; font-size: 15px; max-width: 85%; line-height: 1.5; }
.msg.ai { background: rgba(255,255,255,0.8); box-shadow: 0 4px 15px rgba(0,0,0,0.03); align-self: flex-start; border-bottom-left-radius: 4px; }
.msg.user { background: #0071e3; color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
.reply-line { height: 10px; background: rgba(0,0,0,0.05); border-radius: 5px; margin-bottom: 8px; }
.reply-line.short { width: 60%; } .reply-line.long { width: 90%; }

/* 悬浮面板 */
.glass-panel {
  background: rgba(255, 255, 255, 0.8); backdrop-filter: saturate(180%) blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5); box-shadow: 0 20px 40px rgba(0,0,0,0.08);
  border-radius: 20px; padding: 12px 20px; display: flex; gap: 12px; align-items: center;
}
.float-card { position: absolute; animation: float 6s infinite ease-in-out; }
.float-1 { top: -30px; right: -30px; animation-delay: 0s; }
.float-2 { bottom: -30px; left: -30px; animation-delay: 3s; }
.icon-box { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.icon-box.blue { background: #e0f2fe; } .icon-box.green { background: #dcfce7; }
.info span { display: block; font-size: 11px; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; }
.info strong { font-size: 16px; color: #1d1d1f; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }

/* --- 通用 Section 标题 --- */
.section-title { font-size: 56px; font-weight: 700; letter-spacing: -2px; margin-bottom: 16px; color: #1d1d1f; }
.section-subtitle { font-size: 24px; color: #86868b; font-weight: 400; letter-spacing: -0.5px; margin-bottom: 60px; }

/* --- Screen 2: Vision (Bento Grid) --- */
.vision-screen { background: #fff; }
.column-layout { text-align: center; }
.bento-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; }
.bento-card {
  text-align: left; padding: 40px; border-radius: 30px; background: #fbfbfd;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); border: 1px solid transparent;
}
.bento-card:hover { background: #fff; box-shadow: 0 30px 60px rgba(0,0,0,0.05); transform: translateY(-5px); border-color: rgba(0,0,0,0.05); }
.card-icon { font-size: 48px; margin-bottom: 24px; display: inline-block; }
.bento-card h3 { font-size: 24px; font-weight: 600; margin-bottom: 12px; letter-spacing: -0.5px; }
.bento-card p { color: #86868b; line-height: 1.6; font-size: 16px; }

/* --- Screen 3: Features --- */
.row-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 100px; align-items: center; }
.feature-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 40px; margin-top: 40px; }
.feature-list li { display: flex; gap: 24px; align-items: flex-start; }
.icon-wrapper { background: #f5f5f7; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.check { color: #1d1d1f; font-weight: bold; font-size: 18px; }
.text-content strong { font-size: 20px; font-weight: 600; display: block; margin-bottom: 8px; letter-spacing: -0.5px; }
.text-content p { color: #86868b; margin: 0; line-height: 1.6; font-size: 16px; }

/* 图表卡片 */
.data-vis-card { padding: 40px; height: 450px; display: flex; flex-direction: column; justify-content: space-between; border-radius: 32px; background: #fff; border: 1px solid rgba(0,0,0,0.05); }
.graph-header { font-size: 14px; font-weight: 600; color: #86868b; display: flex; align-items: center; gap: 8px; }
.graph-header .dot { width: 8px; height: 8px; background: #0071e3; border-radius: 50%; }
.graph-bars { display: flex; align-items: flex-end; gap: 24px; height: 300px; width: 100%; justify-content: center; position: relative; }
.bar { width: 48px; background: #f5f5f7; border-radius: 12px 12px 0 0; position: relative; transition: height 1s cubic-bezier(0.16, 1, 0.3, 1); }
.bar.active { background: linear-gradient(to top, #0071e3, #4facfe); }
.glass-tooltip {
  position: absolute; top: -50px; left: 50%; transform: translateX(-50%);
  background: rgba(29, 29, 31, 0.8); backdrop-filter: blur(10px); color: #fff;
  padding: 8px 16px; border-radius: 10px; font-size: 13px; font-weight: 500; white-space: nowrap;
}

/* --- Screen 4: Process & Footer (沉浸式深色) --- */
.process-screen { background: #000; color: #f5f5f7; text-align: center; }
.process-steps { display: flex; justify-content: center; align-items: center; gap: 60px; margin-bottom: 120px; }
.step { position: relative; }
.step-num { font-size: 80px; font-weight: 800; color: rgba(255,255,255,0.05); margin-bottom: -40px; letter-spacing: -4px; }
.step h3 { font-size: 24px; font-weight: 600; position: relative; z-index: 1; letter-spacing: -0.5px; }
.step-line { width: 120px; height: 1px; background: rgba(255,255,255,0.15); }

.final-cta h2 { font-size: 56px; font-weight: 700; margin-bottom: 48px; letter-spacing: -2px; }
.primary-btn.ultra-huge { font-size: 20px; padding: 24px 64px; border-radius: 40px; background: #fff; color: #000; }
.primary-btn.ultra-huge:hover { background: #f5f5f7; transform: scale(1.05); }
.copyright { margin-top: 100px; color: #86868b; font-size: 14px; line-height: 1.8; }
</style>
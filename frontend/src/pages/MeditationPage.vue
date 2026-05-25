<template>
  <div class="page-container" :class="currentTheme">
    
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <nav class="top-nav">
      <button class="back-btn" @click="handleBack">
        <span class="arrow-icon">←</span>
        <span class="btn-text">退出冥想</span>
      </button>
    </nav>

    <div class="main-content">
      
      <Transition name="fade" mode="out-in">
        <div v-if="!isRunning" class="glass-card selection-panel" key="selection">
          <div class="panel-header">
            <h2>🧘 冥想空间</h2>
            <p>请选择适合当下的呼吸节奏</p>
          </div>

          <div class="mode-grid">
            <div 
              v-for="mode in modes" 
              :key="mode.id"
              class="mode-card"
              :class="[mode.theme, { active: selectedMode.id === mode.id }]"
              @click="selectMode(mode)"
            >
              <div class="mode-icon">{{ mode.icon }}</div>
              <div class="mode-info">
                <h3>{{ mode.name }}</h3>
                <p>{{ mode.desc }}</p>
                <span class="time-tag">⏱️ {{ Math.floor(mode.duration / 60) }} min</span>
              </div>
            </div>
          </div>

          <button 
            class="start-btn-large" 
            :class="selectedMode.theme + '-btn'"
            @click="startMeditation"
          >
            开始 {{ selectedMode.name }}
          </button>
        </div>

        <div v-else class="meditation-view" key="meditation">
          
          <div class="breathing-container">
            <div 
              class="breathing-circle"
              :style="{ animationDuration: selectedMode.rhythm }"
            >
              <div class="inner-glow"></div>
              <div class="outer-ring"></div>
            </div>
            
            <div class="guide-text">
              <h3>{{ guideMessage }}</h3>
              <p class="sub-guide">{{ selectedMode.guide }}</p>
            </div>
          </div>

          <div class="timer-display">{{ formattedTime }}</div>

          <button class="stop-btn" @click="stopMeditation">
            结束练习
          </button>
        </div>
      </Transition>

    </div>

    <Transition name="toast-fade">
      <div v-if="showToast" class="toast-message">
        <span class="toast-icon">🎉</span>
        <span>练习完成！感受一下此刻的平静。</span>
      </div>
    </Transition>

    <Transition name="modal-fade">
      <div v-if="showExitModal" class="custom-modal-overlay">
        <div class="custom-modal">
          <h3>正在冥想中</h3>
          <p>现在的状态很难得，确定要放弃本次练习吗？</p>
          <div class="modal-actions">
            <button class="modal-btn cancel" @click="showExitModal = false">继续练习</button>
            <button class="modal-btn confirm" @click="confirmExit">确定退出</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// ================= 新增状态 =================
const showToast = ref(false);     // 控制 Toast
const showExitModal = ref(false); // 控制 Modal

// ================= 1. 数据定义 =================
const modes = [
  { 
    id: 1, 
    name: '焦虑急救', 
    desc: '盒式呼吸法，快速平复心跳。', 
    icon: '📦', 
    duration: 180, // 3分钟
    rhythm: '16s', // 4吸-4停-4呼-4停
    theme: 'theme-blue',
    guide: '吸气... 屏住... 呼气... 屏住...'
  },
  { 
    id: 2, 
    name: '深度助眠', 
    desc: '4-7-8 呼吸法，激活副交感神经。', 
    icon: '🌙', 
    duration: 300, // 5分钟
    rhythm: '19s', // 4吸-7停-8呼
    theme: 'theme-purple',
    guide: '鼻吸气... 屏住... 用嘴呼气...'
  },
  { 
    id: 3, 
    name: '专注唤醒', 
    desc: '均衡呼吸，为大脑充氧。', 
    icon: '💡', 
    duration: 300, 
    rhythm: '10s', 
    theme: 'theme-orange',
    guide: '跟随圆圈律动，保持觉察'
  },
  { 
    id: 4, 
    name: '情绪释放', 
    desc: '深呼吸，排出压力与负面情绪。', 
    icon: '🍃', 
    duration: 600, // 10分钟
    rhythm: '12s',
    theme: 'theme-green',
    guide: '吸入平静... 呼出压力...'
  }
];

// ================= 2. 状态管理 =================
const selectedMode = ref(modes[0]);
const isRunning = ref(false);
const timeLeft = ref(modes[0].duration);
const guideMessage = ref('准备...');
let timer = null;

const currentTheme = computed(() => isRunning.value ? selectedMode.value.theme : 'theme-default');

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60);
  const s = timeLeft.value % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
});

// ================= 3. 方法逻辑 =================
const selectMode = (mode) => {
  selectedMode.value = mode;
  timeLeft.value = mode.duration;
};

const startMeditation = () => {
  isRunning.value = true;
  guideMessage.value = "跟随呼吸";
  
  timer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--;
    } else {
      finishMeditation();
    }
  }, 1000);
};

const stopMeditation = () => {
  clearInterval(timer);
  isRunning.value = false;
  timeLeft.value = selectedMode.value.duration;
};

// [修改] 练习完成逻辑：使用 Toast
const finishMeditation = () => {
  stopMeditation();
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

// [修改] 返回逻辑：使用 Modal
const handleBack = () => {
  if (isRunning.value) {
    showExitModal.value = true;
  } else {
    router.back();
  }
};

// [新增] 确认退出
const confirmExit = () => {
  stopMeditation();
  router.back();
};

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<style scoped>
/* ================= 全局容器与背景 ================= */
.page-container {
  min-height: 100vh;
  padding: 20px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: background 1.5s ease;
  overflow: hidden;
}


.theme-blue { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); }
.theme-purple { background: linear-gradient(135deg, #240b36 0%, #c31432 100%); }
.theme-orange { background: linear-gradient(135deg, #ff512f 0%, #dd2476 100%); }
.theme-green { background: linear-gradient(135deg, #134e5e 0%, #71b280 100%); }

.bg-orb {
  position: absolute; border-radius: 50%; filter: blur(80px); z-index: 0; opacity: 0.4;
  transition: all 1s ease;
}
.orb-1 { width: 300px; height: 300px; top: -50px; left: -50px; background: rgba(255,255,255,0.2); }
.orb-2 { width: 250px; height: 250px; bottom: -50px; right: -50px; background: rgba(255,255,255,0.2); }

/* ================= 顶部导航 ================= */
.top-nav {
  position: absolute; top: 30px; left: 30px; z-index: 100;
}

.back-btn {
  display: flex; align-items: center; gap: 8px; 
  padding: 10px 24px;
  border-radius: 50px; 
  background: rgba(255, 255, 255, 0.9); 
  backdrop-filter: blur(10px);
  border: 1px solid white;
  color: #333; 
  font-weight: 700; 
  cursor: pointer; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}
.back-btn:hover { 
  transform: scale(1.05); 
  background: #fff; 
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

/* ================= 模式选择面板 ================= */
.glass-card {
  width: 100%; max-width: 500px;
  
  backdrop-filter: blur(20px);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 30px;
  z-index: 10;
  text-align: center;
}

.panel-header h2 { margin: 0 0 10px 0; color: #2c3e50; font-size: 1.8rem; }
.panel-header p { color: #666; margin-bottom: 30px; }

.mode-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }

.mode-card {
  /* 1. 改为半透明白色背景 */
  background: rgba(255, 255, 255, 0.4); 
  
  /* 2. 加上边框让它更像玻璃片 */
  border: 1px solid rgba(255, 255, 255, 0.6);
  
  /* 3. (可选) 如果背景有东西，加上模糊才显磨砂感。
     但在极简白背景下，主要靠透明度和阴影来体现 */
  backdrop-filter: blur(10px); 
  
  padding: 20px; 
  border-radius: 16px;
  text-align: left; 
  cursor: pointer; 
  transition: all 0.2s;
}

/* 悬浮效果：变白一点，上浮 */
.mode-card:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateY(-2px); 
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

/* 选中状态：纯白不透明，加深色边框 */
.mode-card.active {
  
  border-color: #587a9c;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.mode-icon { font-size: 2rem; margin-bottom: 10px; }
.mode-info h3 { margin: 0 0 5px 0; font-size: 1rem; color: #333; font-weight: bold; }
.mode-info p { margin: 0 0 8px 0; font-size: 0.8rem; color: #666; line-height: 1.4; }
.time-tag { font-size: 0.75rem; color: #555; background: #eee; padding: 2px 6px; border-radius: 4px; font-weight: bold; }

.start-btn-large {
  width: 100%; padding: 16px; border-radius: 50px; border: none;
  color: white; font-size: 1.1rem; font-weight: bold; cursor: pointer;
  transition: 0.3s; box-shadow: 0 10px 20px rgba(0,0,0,0.15);
}
.start-btn-large:hover { transform: translateY(-2px); filter: brightness(1.1); }

.theme-blue-btn { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
.theme-purple-btn { background: linear-gradient(135deg, #4b134f 0%, #c94b4b 100%); }
.theme-orange-btn { background: linear-gradient(135deg, #ff512f 0%, #dd2476 100%); }
.theme-green-btn { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }

/* ================= 冥想进行中 ================= */
.meditation-view { 
  display: flex; flex-direction: column; align-items: center; justify-content: center; 
  width: 100%; height: 100%; z-index: 10;
}

.breathing-container { position: relative; margin: 40px 0; display: flex; flex-direction: column; align-items: center; }

.breathing-circle {
  width: 220px; height: 220px; border-radius: 50%;
  position: relative; display: flex; align-items: center; justify-content: center;
  animation: breathe-scale infinite ease-in-out; 
}

.inner-glow {
  width: 100%; height: 100%; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.1) 70%);
  box-shadow: 0 0 60px 20px rgba(255,255,255,0.3);
  position: absolute;
}

.outer-ring {
  width: 120%; height: 120%; border-radius: 50%; border: 2px solid rgba(255,255,255,0.3);
  position: absolute; opacity: 0.5;
  animation: ripple infinite ease-in-out; animation-duration: inherit;
}

.guide-text { margin-top: 50px; text-align: center; }
.guide-text h3 { 
  font-size: 2.2rem; color: white; margin: 0; 
  text-shadow: 0 4px 10px rgba(0,0,0,0.5); 
  font-weight: 800; letter-spacing: 2px;
}
.sub-guide { 
  color: rgba(255,255,255,0.9); margin-top: 10px; font-size: 1.1rem; 
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.timer-display { 
  font-size: 4.5rem; font-weight: 700; color: white; margin: 20px 0 40px; 
  font-feature-settings: "tnum"; 
  text-shadow: 0 4px 15px rgba(0,0,0,0.4); 
}

.stop-btn {
  background: rgba(255,255,255,0.15); 
  border: 1px solid rgba(255,255,255,0.5);
  color: white; padding: 12px 40px; border-radius: 50px; 
  font-size: 1.1rem; cursor: pointer; transition: 0.2s;
  backdrop-filter: blur(5px);
  font-weight: bold;
}
.stop-btn:hover { background: rgba(255,255,255,0.3); transform: scale(1.05); }

@keyframes breathe-scale {
  0%, 100% { transform: scale(0.8); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
}
@keyframes ripple {
  0%, 100% { transform: scale(1); opacity: 0.1; }
  50% { transform: scale(1.1); opacity: 0.4; }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }



/* ==================== [新增] Modal 样式 ==================== */
.custom-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); /* 深色遮罩 */
  backdrop-filter: blur(8px);
  z-index: 3000;
  display: flex; align-items: center; justify-content: center;
}

.custom-modal {
  background: white; padding: 30px; width: 85%; max-width: 320px;
  border-radius: 24px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  text-align: center; animation: modal-pop 0.3s ease-out;
}

.custom-modal h3 { margin: 0 0 10px 0; color: #2c3e50; font-size: 1.2rem; }
.custom-modal p { color: #666; font-size: 0.9rem; margin-bottom: 25px; line-height: 1.5; }

.modal-actions { display: flex; gap: 15px; justify-content: center; }

.modal-btn {
  padding: 10px 20px; border-radius: 50px; font-size: 0.9rem;
  cursor: pointer; border: none; font-weight: 600; transition: all 0.2s;
}

.modal-btn.cancel { background: #f4f6f9; color: #666; }
.modal-btn.cancel:hover { background: #e0e2e5; }

.modal-btn.confirm {
  background: #ff6b6b; color: white;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}
.modal-btn.confirm:hover { transform: translateY(-2px); }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

@keyframes modal-pop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
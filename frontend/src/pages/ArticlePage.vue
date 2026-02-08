<template>
  <div class="page-container">
    
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <nav class="top-nav">
      <button class="back-btn glass-effect" @click="$router.back()">
        <span class="arrow-icon">←</span>
        <span class="btn-text">返回首页</span>
      </button>
    </nav>

    <div class="hub-header">
      <h1>📚 心理百科知识库</h1>
      <p class="subtitle">已收录 {{ articles.length }} 条心理学实证建议</p>
      
      <div class="search-box">
        <span class="icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="试试搜索：失眠、拖延、社恐..."
        >
      </div>

      <div class="tabs-row">
        <button 
          v-for="tab in tabs" 
          :key="tab"
          class="tab-btn" 
          :class="{ active: currentTab === tab }"
          @click="currentTab = tab"
        >
          {{ tab }}
        </button>
      </div>
    </div>

    <div class="cards-grid">
      <div 
        v-for="item in filteredArticles" 
        :key="item.id"
        class="glass-card list-card"
        @click="openArticle(item)"
      >
        <div class="card-icon" :class="item.theme">{{ item.icon }}</div>
        <div class="card-content">
          <h3>{{ item.title }}</h3>
          <p>{{ item.subtitle }}</p>
          <div class="card-meta">
            <span class="tag">#{{ item.category }}</span>
            <span class="read-time">📖 3min</span>
          </div>
        </div>
      </div>
    </div>

    <Transition name="modal">
      <div v-if="selectedArticle" class="modal-overlay" @click.self="closeArticle">
        <div class="modal-window">
          <button class="close-btn" @click="closeArticle">×</button>
          
          <div class="article-content">
            <header class="article-header" :class="selectedArticle.theme">
              <span class="big-icon">{{ selectedArticle.icon }}</span>
              <h2>{{ selectedArticle.title }}</h2>
              <p>{{ selectedArticle.subtitle }}</p>
            </header>

            <div class="article-body">
              <p v-for="(p, i) in selectedArticle.paragraphs" :key="i">{{ p }}</p>
              <div class="highlight-box">
                <h4>✨ 心理锦囊：试着这样做</h4>
                <ul>
                  <li v-for="(tip, j) in selectedArticle.tips" :key="j">{{ tip }}</li>
                </ul>
              </div>
            </div>

            <footer class="article-footer">
              <button class="ai-btn" @click="chatWithAI">
                🤖 和 AI 聊聊“{{ selectedArticle.keyword }}”
              </button>
            </footer>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 状态管理
const searchQuery = ref('');
const currentTab = ref('全部');
const selectedArticle = ref(null);

const tabs = ['全部', '情绪急救', '自我成长', '人际关系', '职场效率'];

// 文章数据 (这里省略了具体内容，保持你之前的 articles 数据即可)
const articles = [
  {
    id: 1,
    title: "失眠急救指南",
    subtitle: "美军睡眠法：2分钟快速入睡",
    icon: "😴",
    theme: "blue",
    category: "情绪急救",
    keyword: "失眠",
    paragraphs: [
      "躺在床上翻来覆去睡不着？越是强迫自己睡，大脑反而越清醒。这通常是因为交感神经还处于兴奋状态。",
      "美军睡眠法的核心是彻底放松面部肌肉，尤其是舌头、下巴和眼周肌肉。"
    ],
    tips: [
      "放松面部：想象你的脸像融化的黄油。",
      "肩膀下沉：让双手自然落在身体两侧。",
      "清空大脑：默念“不许想”十秒钟。"
    ]
  },
  {
    id: 2,
    title: "停止精神内耗",
    subtitle: "为什么你总是感到很累？",
    icon: "🔋",
    theme: "green",
    category: "情绪急救",
    keyword: "内耗",
    paragraphs: [
      "精神内耗就像手机后台开了太多耗电APP。你没有在做具体的工作，但大脑一直在纠结“如果...怎么办”。",
      "反刍思维（Rumination）会迅速耗干你的心理能量。"
    ],
    tips: [
      "课题分离：分清“我的事”和“别人的事”。",
      "行动优先：焦虑是想出来的，行动是解药。",
      "书写疗法：把担心的事写在纸上归档。"
    ]
  },
  {
    id: 3,
    title: "战胜拖延症",
    subtitle: "不是因为懒，而是因为恐惧",
    icon: "🍅",
    theme: "red",
    category: "职场效率",
    keyword: "拖延",
    paragraphs: [
      "很多时候我们拖延，是因为任务看起来太庞大、太痛苦。大脑为了保护我们免受痛苦，选择了逃避。",
      "“微量开始”是欺骗大脑最好的方式。"
    ],
    tips: [
      "5分钟原则：告诉自己只做5分钟，如果你想停下来就可以停。",
      "拆解任务：把“写论文”拆解为“打开文档”和“写标题”。"
    ]
  },
  {
    id: 4,
    title: "冒名顶替综合征",
    subtitle: "总觉得自己“不配”？",
    icon: "🎭",
    theme: "purple",
    category: "自我成长",
    keyword: "自卑",
    paragraphs: [
      "你是否觉得自己的成功全是运气，随时会被人揭穿？这叫冒名顶替综合征（Imposter Syndrome）。",
      "即使是爱因斯坦也曾觉得自己是欺世盗名的骗子。"
    ],
    tips: [
      "建立成就库：把你的哪怕微小的成功记录下来。",
      "重新归因：把“运气好”改为“我做对了什么”。"
    ]
  },
  {
    id: 5,
    title: "应对社交恐惧",
    subtitle: "打破聚光灯效应的幻觉",
    icon: "🙈",
    theme: "orange",
    category: "人际关系",
    keyword: "社恐",
    paragraphs: [
      "你走进教室时觉得所有人都在盯着你？心理学上这叫“聚光灯效应”。",
      "其实大家都很忙，都在担心自己表现得好不好，根本没人有空盯着你。"
    ],
    tips: [
      "注意力外移：观察周围环境的颜色，而不是关注心跳。",
      "允许尴尬：告诉自己“脸红了也很可爱”。"
    ]
  },
  {
    id: 6,
    title: "愤怒管理",
    subtitle: "给情绪按下暂停键",
    icon: "🔥",
    theme: "red",
    category: "情绪急救",
    keyword: "愤怒",
    paragraphs: [
      "愤怒往往是次生情绪，它的背后通常是受伤、无助或被忽视。",
      "当下的爆发往往不能解决问题，只会制造新的问题。"
    ],
    tips: [
      "6秒法则：愤怒的生理冲动只持续6秒，数6个数再说话。",
      "离开现场：物理上的距离能带来心理上的冷静。"
    ]
  },
  {
    id: 7,
    title: "非暴力沟通",
    subtitle: "如何好好说话？",
    icon: "🕊️",
    theme: "blue",
    category: "人际关系",
    keyword: "沟通",
    paragraphs: [
      "大多数争吵是因为我们把“评论”当成了“事实”。",
      "非暴力沟通的核心是表达需求，而不是指责对方。"
    ],
    tips: [
      "讲事实：说“你迟到了30分钟”，而不是“你总是迟到”。",
      "讲感受：说“我感到很担心”，而不是“你让我很生气”。"
    ]
  },
  {
    id: 8,
    title: "告别完美主义",
    subtitle: "完成比完美更重要",
    icon: "🏁",
    theme: "green",
    category: "自我成长",
    keyword: "完美主义",
    paragraphs: [
      "完美主义不是追求卓越，而是对失败的恐惧。它会让你迟迟不敢开始。",
      "世界上没有完美的方案，只有迭代出来的方案。"
    ],
    tips: [
      "设定B-标准：允许自己这次只拿80分。",
      "庆祝失败：失败意味着你在尝试新的东西。"
    ]
  }
];

// 逻辑处理
const filteredArticles = computed(() => {
  return articles.filter(item => {
    const matchTab = currentTab.value === '全部' || item.category === currentTab.value;
    const matchSearch = item.title.includes(searchQuery.value) || 
                        item.keyword.includes(searchQuery.value);
    return matchTab && matchSearch;
  });
});

const openArticle = (item) => { selectedArticle.value = item; };
const closeArticle = () => { selectedArticle.value = null; };

const chatWithAI = () => {
  if (selectedArticle.value) {
    router.push({ 
      path: '/chat', 
      query: { initialPrompt: `我想和你聊聊关于“${selectedArticle.value.keyword}”的话题...` } 
    });
  }
};
</script>

<style scoped>
.page-container {
  padding: 30px 40px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  position: relative;
}

/* 装饰背景 */
.bg-orb { position: absolute; border-radius: 50%; filter: blur(80px); z-index: -1; }
.orb-1 { width: 300px; height: 300px; background: rgba(161, 140, 209, 0.2); top: -50px; left: -50px; }
.orb-2 { width: 250px; height: 250px; background: rgba(142, 197, 252, 0.2); bottom: 100px; right: -50px; }

/* ==================== [新增样式] 返回按钮 ==================== */
.top-nav {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start; /* 靠左对齐 */
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 50px; /* 胶囊圆角 */
  border: 1px solid rgba(255, 255, 255, 0.6); /* 细边框 */
  background: rgba(255, 255, 255, 0.6); /* 半透明白 */
  backdrop-filter: blur(12px); /* 磨砂玻璃效果 */
  color: #555;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.back-btn:hover {
  background: white; /* 悬浮变纯白 */
  transform: translateX(-5px); /* 向左微动，暗示返回 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  color: #2c3e50;
}

.arrow-icon {
  font-size: 1.2rem;
  line-height: 1;
}

/* ==================== 其他原有样式 (保持不变) ==================== */
.hub-header { text-align: center; margin-bottom: 50px; }
.hub-header h1 { font-size: 2.2rem; color: #2c3e50; margin-bottom: 10px; }
.subtitle { color: #666; margin-bottom: 30px; }

.search-box {
  background: white; width: 100%; max-width: 400px; margin: 0 auto 30px;
  display: flex; align-items: center; padding: 12px 20px;
  border-radius: 50px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.search-box input { border: none; outline: none; flex: 1; font-size: 1rem; margin-left: 10px; }

.tabs-row { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }
.tab-btn {
  background: rgba(255,255,255,0.6); border: 1px solid rgba(0,0,0,0.05);
  padding: 8px 20px; border-radius: 20px; cursor: pointer; color: #666;
  transition: all 0.3s;
}
.tab-btn.active { background: #667eea; color: white; transform: scale(1.05); }

/* 卡片列表 */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.glass-card {
  background: rgba(255,255,255,0.7); backdrop-filter: blur(10px);
  border-radius: 20px; padding: 25px; cursor: pointer;
  transition: all 0.3s; border: 1px solid rgba(255,255,255,0.5);
  display: flex; flex-direction: column; gap: 15px;
}
.glass-card:hover { transform: translateY(-5px); background: white; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }

.card-icon { 
  font-size: 2rem; width: 50px; height: 50px; 
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px; background: rgba(0,0,0,0.03);
}
.card-icon.blue { color: #4facfe; background: rgba(79, 172, 254, 0.1); }
.card-icon.green { color: #43e97b; background: rgba(67, 233, 123, 0.1); }
.card-icon.red { color: #ff6b6b; background: rgba(255, 107, 107, 0.1); }
.card-icon.purple { color: #a18cd1; background: rgba(161, 140, 209, 0.1); }
.card-icon.orange { color: #fa709a; background: rgba(250, 112, 154, 0.1); }

.card-content h3 { margin: 0 0 5px 0; font-size: 1.1rem; color: #333; }
.card-content p { margin: 0 0 15px 0; font-size: 0.9rem; color: #888; }
.card-meta { display: flex; justify-content: space-between; font-size: 0.8rem; color: #aaa; }
.tag { color: #667eea; background: #eef2ff; padding: 2px 8px; border-radius: 4px; }

/* 弹窗样式 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(5px);
  z-index: 1000; display: flex; align-items: center; justify-content: center;
}
.modal-window {
  width: 90%; max-width: 600px; background: white; border-radius: 24px;
  position: relative; overflow: hidden; max-height: 85vh; display: flex; flex-direction: column;
}
.close-btn {
  position: absolute; top: 15px; right: 15px; width: 32px; height: 32px;
  background: rgba(0,0,0,0.05); border: none; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; z-index: 10;
}
.article-content { overflow-y: auto; padding-bottom: 30px; }

.article-header { padding: 40px 30px 20px; text-align: center; color: white; }
.article-header.blue { background: linear-gradient(135deg, #a1c4fd, #c2e9fb); }
.article-header.green { background: linear-gradient(135deg, #84fab0, #8fd3f4); }
.article-header.red { background: linear-gradient(135deg, #ff9a9e, #fecfef); }
.article-header.purple { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }
.article-header.orange { background: linear-gradient(135deg, #fccb90, #d57eeb); }

.big-icon { font-size: 3.5rem; display: block; margin-bottom: 10px; }

.article-body { padding: 30px; font-size: 1.05rem; line-height: 1.8; color: #444; }
.highlight-box {
  background: #f9f9f9; padding: 20px; border-radius: 12px;
  margin-top: 25px; border-left: 4px solid #ddd;
}
.highlight-box h4 { margin: 0 0 10px 0; color: #667eea; }

.ai-btn {
  display: block; width: 80%; margin: 0 auto; padding: 12px;
  background: #2c3e50; color: white; border: none; border-radius: 50px;
  font-weight: bold; cursor: pointer; transition: transform 0.2s;
}
.ai-btn:hover { transform: scale(1.03); background: #34495e; }

/* 动画 */
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
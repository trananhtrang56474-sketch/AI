<template>
  <div class="home-dashboard">
    <div class="welcome-banner card">
      <div class="banner-content">
        <h4><span role="img" aria-label="wave">👋</span> 你好，很高兴见到你</h4>
        <p>这里是你的心灵栖息地。无论是倾诉烦恼，还是记录当下的心情，我都随时在这里陪伴你。</p>
        <button class="primary-btn" @click="startNewChat">
          立即开始对话
        </button>
      </div>
      <div class="banner-decoration">🌱</div>
    </div>

    <div class="main-content-grid">
      
      <div class="left-column">
        
        <div class="card emotion-tracker">
          <div class="card-header">
            <h4><span role="img" aria-label="chart">📈</span> 心灵晴雨表 (Emotion Tracking)</h4>
            <span class="sub-text">最近 7 次对话趋势</span>
          </div>
          
          <div class="chart-container">
            <EmotionChart :chart-data="emotionData" />
          </div>
        </div>
        
        <div class="card knowledge-hub">
          <div class="card-header">
            <h4><span role="img" aria-label="books">📚</span> 心理知识库 (Knowledge Base)</h4>
          </div>
          <p class="card-desc">我们的建议基于专业的心理学理论，为你提供科学的支持。</p>
          
          <div class="topic-list">
            <span class="topic-tag">🧘‍♀️ 缓解焦虑</span>
            <span class="topic-tag">🌬️ 正念呼吸</span>
            <span class="topic-tag">🧠 认知重构</span>
            <span class="topic-tag">🤝 人际关系</span>
            <span class="topic-tag">💤 睡眠改善</span>
            <span class="topic-tag more-tag">探索更多 &rarr;</span>
          </div>
        </div>
      </div>
      
      <div class="right-column">
        
        <div class="card quick-action primary-action" @click="startNewChat">
          <div class="icon-wrapper">💬</div>
          <div class="action-text">
            <h5>开始新对话</h5>
            <p>此时此刻，想聊点什么？</p>
          </div>
        </div>
        
        <div class="card quick-action guided-session">
          <div class="icon-wrapper">🧘</div>
          <div class="action-text">
            <h5>引导式练习</h5>
            <p>5分钟正念冥想，放松身心。</p>
          </div>
        </div>
        
        <div class="card quick-action journal">
          <div class="icon-wrapper">✍️</div>
          <div class="action-text">
            <h5>情绪日志</h5>
            <p>快速记录此刻的心情标签。</p>
          </div>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// 确保路径正确
import EmotionChart from '@/components/EmotionChart.vue'; 

const router = useRouter();

// --- 数据状态 ---
const emotionData = ref({
  labels: [],
  datasets: []
});

// --- 模拟从 API 获取数据 ---
const fetchDashboardData = async () => {
  // 模拟网络延迟
  // await new Promise(r => setTimeout(r, 500));
  
  // 这里将来替换为 axios.get('/api/emotions')
  emotionData.value = {
    labels: ['10-12', '10-13', '10-14', '10-15', '10-16', '10-17', '10-18'],
    datasets: [
      {
        label: '情绪指数',
        data: [3, 5, 4, 6, 4, 2, 3], 
        borderColor: '#1890ff',
        backgroundColor: 'rgba(24, 144, 255, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4, // 让曲线更平滑
        pointBackgroundColor: '#fff',
        pointBorderColor: '#1890ff',
        pointRadius: 4
      }
    ]
  };
};

// 组件加载时获取数据
onMounted(() => {
  fetchDashboardData();
});

const startNewChat = () => {
  router.push('/chat');
};
</script>

<style scoped>
/* 全局容器 */
.home-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1200px; /* 限制最大宽度，在大屏上更好看 */
  margin: 0 auto;
  width: 100%;
}

/* 通用卡片样式 - 增加柔和阴影 */
.card {
  background: #fff;
  padding: 24px;
  border-radius: 16px; /* 更圆润的角 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); /* 非常淡的阴影 */
  border: 1px solid rgba(0,0,0,0.02);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* 卡片头部通用样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.card h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
}
.sub-text {
  font-size: 12px;
  color: #999;
}

/* Banner 样式优化 */
.welcome-banner {
  background: linear-gradient(120deg, #e6f7ff 0%, #f0fff4 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.banner-content {
  z-index: 2;
}
.banner-content h4 {
  font-size: 22px;
  color: #2c3e50;
  margin-bottom: 8px;
}
.banner-content p {
  color: #555;
  margin-bottom: 16px;
  max-width: 600px;
}
.banner-decoration {
  font-size: 80px;
  opacity: 0.2;
  position: absolute;
  right: 20px;
  bottom: -10px;
  user-select: none;
  pointer-events: none;
}

/* 按钮样式优化 */
.primary-btn {
  background: #1890ff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 4px 10px rgba(24, 144, 255, 0.3);
  transition: all 0.2s;
}
.primary-btn:hover {
  background: #40a9ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(24, 144, 255, 0.4);
}
.primary-btn:active {
  transform: translateY(0);
}

/* 布局网格 */
.main-content-grid {
  display: flex;
  gap: 24px;
}
.left-column {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.right-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 图表容器 */
.chart-container {
  height: 280px;
  width: 100%;
  position: relative;
}

/* 知识库标签 */
.topic-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.topic-tag {
  background: #f5f7fa;
  color: #555;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.topic-tag:hover {
  background: #e6f7ff;
  color: #1890ff;
  border-color: #bae7ff;
}
.more-tag {
  background: transparent;
  color: #1890ff;
  font-weight: 500;
}

/* 快捷入口卡片优化 */
.quick-action {
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  border: 1px solid transparent;
}
.quick-action:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border-color: #e6f7ff;
}
.icon-wrapper {
  font-size: 24px;
  background: #f5f5f5;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.action-text h5 {
  font-size: 16px;
  color: #333;
  margin: 0 0 4px 0;
  font-weight: 600;
}
.action-text p {
  font-size: 13px;
  color: #888;
  margin: 0;
  line-height: 1.4;
}

/* 特殊颜色修饰 */
.primary-action .icon-wrapper {
  background: #e6f7ff;
}
.guided-session .icon-wrapper {
  background: #f6ffed;
}
.journal .icon-wrapper {
  background: #fffbe6;
}

/* 📱 移动端适配 (重点优化) */
@media (max-width: 768px) {
  .main-content-grid {
    flex-direction: column; /* 手机上改为单列 */
  }
  
  .left-column, .right-column {
    flex: auto; /* 宽度自动填满 */
    width: 100%;
  }

  .banner-decoration {
    display: none; /* 手机上隐藏背景装饰，防止遮挡 */
  }
}
</style>
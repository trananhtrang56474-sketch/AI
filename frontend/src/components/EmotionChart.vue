<template>
  <div class="chart-wrapper">
    <Line
      v-if="chartData && chartData.datasets && chartData.datasets.length > 0"
      :data="chartData"
      :options="chartOptions"
    />
    
    <div v-else class="empty-chart">
      <span>📊</span>
      <p>暂无情绪数据，快去和 AI 聊聊吧</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler // 用于填充曲线下方的颜色
} from 'chart.js';
import { Line } from 'vue-chartjs';

// 注册 Chart.js 必须的组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], datasets: [] })
  }
});

// --- 图表配置选项 (美化) ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false, // 允许图表填满父容器的高度
  plugins: {
    legend: {
      display: false // 隐藏图例 (因为我们在 Home 页面卡片标题里已经写了)
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      titleColor: '#333',
      bodyColor: '#666',
      borderColor: '#eee',
      borderWidth: 1,
      padding: 10,
      displayColors: false, // 不显示 tooltip 里的小色块
      callbacks: {
        label: function(context) {
          return `情绪指数: ${context.parsed.y}`;
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false, // 隐藏 X 轴网格线，看起来更干净
        drawBorder: false
      },
      ticks: {
        color: '#999',
        font: { size: 12 }
      }
    },
    y: {
      grid: {
        color: '#f0f0f0', // Y 轴网格线改淡一点
        borderDash: [5, 5] // 虚线效果
      },
      ticks: {
        display: false, // 隐藏 Y 轴数值，只看趋势更直观
      },
      border: {
        display: false // 隐藏 Y 轴左边的轴线
      },
      min: 0, // 假设情绪分最低 0
      max: 10 // 假设情绪分最高 10
    }
  },
  elements: {
    line: {
      tension: 0.4 // 0.4 让线条变成平滑的贝塞尔曲线，而不是折线
    },
    point: {
      radius: 4,
      hoverRadius: 6,
      backgroundColor: '#fff',
      borderWidth: 2
    }
  },
  interaction: {
    intersect: false,
    mode: 'index',
  },
};
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%; /* 填满父容器 */
  position: relative;
}

.empty-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f9fafb;
  border-radius: 12px;
  color: #9ca3af;
}

.empty-chart span {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.empty-chart p {
  font-size: 14px;
  margin: 0;
}
</style>
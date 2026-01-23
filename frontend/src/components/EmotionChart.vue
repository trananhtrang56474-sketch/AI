<template>
  <div class="chart-container">
    <v-chart 
      v-if="chartData && chartData.scores && chartData.scores.length > 0" 
      class="chart" 
      :option="option" 
      autoresize 
    />
    
    <div v-else class="empty-chart">
      <div class="empty-icon">📊</div>
      <p>暂无情绪数据</p>
      <span>与 AI 多聊几句，生成你的心理画像</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import {
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  MarkLineComponent
} from 'echarts/components';
import VChart from 'vue-echarts';

// 注册 ECharts 必需组件
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  MarkLineComponent
]);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ dates: [], scores: [] })
  }
});

// 计算 ECharts 配置项
const option = computed(() => {
  return {
    backgroundColor: 'transparent', 
    
    // ✨✨✨ 核心修复：防止被截断 ✨✨✨
    grid: {
      top: '15%',
      bottom: '10%', // 留出空间
      left: '5%',
      right: '5%',
      containLabel: true // 🔥 关键：自动计算空间，保证坐标轴文字不被切掉
    },

    // 悬停提示框
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#eee',
      borderWidth: 1,
      textStyle: { color: '#333' },
      formatter: function (params) {
        const score = params[0].value;
        let status = '';
        if (score >= 70) status = '🌞 积极';
        else if (score >= 40) status = '🍃 平静';
        else status = '🌧️ 负面';
        
        return `
          <div style="font-size:12px; color:#999; margin-bottom:4px;">${params[0].name}</div>
          <div style="font-weight:bold; font-size:14px;">${status}</div>
          <div style="font-size:12px;">心理指数: <span style="font-weight:bold;">${score}</span></div>
        `;
      }
    },

    // X轴 (时间)
    xAxis: {
      type: 'category',
      data: props.chartData.dates,
      boundaryGap: false,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { 
        color: '#9ca3af', 
        fontSize: 11,
        interval: 'auto' // 自动隐藏过密的标签
      }
    },

    // Y轴 (分数)
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      splitNumber: 3,
      axisLabel: { color: '#9ca3af', fontSize: 11 },
      splitLine: {
        lineStyle: { type: 'dashed', color: '#f3f4f6' }
      }
    },

    // 视觉映射 (让线条变色)
    visualMap: {
      show: false,
      dimension: 1, 
      pieces: [
        { gt: 0, lte: 40, color: '#ff6b6b' },   // 红
        { gt: 40, lte: 70, color: '#4ecdc4' },  // 青
        { gt: 70, lte: 100, color: '#feca57' }  // 黄
      ],
      outOfRange: { color: '#ccc' }
    },

    // 数据系列
    series: [
      {
        data: props.chartData.scores,
        type: 'line',
        smooth: 0.4, 
        symbol: 'circle',
        symbolSize: 6, // 稍微调小一点，显得更精致
        itemStyle: {
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          width: 3,
          shadowColor: 'rgba(0,0,0,0.1)',
          shadowBlur: 10,
          shadowOffsetY: 5
        },
        areaStyle: {
          opacity: 0.15
        },
        markLine: {
          symbol: 'none',
          silent: true,
          data: [
            { yAxis: 40, lineStyle: { color: '#ff6b6b', type: 'dotted', opacity: 0.4 } },
            { yAxis: 70, lineStyle: { color: '#feca57', type: 'dotted', opacity: 0.4 } }
          ],
          label: { show: false }
        }
      }
    ]
  };
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
  background: #fff;
  border-radius: 12px; 
  /* 这里的 padding 可以去掉，由 ECharts grid 控制，防止双重边距 */
  box-sizing: border-box;
}

.chart {
  width: 100%;
  height: 100%;
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
  border: 1px dashed #e5e7eb;
  color: #9ca3af;
}

.empty-icon { font-size: 32px; margin-bottom: 8px; opacity: 0.5; }
.empty-chart p { font-size: 14px; margin: 0 0 4px 0; font-weight: 600; color: #4b5563; }
.empty-chart span { font-size: 12px; color: #9ca3af; }
</style>
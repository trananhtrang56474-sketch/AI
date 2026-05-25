<template>
  <div class="report-container">
    <div class="report-header">
      <div class="header-titles">
        <h2 class="gradient-text"> 深度心理洞察报告</h2>
        <p>基于多模态语义分析与 Russell 情感环形模型</p>
      </div>
      <button class="export-btn" @click="downloadPDF" :disabled="isExporting">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        {{ isExporting ? '正在云端渲染...' : '导出 PDF' }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>正在为您演算多维度心理画像...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="action-btn" @click="$router.push('/chat')">去聊几句</button>
    </div>

    <div v-else id="report-export-area" class="export-wrapper">
      
      <div v-if="analytics.risk_level === 'HIGH'" class="risk-banner fade-in">
        <div class="banner-icon">⚠️</div>
        <div class="banner-text">
          <strong>情绪高风险预警：</strong> 系统检测到您近期情绪能量极低或存在剧烈波动。请允许自己暂时停下来休息，若持续感到痛苦，建议寻求专业心理咨询支持。
        </div>
      </div>

      <div class="report-grid">
        
        <div class="card summary-card fade-in" style="animation-delay: 0.1s;">
          <div class="summary-header">
            <div class="header-left">
              <h3>💡 AI 导师诊断陈述</h3>
              <span class="persona-tag" v-if="analytics.persona">👤 画像解析：{{ analytics.persona }}</span>
            </div>
            <div class="health-score-badge" :class="analytics.risk_level?.toLowerCase() || 'low'">
              <span class="score-label">心理健康指数</span>
              <span class="score-value">{{ analytics.health_index || 60 }}</span>
            </div>
          </div>
          
          <div class="summary-content">
            <div class="status-box">
              <strong>当前心境：</strong> {{ aiSummary.status_summary }}
            </div>
            <div class="advice-grid">
              <div class="issues">
                <h4>⚠️ 潜在情绪触发点</h4>
                <ul>
                  <li v-for="(issue, idx) in aiSummary.core_issues" :key="idx">{{ issue }}</li>
                </ul>
              </div>
              <div class="actions">
                <h4>🌱 认知行为(CBT)干预建议</h4>
                <ul>
                  <li v-for="(advice, idx) in aiSummary.action_advices" :key="idx">{{ advice }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="card risk-quotes-card fade-in" style="animation-delay: 0.2s;" v-if="analytics.high_risk_quotes && analytics.high_risk_quotes.length > 0">
          <h3>🚨 核心痛点与风险原话回溯</h3>
          <div class="quote-list">
            <div class="quote-item" v-for="(quote, idx) in analytics.high_risk_quotes" :key="idx">
              <span class="quote-time">{{ quote.time }}</span>
              <p class="quote-text">"{{ quote.text }}"</p>
            </div>
          </div>
        </div>

        <div class="card chart-card fade-in" style="animation-delay: 0.3s;">
          <div class="card-header-flex">
            <h3>📉 近期心境波动轨迹</h3>
            <button class="academic-download-btn" @click="downloadAcademicChart" :disabled="isDownloadingChart">
              <svg v-if="!isDownloadingChart" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              <span v-else class="mini-spinner"></span>
              {{ isDownloadingChart ? '渲染中...' : '下载轨迹(PNG)' }}
            </button>
          </div>
          <p class="sub-info">
            波动率指数：<strong>{{ analytics.volatility }}</strong> | 
            干预环比(较前半周期)：
            <span :class="analytics.progress_delta >= 0 ? 'good' : 'warning'" class="delta-badge">
              {{ analytics.progress_delta >= 0 ? '↑' : '↓' }} {{ Math.abs(analytics.progress_delta || 0) }} 分
            </span>
          </p>
          <v-chart class="chart" :option="trendOption" autoresize />
        </div>

        <div class="card chart-card fade-in" style="animation-delay: 0.4s;">
          <h3>🧭 心理能量空间 (Russell模型)</h3>
          <p class="sub-info">核心质心：V(效价) <strong>{{ analytics.avg_v }}</strong> | A(唤醒) <strong>{{ analytics.avg_a }}</strong></p>
          <v-chart class="chart" :option="scatterOption" autoresize />
        </div>

        <div class="card pie-card fade-in" style="animation-delay: 0.5s;">
          <h3>📊 情绪内稳态结构</h3>
          <v-chart class="chart" :option="pieOption" autoresize />
        </div>

        <div class="card cloud-card fade-in" style="animation-delay: 0.6s;">
          <h3>☁️ 潜意识高频主题</h3>
          <div class="word-cloud">
            <span v-for="(word, idx) in analytics.keywords" :key="idx" 
                  :style="getWordStyle(word.value, idx)" class="cloud-word">
              {{ word.name }}
            </span>
            <div v-if="!analytics.keywords || analytics.keywords.length === 0" class="empty-cloud">
              暂无足够词汇，多和 AI 聊聊吧
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, PieChart, ScatterChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, MarkAreaComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, PieChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, MarkAreaComponent]);

const router = useRouter();

const isLoading = ref(true);
const error = ref('');
const isExporting = ref(false); 
const isDownloadingChart = ref(false);

const dates = ref([]);
const scores = ref([]);
const analytics = ref({});
const aiSummary = ref({});

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080';

const fetchReportData = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    router.push('/login');
    return;
  }
  try {
    isLoading.value = true;
    error.value = '';
    const res = await axios.get(`${API_BASE}/api/report?user_id=${userId}`);
    dates.value = res.data.dates || [];
    scores.value = res.data.scores || [];
    analytics.value = res.data.analytics || {};
    aiSummary.value = res.data.summary || {};
  } catch (err) {
    console.error("获取报告失败:", err);
    error.value = err.response?.data?.error || '无法生成报告，可能需要积累更多对话数据。';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchReportData();
});

const downloadAcademicChart = async () => {
  const userId = localStorage.getItem('user_id');
  if (!userId) return;
  isDownloadingChart.value = true;
  try {
    const res = await axios.get(`${API_BASE}/api/export-trajectory?user_id=${userId}`);
    const link = document.createElement('a');
    link.href = res.data.url;
    link.download = `Academic_Trajectory_${new Date().getTime()}.png`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert(err.response?.data?.error || "生成高清轨迹图失败");
  } finally {
    isDownloadingChart.value = false;
  }
};

const getWordStyle = (value, index) => {
  const sizes = [30, 26, 22, 18, 16, 14, 14, 12, 12];
  const opacity = Math.max(0.6, 1 - index * 0.05);
  const colors = ['#1890FF', '#2F54EB', '#13C2C2', '#722ED1', '#096DD9', '#597EF7'];
  return { fontSize: `${sizes[index] || 12}px`, opacity: opacity, color: colors[index % colors.length], margin: `${Math.random() * 10 + 6}px`, lineHeight: 1.2 };
};

// 依然调用后端 PDF 引擎
const downloadPDF = async () => {
  isExporting.value = true;
  const userId = localStorage.getItem('user_id');

  try {
    const res = await axios.get(`${API_BASE}/api/export-pdf-pro?user_id=${userId}`, {
      responseType: 'blob' 
    });

    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `AI心理洞察报告_${new Date().toLocaleDateString()}.pdf`;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('PDF 下载失败:', error);
    alert('报告生成失败，请稍后重试');
  } finally {
    isExporting.value = false;
  }
};

// --- ECharts 配置 ---
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' }, extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;' },
  grid: { top: 20, right: 20, bottom: 20, left: 30, containLabel: true },
  xAxis: { type: 'category', data: dates.value, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#64748b' } },
  yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }, axisLabel: { color: '#64748b' } },
  series: [{ data: scores.value, type: 'line', smooth: 0.4, symbol: 'circle', symbolSize: 8, itemStyle: { color: '#1890FF', borderWidth: 3, borderColor: '#fff' }, lineStyle: { width: 3, shadowColor: 'rgba(24, 144, 255, 0.3)', shadowBlur: 12, shadowOffsetY: 6 }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(24, 144, 255, 0.2)' }, { offset: 1, color: 'rgba(24, 144, 255, 0)' }] } } }]
}));

const scatterOption = computed(() => {
  const vList = analytics.value.raw_valences || [];
  const aList = analytics.value.raw_arousals || [];
  const scatterData = vList.map((v, i) => [v, aList[i]]);
  return {
    tooltip: { formatter: '效价(V): {c[0]}<br/>唤醒(A): {c[1]}', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' }, extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;' },
    grid: { top: 10, right: 10, bottom: 20, left: 20, containLabel: true },
    xAxis: { type: 'value', min: 1, max: 10, show: false }, yAxis: { type: 'value', min: 1, max: 10, show: false },
    series: [{ type: 'scatter', symbolSize: 14, itemStyle: { color: 'rgba(24, 144, 255, 0.7)', shadowBlur: 8, shadowColor: 'rgba(24, 144, 255, 0.3)', shadowOffsetY: 4 }, data: scatterData, markArea: { silent: true, itemStyle: { opacity: 0.03 }, label: { position: 'inside', color: '#94a3b8', fontSize: 13, fontWeight: 'bold' }, data: [ [{ xAxis: 5.5, yAxis: 5.5, name: '激越 (右上)' }, { xAxis: 10, yAxis: 10 }], [{ xAxis: 1, yAxis: 5.5, name: '应激 (左上)', itemStyle:{color:'#FF4D4F'} }, { xAxis: 5.5, yAxis: 10 }], [{ xAxis: 1, yAxis: 1, name: '抑郁 (左下)', itemStyle:{color:'#2F54EB'} }, { xAxis: 5.5, yAxis: 5.5 }], [{ xAxis: 5.5, yAxis: 1, name: '放松 (右下)' }, { xAxis: 10, yAxis: 5.5 }] ] } }]
  };
});

const pieOption = computed(() => {
  const dist = analytics.value.distribution || { positive: 0, neutral: 0, negative: 0 };
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c}次', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' }, extraCssText: 'box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px;' },
    legend: { bottom: 0, left: 'center', icon: 'circle', textStyle: { color: '#64748b' } },
    series: [{ type: 'pie', radius: ['50%', '75%'], center: ['50%', '45%'], avoidLabelOverlap: false, itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 3 }, label: { show: false }, data: [ { value: dist.positive, name: '积极/高能', itemStyle: { color: '#1890FF' } }, { value: dist.neutral, name: '平静/中性', itemStyle: { color: '#cbd5e1' } }, { value: dist.negative, name: '消极/内耗', itemStyle: { color: '#FF4D4F' } } ] }]
  };
});
</script>

<style scoped>
/* 🌟 高端流体渐变背景 */
.report-container {
  padding: 40px;
  min-height: 100vh;

  color: #1e293b;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.report-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.header-titles h2 { 
  margin: 0 0 8px 0; font-size: 28px; font-weight: 800; letter-spacing: 0.5px;
  background: linear-gradient(90deg, #0f172a, #334155);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.header-titles p { margin: 0; color: #64748b; font-size: 15px; font-weight: 500;}

/* 高级按钮质感 */
.export-btn { 
  display: flex; align-items: center; gap: 8px; 
  background: linear-gradient(135deg, #1890FF 0%, #096dd9 100%); 
  color: #fff; padding: 12px 24px; border-radius: 12px; font-weight: 600; font-size: 15px;
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border: none;
  box-shadow: 0 4px 15px rgba(24, 144, 255, 0.3);
}
.export-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(24, 144, 255, 0.4); }
.export-btn:disabled { background: #cbd5e1; box-shadow: none; cursor: not-allowed; }

.risk-banner { 
  display: flex; align-items: center; gap: 16px;
  background: rgba(254, 226, 226, 0.8); backdrop-filter: blur(10px);
  border: 1px solid rgba(252, 165, 165, 0.5); border-left: 6px solid #ef4444; 
  color: #991b1b; padding: 20px 24px; border-radius: 12px; margin-bottom: 30px; 
  font-size: 15px; box-shadow: 0 4px 20px rgba(239, 68, 68, 0.05);
}
.banner-icon { font-size: 24px; }

.report-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }

/* 🌟 核心拟态卡片 (Glassmorphism) */
.card { 
  background: rgba(255, 255, 255, 0.7); 
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border-radius: 20px; padding: 28px; 
  box-shadow: 0 8px 32px rgba(148, 163, 184, 0.08); 
  border: 1px solid rgba(255, 255, 255, 0.8); 
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
}
.card:hover { 
  transform: translateY(-4px); 
  box-shadow: 0 16px 40px rgba(148, 163, 184, 0.15); 
  border-color: #fff;
}
.card h3 { margin: 0 0 24px 0; font-size: 18px; color: #0f172a; display: flex; align-items: center; gap: 8px; font-weight: 700; }

.card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.academic-download-btn { 
  display: flex; align-items: center; gap: 6px; font-size: 13px; color: #1890FF; 
  background: rgba(24, 144, 255, 0.1); border: none; padding: 6px 14px; border-radius: 20px; 
  cursor: pointer; transition: 0.3s; font-weight: 600;
}
.academic-download-btn:hover:not(:disabled) { background: rgba(24, 144, 255, 0.2); transform: scale(1.05);}
.mini-spinner { width: 14px; height: 14px; border: 2px solid #ccc; border-top-color: #1890FF; border-radius: 50%; animation: spin 1s linear infinite; }

.summary-card { grid-column: span 2; background: rgba(255, 255, 255, 0.85); }
.summary-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header-left { display: flex; align-items: center; gap: 16px; }

.persona-tag { 
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); color: #0284c7; 
  padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 700; border: none; box-shadow: 0 2px 8px rgba(2, 132, 199, 0.1);
}
.health-score-badge { display: flex; align-items: center; gap: 10px; background: #f0fdf4; padding: 8px 16px; border-radius: 12px; color: #166534; font-weight: 600; }
.health-score-badge.high { background: #fef2f2; color: #991b1b; } 
.health-score-badge.medium { background: #fffbeb; color: #b45309; } 
.score-value { font-size: 24px; font-weight: 800; font-family: 'SF Pro Display', sans-serif;}

.status-box { 
  background: rgba(240, 248, 255, 0.6); backdrop-filter: blur(4px);
  padding: 20px 24px; border-radius: 12px; margin-bottom: 28px; 
  color: #334155; line-height: 1.7; border-left: 4px solid #1890FF; font-size: 16px;
}
.status-box strong { color: #1890FF; }
.advice-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.issues h4, .actions h4 { font-size: 15px; margin-bottom: 16px; color: #0f172a; font-weight: 700; }
.advice-grid ul { padding-left: 20px; margin: 0; color: #475569; line-height: 1.9; font-size: 15px; }
.advice-grid li { margin-bottom: 10px; }

.risk-quotes-card { grid-column: span 2; background: rgba(255, 250, 250, 0.7); }
.quote-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
.quote-item { 
  background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 12px; 
  border-left: 4px solid #ef4444; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05); 
}
.quote-time { font-size: 13px; color: #94a3b8; margin-bottom: 10px; display: block; font-weight: 500;}
.quote-text { margin: 0; font-size: 15px; color: #334155; font-style: italic; line-height: 1.6; }

.chart { width: 100%; height: 300px; }

.sub-info { font-size: 14px; color: #64748b; margin-top: -12px; margin-bottom: 16px; font-weight: 500;}
.delta-badge { font-weight: bold; margin-left: 6px; padding: 2px 8px; border-radius: 10px; background: rgba(0,0,0,0.03);}
.warning { color: #ef4444; }
.good { color: #10b981; }

.word-cloud { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; height: 300px; padding: 10px; }
.cloud-word { font-weight: 800; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: default; }
.cloud-word:hover { transform: scale(1.2) rotate(-3deg); z-index: 10; text-shadow: 0 8px 20px rgba(24,144,255,0.3);}
.empty-cloud { color: #94a3b8; font-size: 14px; }

/* 🌟 入场动画 */
.fade-in { animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-state, .error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; color: #64748b; font-weight: 500;}
.spinner { width: 50px; height: 50px; border: 4px solid #e2e8f0; border-top-color: #1890FF; border-radius: 50%; animation: spin 1s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; margin-bottom: 24px; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .report-grid { grid-template-columns: 1fr; }
  .summary-card, .risk-quotes-card { grid-column: span 1; }
  .advice-grid { grid-template-columns: 1fr; }
}
</style>
<template>
  <div class="chart-container">
    <div v-if="hasData" class="chart-header">
      <div class="header-left">
        <div class="view-toggle">
          <button :class="{ active: currentView === 'timeline' }" @click="currentView = 'timeline'">
            📉 时间轨迹
          </button>
          <button :class="{ active: currentView === 'circumplex' }" @click="currentView = 'circumplex'">
            🧭 心理空间
          </button>
        </div>
        <span class="model-badge">AI 情绪动态追踪引擎</span>
        <button class="help-btn" @click="showHelpModal = true" title="读懂背后的心理学算法">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          算法解读
        </button>
      </div>
      
      <div class="header-right">
        <div v-if="currentView === 'timeline'" class="custom-legend">
          <div class="legend-item"><span class="dot peak"></span>巅峰</div>
          <div class="legend-item"><span class="dot valley"></span>谷底</div>
          <div class="legend-item"><span class="dot current"></span>当前</div>
        </div>
      </div>
    </div>

    <v-chart 
      v-if="hasData" 
      class="chart" 
      :option="currentOption" 
      :update-options="{ notMerge: true, lazyUpdate: true }"
      @click="handleChartClick"
      autoresize 
    />
    
    <div v-else class="empty-chart">
      <div class="empty-icon">📊</div>
      <p>暂无情绪数据</p>
      <span>与 AI 多聊几句，生成你的心理画像</span>
    </div>

    <div v-if="hasData && currentView === 'timeline'" class="trend-footer" :style="{ backgroundColor: emotionTrend.bgColor }">
      <div class="trend-icon">{{ emotionTrend.icon }}</div>
      <div class="trend-text">
        <strong>心境趋势诊断：</strong>
        <span :style="{ color: emotionTrend.color }">{{ emotionTrend.text }}</span>
      </div>
    </div>

    <transition name="fade">
      <div v-if="selectedPoint" class="detail-modal-overlay" @click="selectedPoint = null">
        <div class="detail-card" @click.stop>
          <div class="card-header">
            <span class="time-badge">🕒 {{ selectedPoint.time }}</span>
            <span class="academic-tag">{{ getAcademicLabel(selectedPoint.valence, selectedPoint.arousal) }}</span>
            <button class="close-btn" @click="selectedPoint = null">×</button>
          </div>
          
          <div class="card-body">
            <div class="quote-box">
              <div class="quote-icon">“</div>
              <p class="user-text">{{ selectedPoint.content }}</p>
            </div>

            <div class="metrics-grid">
              <div class="metric-item">
                <span class="metric-label">核心心境</span>
                <span class="metric-value highlight">{{ selectedPoint.score }}<small>分</small></span>
              </div>
              <div class="metric-item">
                <span class="metric-label">瞬时情绪</span>
                <span class="metric-value">{{ selectedPoint.tag }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">唤醒度 (Arousal)</span>
                <span class="metric-value" :style="{color: getEnergyColor(selectedPoint.arousal)}">
                  {{ selectedPoint.arousal }}/10
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">效价 (Valence)</span>
                <span class="metric-value" :style="{color: getValenceColor(selectedPoint.valence)}">
                  {{ selectedPoint.valence }}/10
                </span>
              </div>
            </div>

            <div class="insight-stack">
              <div class="ai-insight">
                <strong>💡 AI 深度解读：</strong>
                <p>{{ generateInsight(selectedPoint.valence, selectedPoint.arousal) }}</p>
              </div>
              <div class="cbt-insight">
                <strong>🛡️ CBT 干预建议：</strong>
                <p>{{ generateCBT(selectedPoint.valence, selectedPoint.arousal) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="showHelpModal" class="help-modal-overlay" @click="showHelpModal = false">
        <div class="help-card" @click.stop>
          <div class="help-header">
            <h3>💡 AI 情绪图表背后的科学算法</h3>
            <button class="close-btn" @click="showHelpModal = false">×</button>
          </div>
          <div class="help-body">
            
            <div class="help-section">
              <h4>🏛️ 理论一：Russell 情感环形模型 (1980)</h4>
              <p>“心理空间”视图并非随机生成，而是严谨基于 Russell 的经典情感双极模型。我们将您的每一句话投射到二维空间中：</p>
              <ul>
                <li><strong>横轴 (效价 Valence)：</strong>越靠右代表情绪越积极，越靠左越消极。</li>
                <li><strong>纵轴 (唤醒 Arousal)：</strong>越靠上代表躯体能量越充沛（如激动、焦虑），越靠下越低迷（如放松、抑郁）。</li>
              </ul>
            </div>
            
            <div class="help-section">
              <h4>🌊 理论二：ALMA 分层情感架构 (Gebhard, 2005)</h4>
              <p>为什么“时间轨迹”曲线没有随着你的一句玩笑话剧烈波动？系统区分了由单次事件触发的短暂<strong>“情绪 (Emotion)”</strong>，以及没有明确指向的长期<strong>“心境 (Mood)”</strong>。每一个瞬时情绪发生后，都会像磁铁一样，以一定权重缓慢拉动底层的心境质心，计算出更平滑、客观的内稳态曲线。</p>
            </div>

            <div class="help-section">
              <h4>⚓ 理论三：动态情感惯性 (Kuppens 等, 2010)</h4>
              <p>人的心理是存在“惯性”的。前一刻的心情能在很大程度上预测下一刻的心境。在算法层面，系统引入了动态自回归（Autoregressive）机制：<strong>当您处于低落状态时，算法会自动增加“情感阻尼”权重。</strong>这意味着系统充分理解您难以瞬间走出低谷的心理阻力，避免不切实际的评分骤升，从而提供更贴合真实状态的 CBT 陪伴干预。</p>
            </div>

            <div class="help-section highlight-section">
              <h4>🌌 视觉现象：坐标坍缩现象</h4>
              <p>当您连续处于极其相似的情绪状态时，二维坐标会发生重叠。此时图表上的紫点会<strong>因为半透明叠加而颜色极深</strong>，这代表您在该情绪极点上积攒了极高的“心理滞留度”。</p>
            </div>

          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart, ScatterChart, LinesChart, EffectScatterChart } from 'echarts/charts'; 
import {
  GridComponent,
  TooltipComponent,
  VisualMapComponent,
  MarkLineComponent,
  MarkAreaComponent,
  TitleComponent,
  MarkPointComponent, 
  DataZoomComponent   
} from 'echarts/components';
import VChart from 'vue-echarts';

use([
  CanvasRenderer, LineChart, ScatterChart, LinesChart, EffectScatterChart, 
  GridComponent, TooltipComponent, VisualMapComponent, MarkLineComponent,
  MarkAreaComponent, TitleComponent, MarkPointComponent, DataZoomComponent
]);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ dates: [], scores: [], arousals: [], valences: [], tags: [], contents: [] })
  }
});

const hasData = computed(() => props.chartData?.scores?.length > 0);

const currentView = ref('timeline');
const selectedPoint = ref(null);
const showHelpModal = ref(false);

const getEnergyColor = (a) => a >= 5.5 ? '#f59e0b' : '#3b82f6';
const getValenceColor = (v) => v >= 5.5 ? '#10b981' : '#ef4444';

const getAcademicLabel = (v, a) => {
  const vStr = v >= 5.5 ? '正效价' : '负效价';
  const aStr = a >= 5.5 ? '高唤醒' : '低唤醒';
  return `${vStr} + ${aStr}`;
};

const emotionTrend = computed(() => {
  if (!hasData.value || props.chartData.scores.length < 2) {
    return { icon: '⚖️', text: '数据收集初期，等待进一步分析', color: '#64748b', bgColor: '#f8fafc' };
  }
  const scores = props.chartData.scores;
  const start = scores[0];
  const end = scores[scores.length - 1];
  const diff = end - start;
  const percent = start === 0 ? (diff > 0 ? 100 : 0) : Math.round((Math.abs(diff) / start) * 100);

  if (diff >= 5) {
    return { icon: '📈', text: `心境整体呈上升改善趋势 (+${percent}%)`, color: '#10b981', bgColor: 'rgba(16, 185, 129, 0.05)' };
  } else if (diff <= -5) {
    return { icon: '📉', text: `心境整体呈下降预警趋势 (-${percent}%)`, color: '#ef4444', bgColor: 'rgba(239, 68, 68, 0.05)' };
  } else {
    return { icon: '〰️', text: `心理内环境保持平稳状态`, color: '#f59e0b', bgColor: 'rgba(245, 158, 11, 0.05)' };
  }
});

const generateInsight = (v, a) => {
  if (v >= 5.5 && a >= 5.5) return "你当时处于高能量的积极状态（如开心、激动），思维活跃，行动力强，是创造力的高峰期。";
  if (v >= 5.5 && a < 5.5) return "你当时处于低能量的积极状态（如放松、平静），内心充满安全感，非常适合休息和深度思考。";
  if (v < 5.5 && a >= 5.5) return "你当时处于高能量的消极状态（如焦虑、愤怒），身体处于应激警觉状态，消耗了大量精力，需要注意情绪着陆。";
  if (v < 5.5 && a < 5.5) return "你当时处于低能量的消极状态（如抑郁、疲惫），心理防线较脆弱，此时什么都不做、好好睡一觉就是最好的治愈。";
  return "你的情绪处于中性平稳状态，像缓缓流淌的小溪。";
};

const generateCBT = (v, a) => {
  if (v >= 5.5 && a >= 5.5) return "【积极强化】建议使用'品味(Savoring)'技术，在脑海中停留并强化这份快乐，建立积极心理锚点。";
  if (v >= 5.5 && a < 5.5) return "【正念冥想】维持现状。建议进行简单的正念身体扫描，储存这份宁静的心理能量以备不时之需。";
  if (v < 5.5 && a >= 5.5) return "【认知重构】高应激警告！请立即停止灾难化思考，尝试 5-4-3-2-1 五感着陆法，将注意力拉回当下躯体。";
  if (v < 5.5 && a < 5.5) return "【行为激活】低耗竭预警！不要强迫自己“振作”，试着完成一个极微小的行动（如喝杯温水），用微弱的躯体动作打破情绪死循环。";
};

const handleChartClick = (params) => {
  if (params.componentType !== 'series' || params.seriesType === 'lines') return; 
  let index = params.dataIndex;
  
  if (params.seriesType === 'effectScatter') {
    index = props.chartData.dates.length - 1;
  }
  
  selectedPoint.value = {
    time: props.chartData.dates[index],
    score: props.chartData.scores[index],
    tag: props.chartData.tags?.[index] || '平静',
    content: props.chartData.contents?.[index] || '（无文本记录）',
    valence: Math.round((props.chartData.valences?.[index] || 5) * 10) / 10,
    arousal: Math.round((props.chartData.arousals?.[index] || 5) * 10) / 10
  };
};
// 时间轨迹
const timelineOption = computed(() => {
  if (!hasData.value) return {};
  const lastIdx = props.chartData.dates.length - 1;
  const lastDate = props.chartData.dates[lastIdx];
  const lastScore = props.chartData.scores[lastIdx];

  return {
    backgroundColor: 'transparent',
    // ✨ 核心动画控制：开启数据更新时的平滑过渡
    animation: true,
    animationDuration: 1000,          // 第一次进网页时的绘制时长
    animationDurationUpdate: 500,     // 每次发新消息时，新点延伸的时长
    animationEasingUpdate: 'cubicInOut',

    grid: { top: '15%', bottom: '20%', left: '2%', right: '5%', containLabel: true },
  
    dataZoom: [
      { type: 'inside', xAxisIndex: 0, filterMode: 'filter' }, 
      { 
        type: 'slider', xAxisIndex: 0, height: 12, bottom: 5, 
        borderColor: 'transparent', backgroundColor: 'rgba(123, 97, 255, 0.05)',
        fillerColor: 'rgba(123, 97, 255, 0.2)', handleStyle: { color: '#7b61ff' },
        showDetail: false 
      }
    ],
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0', padding: 12, textStyle: { color: '#334155' },
      extraCssText: 'border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);',
      formatter: (params) => {
        const i = params[0].dataIndex;
        const tag = props.chartData.tags[i] || '未知';
        const score = props.chartData.scores[i];
        const academicStr = getAcademicLabel(props.chartData.valences[i]||5, props.chartData.arousals[i]||5);
        return `<b>🕒 ${params[0].name}</b><br/>状态: ${tag} <span style="color:#94a3b8;font-size:11px;">(${academicStr})</span><br/>核心心境: <b style="color:#7b61ff">${score}</b> 分<br/><small style="color:#94a3b8">👉 点击圆点查看深度解析</small>`;
      }
    },
    xAxis: {
      type: 'category', data: props.chartData.dates, boundaryGap: false,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#9ca3af', fontSize: 11, margin: 12 }
    },
    yAxis: {
      type: 'value', min: 0, max: 100, splitNumber: 4,
      axisLine: { show: false }, axisTick: { show: false },
      axisLabel: { color: '#9ca3af', fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: 'rgba(123, 97, 255, 0.1)' } }
    },
    series: [
      {
        data: props.chartData.scores, type: 'line', smooth: 0.4, symbol: 'circle', symbolSize: 8, showSymbol: true, 
        itemStyle: { borderWidth: 2, borderColor: '#fff' },
        lineStyle: { width: 4, shadowColor: 'rgba(0,0,0,0.1)', shadowBlur: 10, shadowOffsetY: 5 },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(123, 97, 255, 0.25)' }, { offset: 1, color: 'rgba(123, 97, 255, 0)' }] } },
        markPoint: {
          symbol: 'pin', symbolSize: 45,
          data: [
            { type: 'max', name: '巅峰', itemStyle: { color: '#f59e0b' } },
            { type: 'min', name: '谷底', itemStyle: { color: '#60a5fa' } },
            { name: '当前', coord: [lastDate, lastScore], value: lastScore, itemStyle: { color: '#ef4444' } }
          ],
          label: { fontSize: 10, color: '#fff', formatter: '{c}', show: true }
        }
      },
      {
        type: 'effectScatter', coordinateSystem: 'cartesian2d', data: [[lastDate, lastScore]], 
        symbolSize: 14, showEffectOn: 'render', rippleEffect: { brushType: 'stroke', scale: 3.5 },
        itemStyle: { color: '#ef4444', shadowBlur: 10, shadowColor: 'rgba(239, 68, 68, 0.5)' },
        zlevel: 5, tooltip: { show: false } 
      }
    ]
  };
});
// 心理空间
const circumplexOption = computed(() => {
  if (!hasData.value) return {};
  
  const valences = props.chartData.valences || [];
  const arousals = props.chartData.arousals || [];
  
  // ✨ 升级 1：重构散点数据，专门为“起点”和“当前”定制颜色、大小和层级
  const scatterData = valences.map((v, i) => {
    const isStart = i === 0;
    const isEnd = i === valences.length - 1;
    
    let color = 'rgba(123, 97, 255, 0.4)'; // 默认：半透明紫
    let borderColor = '#fff';
    let size = 14;
    let zlevel = 3;

    if (isStart) {
      color = '#10b981'; // 起点：治愈绿
      borderColor = '#059669';
      size = 18;
      zlevel = 4;
    } else if (isEnd) {
      color = '#ef4444'; // 当前：警示红
      borderColor = '#b91c1c';
      size = 18;
      zlevel = 5;
    }

    return {
      value: [v, arousals[i] || 5],
      itemStyle: { color, borderColor, borderWidth: 2, shadowColor: color, shadowBlur: 8 },
      symbolSize: size,
      zlevel,
      isStart, // 埋入标记供 Tooltip 使用
      isEnd
    };
  });

  // ✨ 升级 2：修复连线读取逻辑（因为 scatterData 现在变成了对象数组）
  const lineData = scatterData.slice(0, -1).map((point, i) => ({
    coords: [point.value, scatterData[i + 1].value]
  }));

  const startPoint = scatterData[0].value;
  const endPoint = scatterData[scatterData.length - 1].value;

  return {
    backgroundColor: 'transparent',
    grid: { top: '5%', bottom: '5%', left: '5%', right: '5%', containLabel: true },
    tooltip: {
      trigger: 'item', backgroundColor: 'rgba(255, 255, 255, 0.9)', padding: 10,
      formatter: (params) => {
        if(params.seriesType === 'lines') return ''; 
        const i = params.dataIndex;
        const time = props.chartData.dates[i];
        const tag = props.chartData.tags[i] || '未知';
        const academicStr = getAcademicLabel(props.chartData.valences[i]||5, props.chartData.arousals[i]||5);
        
        // Tooltip 里也明示起点和当前
        let prefix = '🕒';
        if (params.data.isStart) prefix = '🟢 [初始状态]';
        if (params.data.isEnd) prefix = '🔴 [当前状态]';

        return `<b>${prefix} ${time}</b><br/>${tag} <span style="color:#94a3b8;font-size:11px;">(${academicStr})</span><br/><small style="color:#94a3b8">👉 点击查看 CBT 建议</small>`;
      }
    },
    xAxis: { type: 'value', min: 1, max: 10, splitLine: { show: false }, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#cbd5e1', width: 2 } } },
    yAxis: { type: 'value', min: 1, max: 10, splitLine: { show: false }, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#cbd5e1', width: 2 } } },
    series: [
      {
        type: 'scatter',
        data: scatterData,
      },
      {
        type: 'lines', coordinateSystem: 'cartesian2d', data: lineData, zlevel: 2,
        effect: { show: true, period: 4, trailLength: 0.2, symbol: 'arrow', symbolSize: 8, color: '#7b61ff' },
        lineStyle: { color: 'rgba(123, 97, 255, 0.3)', width: 2, type: 'dashed', curveness: 0.2 }
      },
      // ✨ 升级 3：强制加上“起点”和“当前”的图钉文本 (MarkPoint)
      {
        type: 'scatter', data: [],
        markPoint: {
          symbol: 'pin', symbolSize: 45,
          data: [
            { name: '起点', coord: startPoint, value: '起点', itemStyle: { color: '#10b981' } },
            { name: '当前', coord: endPoint, value: '当前', itemStyle: { color: '#ef4444' } }
          ],
          label: { color: '#fff', fontSize: 10, formatter: '{c}' }
        }
      },
      // ✨ 升级 4：给最终的“当前状态”加上显眼的呼吸涟漪光环
      {
        type: 'effectScatter', coordinateSystem: 'cartesian2d', data: [endPoint],
        symbolSize: 18, showEffectOn: 'render', rippleEffect: { brushType: 'stroke', scale: 3.5 },
        itemStyle: { color: '#ef4444', shadowBlur: 10, shadowColor: 'rgba(239, 68, 68, 0.5)' },
        zlevel: 5, tooltip: { show: false } 
      },
      {
        type: 'line', data: [], 
        markArea: {
          silent: true,
          label: { show: true, position: 'inside', color: 'rgba(0,0,0,0.15)', fontSize: 16, fontWeight: 'bold' },
          data: [
            [{ xAxis: 5.5, yAxis: 5.5, name: '激越 / 兴奋\n(高效价+高唤醒)', itemStyle: { color: 'rgba(245, 158, 11, 0.05)' } }, { xAxis: 10, yAxis: 10 }], 
            [{ xAxis: 1, yAxis: 5.5, name: '应激 / 焦虑\n(负效价+高唤醒)', itemStyle: { color: 'rgba(239, 68, 68, 0.05)' } }, { xAxis: 5.5, yAxis: 10 }], 
            [{ xAxis: 1, yAxis: 1, name: '无力 / 抑郁\n(负效价+低唤醒)', itemStyle: { color: 'rgba(59, 130, 246, 0.05)' } }, { xAxis: 5.5, yAxis: 5.5 }], 
            [{ xAxis: 5.5, yAxis: 1, name: '平静 / 放松\n(正效价+低唤醒)', itemStyle: { color: 'rgba(16, 185, 129, 0.05)' } }, { xAxis: 10, yAxis: 5.5 }]  
          ]
        }
      }
    ]
  };
});

const currentOption = computed(() => {
  return currentView.value === 'timeline' ? timelineOption.value : circumplexOption.value;
});
</script>

<style scoped>
.chart-container { width: 100%; height: 100%; position: relative; display: flex; flex-direction: column; }
.chart { flex: 1; width: 100%; }

.chart-header { display: flex; justify-content: space-between; align-items: center; padding: 0 4px; margin-bottom: 10px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.view-toggle { display: flex; background: rgba(0,0,0,0.04); border-radius: 20px; padding: 4px; }
.view-toggle button { background: transparent; border: none; padding: 6px 12px; font-size: 12px; border-radius: 16px; cursor: pointer; color: #64748b; transition: all 0.3s; font-weight: 500; }
.view-toggle button.active { background: #fff; color: #7b61ff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.model-badge { font-size: 10px; color: #7b61ff; background: rgba(123, 97, 255, 0.1); padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(123, 97, 255, 0.2); }

.help-btn { display: flex; align-items: center; gap: 4px; background: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16, 185, 129, 0.2); padding: 4px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
.help-btn:hover { background: rgba(16, 185, 129, 0.15); transform: translateY(-1px); box-shadow: 0 2px 5px rgba(16, 185, 129, 0.1); }

.header-right { display: flex; align-items: center; gap: 16px; }
.custom-legend { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.02); padding: 4px 10px; border-radius: 12px; }
.legend-item { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #64748b; font-weight: 500; }
.legend-item .dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.dot.peak { background: #f59e0b; }
.dot.valley { background: #60a5fa; }
.dot.current { background: #ef4444; }

.trend-footer { display: flex; align-items: center; gap: 8px; margin-top: 4px; padding: 10px 14px; border-radius: 8px; border-top: 1px dashed rgba(0,0,0,0.05); }
.trend-icon { font-size: 16px; }
.trend-text { font-size: 13px; }
.trend-text strong { color: #475569; margin-right: 6px; }

.empty-chart { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: rgba(255, 255, 255, 0.4); border-radius: 16px; border: 1px dashed rgba(123, 97, 255, 0.2); color: #9ca3af; }
.empty-icon { font-size: 32px; margin-bottom: 8px; opacity: 0.5; }
.empty-chart p { font-size: 14px; margin: 0 0 4px 0; font-weight: 600; color: #4b5563; }
.empty-chart span { font-size: 12px; }

.detail-modal-overlay, .help-modal-overlay { 
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
  background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(8px); 
  z-index: 99999; display: flex; align-items: center; justify-content: center; 
}

.detail-card { width: 90%; max-width: 360px; background: #fff; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); overflow: hidden; animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); border: 1px solid rgba(123, 97, 255, 0.1); }
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #f1f5f9; }
.time-badge { font-size: 13px; font-weight: 600; color: #475569; }
.academic-tag { font-size: 11px; background: #e2e8f0; color: #475569; padding: 3px 8px; border-radius: 12px; font-weight: bold; }
.close-btn { background: none; border: none; font-size: 20px; color: #94a3b8; cursor: pointer; line-height: 1; transition: color 0.2s; }
.close-btn:hover { color: #ef4444; }

.card-body { padding: 16px; max-height: 70vh; overflow-y: auto; }
.quote-box { display: flex; background: rgba(123, 97, 255, 0.05); padding: 12px; border-radius: 12px; margin-bottom: 16px; position: relative; }
.quote-icon { font-size: 30px; font-family: serif; color: rgba(123, 97, 255, 0.3); line-height: 1; margin-right: 8px; margin-top: -4px; }
.user-text { font-size: 14px; color: #334155; line-height: 1.5; margin: 0; font-style: italic; }

.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.metric-item { display: flex; flex-direction: column; background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.02); }
.metric-label { font-size: 11px; color: #64748b; margin-bottom: 4px; }
.metric-value { font-size: 15px; font-weight: bold; color: #334155; }
.metric-value.highlight { color: #7b61ff; font-size: 18px; }

.insight-stack { display: flex; flex-direction: column; gap: 10px; }
.ai-insight { background: linear-gradient(135deg, rgba(245,158,11,0.05) 0%, rgba(239,68,68,0.05) 100%); padding: 12px; border-radius: 8px; border-left: 3px solid #f59e0b; }
.ai-insight strong { display: block; font-size: 12px; color: #d97706; margin-bottom: 6px; }
.ai-insight p { font-size: 12px; color: #78350f; margin: 0; line-height: 1.5; }
.cbt-insight { background: linear-gradient(135deg, rgba(16,185,129,0.05) 0%, rgba(59,130,246,0.05) 100%); padding: 12px; border-radius: 8px; border-left: 3px solid #10b981; }
.cbt-insight strong { display: block; font-size: 12px; color: #059669; margin-bottom: 6px; }
.cbt-insight p { font-size: 12px; color: #064e3b; margin: 0; line-height: 1.5; }

/* 帮助弹窗专属学术风格 */
.help-card { width: 90%; max-width: 480px; background: #fff; border-radius: 16px; box-shadow: 0 10px 50px rgba(0,0,0,0.15); overflow: hidden; animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.help-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.help-header h3 { margin: 0; font-size: 16px; color: #1e293b; font-weight: 700; letter-spacing: 0.5px; }
.help-body { padding: 24px 20px; max-height: 70vh; overflow-y: auto; }
.help-section { margin-bottom: 24px; }
.help-section:last-child { margin-bottom: 0; }
.help-section h4 { margin: 0 0 10px 0; font-size: 14px; color: #6366f1; display: flex; align-items: center; gap: 6px; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px;}
.help-section p { margin: 0 0 8px 0; font-size: 13px; color: #475569; line-height: 1.6; text-align: justify; }
.help-section ul { margin: 0; padding-left: 20px; font-size: 13px; color: #475569; line-height: 1.6; }
.help-section li { margin-bottom: 6px; }
.help-section strong { color: #334155; }
.highlight-section { background: rgba(99, 102, 241, 0.05); padding: 16px; border-radius: 8px; border-left: 4px solid #6366f1; border-right: 1px solid #e0e7ff; border-top: 1px solid #e0e7ff; border-bottom: 1px solid #e0e7ff;}
.highlight-section h4 { color: #4f46e5; border-bottom: none; padding-bottom: 0;}

@keyframes popIn { 0% { transform: scale(0.95); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
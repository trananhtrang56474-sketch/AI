<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="show" class="modal-overlay" @click.self="close">
        
        <div class="glass-modal portrait-modal">
          <button class="close-btn" @click="close" title="关闭">×</button>
          
          <div class="modal-header">
            <div class="header-icon">
              <span class="pulse-bg"></span>
              🧬
            </div>
            <div class="header-text">
              <h2>AI 心理画像深度解析</h2>
              <p>基于最近 {{ recordCount }} 条心境轨迹 · 量子化演算</p>
            </div>
          </div>

          <div class="modal-scroll-content">
            
            <div class="section-card core-state">
              <div class="state-left">
                <span class="big-emoji">{{ emotionIcon }}</span>
                <div class="state-titles">
                  <h3>
                    {{ dominantEmotion }} 
                    <span class="sub-state" :style="{ color: emotionColor, background: emotionColor + '15' }">
                      + 轻度{{ subState }}
                    </span>
                  </h3>
                  <p class="ai-desc">"{{ trendText }}"</p>
                </div>
              </div>
              
              <div class="state-right">
                <div class="stat-row">
                  <div class="stat-label"><span>🛡️ 稳定度</span></div>
                  <div class="stat-bar">
                    <div class="fill stability-fill" :style="{ width: showAnim ? stabilityScore + '%' : '0%' }"></div>
                  </div>
                  <span class="stat-val">{{ stabilityScore }}</span>
                </div>
                <div class="stat-row">
                  <div class="stat-label"><span>🌪️ 压力值</span></div>
                  <div class="stat-bar">
                    <div class="fill stress-fill" :style="{ width: showAnim ? stressScore + '%' : '0%' }"></div>
                  </div>
                  <span class="stat-val" :class="{'danger-text': stressScore > 70}">{{ stressLevel }}</span>
                </div>
              </div>
            </div>

            <div class="grid-2-col">
              
              <div class="section-card">
                <h4>📊 情绪成分拆解</h4>
                <div class="composition-list">
                  <div class="comp-item">
                    <div class="comp-label">{{ dominantEmotion }} <small>(主导)</small></div>
                    <div class="comp-bar-bg">
                      <div class="comp-bar-fill" :style="{ width: showAnim ? primaryRatio + '%' : '0%', background: emotionColor }"></div>
                    </div>
                    <div class="comp-val" :style="{ color: emotionColor }">{{ primaryRatio }}%</div>
                  </div>
                  <div class="comp-item">
                    <div class="comp-label">环境杂音 <small>(潜意识)</small></div>
                    <div class="comp-bar-bg">
                      <div class="comp-bar-fill secondary-fill" :style="{ width: showAnim ? secondaryRatio + '%' : '0%' }"></div>
                    </div>
                    <div class="comp-val">{{ secondaryRatio }}%</div>
                  </div>
                </div>
                <div class="tags-cloud">
                  <span class="ai-tag">#{{ trendName }}</span>
                  <span class="ai-tag">#自我觉察期</span>
                  <span class="ai-tag" v-if="recentValence > 6">#趋向积极</span>
                  <span class="ai-tag" v-else>#寻求安全感</span>
                </div>
              </div>

              <div class="section-card ai-reasoning">
                <h4>🤖 AI 判读依据</h4>
                <ul class="reason-list">
                  <li>
                    <span class="dot" :style="{ background: emotionColor }"></span>
                    <span><strong>词频特征：</strong>近期高频表现出“{{ dominantEmotion }}”相关意象。</span>
                  </li>
                  <li>
                    <span class="dot" :style="{ background: emotionColor }"></span>
                    <span><strong>波动特征：</strong>情绪极差为 {{ scoreVolatility }} 分，心境内环境{{ volatilityDesc }}。</span>
                  </li>
                  <li>
                    <span class="dot" :style="{ background: '#10b981' }"></span>
                    <span><strong>安全评估：</strong>当前心理内稳态未被破坏 (低风险)。</span>
                  </li>
                </ul>
              </div>
            </div>

            <div class="section-card strategy-box">
              <div class="strategy-header">
                <span class="strategy-badge">🎯 当前干预策略：{{ strategyName }}</span>
                <p>系统已自动切入“{{ strategyDesc }}”模式</p>
              </div>
              <div class="suggestion-area">
                <h4>💡 此刻的温柔建议 (CBT 指导)</h4>
                <div class="suggestion-text">
                  {{ suggestionText }}
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';

const props = defineProps({
  show: Boolean,
  // AI 给出的单次分析 (用于兜底和策略文本)
  analysis: {
    type: Object,
    default: () => ({ emotion: '平静', score: 60, strategy: 'GENERAL_SUPPORT', trend: 'FIRST_CONTACT' })
  },
  // ✨ 核心灵魂：接入图表历史数据阵列
  chartData: {
    type: Object,
    default: () => ({ dates: [], scores: [], arousals: [], valences: [], tags: [], contents: [] })
  }
});

const emit = defineEmits(['close']);
const close = () => emit('close');

const showAnim = ref(false);
watch(() => props.show, (newVal) => {
  if (newVal) {
    showAnim.value = false;
    nextTick(() => { setTimeout(() => { showAnim.value = true; }, 100); });
  }
});

const EMOTION_MAPS = {
  colors: { '危机': '#ef4444', '愤怒': '#f43f5e', '焦虑': '#f59e0b', '抑郁': '#64748b', '平静': '#10b981', '积极': '#14b8a6', '悲伤': '#3b82f6' },
  icons: { '危机': '🆘', '愤怒': '😠', '焦虑': '😰', '抑郁': '🌧️', '平静': '🍃', '积极': '☀️', '迷茫': '😶‍🌫️', '悲伤': '💧' }
};

const recordCount = computed(() => props.chartData.scores?.length || 0);

// ==========================================
// 🧠 核心 1：真实数据聚合推演 (Data Aggregation)
// ==========================================

// ✨ 找出出现频率最高的情绪标签 (真实主导情绪)
const dominantEmotion = computed(() => {
  const tags = props.chartData.tags;
  if (!tags || tags.length === 0) return props.analysis.emotion;
  
  const frequency = {};
  let maxTag = tags[0];
  let maxCount = 0;
  
  for (const tag of tags) {
    frequency[tag] = (frequency[tag] || 0) + 1;
    if (frequency[tag] > maxCount) {
      maxCount = frequency[tag];
      maxTag = tag;
    }
  }
  return maxTag;
});

// ✨ 真实主导情绪的百分比占比
const primaryRatio = computed(() => {
  const tags = props.chartData.tags;
  if (!tags || tags.length === 0) return 60;
  const count = tags.filter(t => t === dominantEmotion.value).length;
  return Math.round((count / tags.length) * 100);
});
const secondaryRatio = computed(() => (100 - primaryRatio.value).toFixed(0));

// ✨ 真实波动极差 (最高分 - 最低分)
const scoreVolatility = computed(() => {
  const scores = props.chartData.scores;
  if (!scores || scores.length < 2) return 10;
  const max = Math.max(...scores);
  const min = Math.min(...scores);
  return max - min;
});

const volatilityDesc = computed(() => {
  if (scoreVolatility.value > 30) return "波动剧烈";
  if (scoreVolatility.value > 15) return "出现起伏";
  return "非常稳固";
});

// ✨ 真实稳定度：100 - (极差 * 惩罚系数)
const stabilityScore = computed(() => {
  if (recordCount.value < 2) return 85; // 默认较稳
  return Math.max(20, 100 - scoreVolatility.value * 1.5).toFixed(0);
});

// ✨ 真实压力值：基于最新的唤醒度 (Arousal)
const recentArousal = computed(() => {
  const arousals = props.chartData.arousals;
  return (arousals && arousals.length > 0) ? arousals[arousals.length - 1] : 5;
});
const recentValence = computed(() => {
  const valences = props.chartData.valences;
  return (valences && valences.length > 0) ? valences[valences.length - 1] : 5;
});

// 如果高唤醒且负效价，压力爆表；如果正效价，那是开心激动，压力要减小。
const stressScore = computed(() => {
  if (recordCount.value === 0) return 40;
  let stress = recentArousal.value * 10; 
  if (recentValence.value > 6) stress -= 20; // 开心带来的高唤醒不算压力
  if (recentValence.value < 4) stress += 15; // 难过带来的高唤醒压力激增
  return Math.min(95, Math.max(10, stress)).toFixed(0);
});
const stressLevel = computed(() => stressScore.value > 75 ? '偏高' : (stressScore.value > 45 ? '中等' : '健康'));

// ==========================================
// 🎨 样式与文案生成 (基于主导情绪)
// ==========================================

const emotionColor = computed(() => EMOTION_MAPS.colors[dominantEmotion.value] || '#7b61ff');
const emotionIcon = computed(() => EMOTION_MAPS.icons[dominantEmotion.value] || '🧠');

const subState = computed(() => {
  if (['焦虑', '愤怒', '危机'].includes(dominantEmotion.value)) return '紧绷';
  if (['抑郁', '悲伤'].includes(dominantEmotion.value)) return '耗竭';
  return '放松';
});

const trendName = computed(() => {
  const map = { "FIRST_CONTACT": "首次建档", "FLUCTUATING": "震荡期", "IMPROVING": "趋势向好", "WORSENING": "承压加剧", "PERSISTENT_NEGATIVE": "低谷盘整" };
  return map[props.analysis.trend] || "演算中";
});

const trendText = computed(() => {
  if (props.analysis.trend === 'IMPROVING') return '情绪正在从紧绷走向平缓，这是一个正在自我调节的积极信号。';
  if (props.analysis.trend === 'WORSENING') return '检测到心理张力正在累积，别硬撑，也许我们需要停下来梳理一下。';
  return '在近期的交互中，核心心理参数保持相对平稳，处于安全阈值内。';
});

const strategyName = computed(() => {
  const map = { "CRISIS_INTERVENTION": "危机干预", "DEEP_VALIDATION": "深度共情", "EMPATHY_SUPPORT": "情感支持", "COGNITIVE_RESTRUCTURING": "认知重构", "GENERAL_SUPPORT": "防卫性倾听" };
  return map[props.analysis.strategy] || "防卫性倾听";
});

const strategyDesc = computed(() => {
  const map = {
    "GENERAL_SUPPORT": "不进行强干预，提供非评判性的绝对安全空间。",
    "DEEP_VALIDATION": "侧重于无条件接纳感受，确认情绪的合法性。",
    "COGNITIVE_RESTRUCTURING": "温和地识别逻辑误区，引导建立更具适应性的视角。"
  };
  return map[props.analysis.strategy] || "以无条件积极关注为主，陪伴在侧。";
});

const suggestionText = computed(() => {
  if (['焦虑', '愤怒'].includes(dominantEmotion.value)) return '🌿 CBT着陆技术：寻找周围 3 件蓝色的物品，深吸气 4 秒，缓缓呼气 6 秒。让身体的警报先解除。';
  if (['抑郁', '悲伤'].includes(dominantEmotion.value)) return '💧 行为激活：现在不需要强迫自己想明白。去喝半杯温水，或者洗把脸，用微小的物理动作打破精神内耗。';
  return '💡 觉察日记：你可以试着写下「我现在最困扰的一件小事是……」，把它具象化，大脑就不再感到失控。';
});
</script>

<style scoped>
.modal-overlay { 
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
  background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  z-index: 9999; display: flex; justify-content: center; align-items: center; 
}
.portrait-modal { 
  width: 92%; max-width: 680px; max-height: 88vh; 
  background: #ffffff; border-radius: 24px; 
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); 
  border: 1px solid rgba(255,255,255,0.8); 
  display: flex; flex-direction: column; position: relative; 
  animation: modalPop 0.4s cubic-bezier(0.16, 1, 0.3, 1); 
  overflow: hidden;
}
.close-btn { 
  position: absolute; top: 20px; right: 20px; width: 32px; height: 32px;
  background: rgba(0,0,0,0.05); border: none; border-radius: 50%;
  font-size: 20px; color: #64748b; cursor: pointer; 
  transition: all 0.2s; z-index: 10; display: flex; align-items: center; justify-content: center;
}
.close-btn:hover { background: rgba(0,0,0,0.1); color: #0f172a; transform: rotate(90deg); }

/* 头部 */
.modal-header { 
  padding: 24px 30px; display: flex; gap: 18px; align-items: center; 
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
  border-bottom: 1px solid #e2e8f0;
}
.header-icon { 
  font-size: 32px; background: #fff; width: 56px; height: 56px; 
  display: flex; align-items: center; justify-content: center; 
  border-radius: 16px; box-shadow: 0 8px 16px rgba(0,0,0,0.06); 
  position: relative;
}
.pulse-bg { position: absolute; width: 100%; height: 100%; border-radius: 16px; background: #7b61ff; opacity: 0.1; animation: pulse 2s infinite; z-index: 0; }
.header-text h2 { margin: 0; font-size: 20px; color: #1e293b; font-weight: 700; letter-spacing: 0.5px; }
.header-text p { margin: 6px 0 0 0; font-size: 13px; color: #64748b; }

/* 滚动区 */
.modal-scroll-content { padding: 30px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }
.modal-scroll-content::-webkit-scrollbar { width: 6px; }
.modal-scroll-content::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

/* 通用卡片 */
.section-card { background: #fff; border-radius: 16px; padding: 22px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }
.section-card h4 { margin: 0 0 16px 0; font-size: 15px; color: #334155; font-weight: 600; display: flex; align-items: center; gap: 6px; }

/* --- 1. 核心状态 --- */
.core-state { display: flex; align-items: center; border: 1px solid rgba(123, 97, 255, 0.15); background: linear-gradient(to right, #ffffff, #f5f3ff); }
.state-left { display: flex; gap: 16px; align-items: center; flex: 1; padding-right: 20px; }
.big-emoji { font-size: 52px; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.1)); }
.state-titles h3 { margin: 0; font-size: 24px; color: #0f172a; display: flex; align-items: center; gap: 10px; font-weight: 700; }
.sub-state { font-size: 13px; padding: 3px 10px; border-radius: 20px; font-weight: 600; }
.ai-desc { margin: 10px 0 0 0; font-size: 14px; color: #64748b; line-height: 1.5; }

.state-right { width: 180px; display: flex; flex-direction: column; gap: 16px; border-left: 1px dashed #cbd5e1; padding-left: 20px; flex-shrink: 0; }
.stat-row { display: flex; align-items: center; gap: 12px; font-size: 13px; }
.stat-label { width: 75px; color: #475569; font-weight: 500; }
.stat-bar { flex: 1; height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; background-clip: padding-box; }
.fill { height: 100%; border-radius: 4px; transition: width 1.2s cubic-bezier(0.34, 1.56, 0.64, 1); }
.stability-fill { background: linear-gradient(90deg, #34d399, #10b981); }
.stress-fill { background: linear-gradient(90deg, #fbbf24, #ef4444); }
.stat-val { font-weight: 700; width: 30px; text-align: right; color: #334155; font-size: 14px; }
.danger-text { color: #ef4444; }

/* --- 2. 网格 --- */
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* 成分拆解 */
.composition-list { display: flex; flex-direction: column; gap: 14px; margin-bottom: 20px; }
.comp-item { display: flex; align-items: center; gap: 12px; font-size: 13px; }
.comp-label { width: 90px; color: #334155; font-weight: 500; display: flex; flex-direction: column; line-height: 1.2; }
.comp-label small { font-size: 11px; color: #94a3b8; font-weight: normal; margin-top: 2px; }
.comp-bar-bg { flex: 1; height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.comp-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease-out; }
.secondary-fill { background: #94a3b8; }
.comp-val { width: 36px; text-align: right; color: #64748b; font-weight: 600; }

.tags-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.ai-tag { font-size: 12px; color: #6343ed; background: rgba(123, 97, 255, 0.08); padding: 5px 12px; border-radius: 16px; border: 1px solid rgba(123, 97, 255, 0.15); font-weight: 500; }

/* 判读 */
.reason-list { list-style: none; padding: 0; margin: 0; }
.reason-list li { display: flex; gap: 12px; font-size: 13px; color: #475569; margin-bottom: 14px; line-height: 1.6; }
.reason-list li:last-child { margin-bottom: 0; }
.dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 7px; flex-shrink: 0; box-shadow: 0 0 8px currentColor; }
.reason-list strong { color: #1e293b; }

/* --- 3. 策略 --- */
.strategy-box { background: linear-gradient(135deg, #fffbeb 0%, #fff 100%); border-color: rgba(245, 158, 11, 0.2); }
.strategy-header { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; border-bottom: 1px dashed #fcd34d; padding-bottom: 16px; }
.strategy-badge { align-self: flex-start; background: #f59e0b; color: white; padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2); }
.strategy-header p { margin: 0; font-size: 13px; color: #b45309; }
.suggestion-area h4 { color: #92400e; margin-bottom: 10px; }
.suggestion-text { font-size: 14px; color: #451a03; background: rgba(255,255,255,0.8); padding: 16px; border-radius: 12px; border-left: 4px solid #f59e0b; line-height: 1.6; font-weight: 500; }

/* --- 动画与适配 --- */
@keyframes modalPop { 
  0% { opacity: 0; transform: scale(0.95) translateY(20px); } 
  100% { opacity: 1; transform: scale(1) translateY(0); } 
}
@keyframes pulse { 
  0% { transform: scale(1); opacity: 0.2; } 
  50% { transform: scale(1.5); opacity: 0; } 
  100% { transform: scale(1); opacity: 0; } 
}
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

@media (max-width: 640px) {
  .core-state { flex-direction: column; align-items: stretch; gap: 20px; }
  .state-left { padding-right: 0; }
  .state-right { width: 100%; border-left: none; border-top: 1px dashed #cbd5e1; padding-left: 0; padding-top: 20px; }
  .grid-2-col { grid-template-columns: 1fr; }
  .modal-scroll-content { padding: 20px; }
  .modal-header { padding: 20px; }
  .header-icon { display: none; } 
}
</style>
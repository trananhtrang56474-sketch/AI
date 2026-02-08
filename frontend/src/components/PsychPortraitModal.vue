<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="show" class="modal-overlay" @click.self="close">
        
        <div class="glass-modal portrait-modal">
          <button class="close-btn" @click="close">×</button>
          
          <div class="modal-header">
            <div class="header-icon">🧬</div>
            <div class="header-text">
              <h2>AI 心理画像深度解析</h2>
              <p>基于最近 {{ new Date().getMinutes() }} 分钟的对话交互生成 · 实时计算</p>
            </div>
          </div>

          <div class="modal-scroll-content">
            
            <div class="section-card core-state">
              <div class="state-left">
                <span class="big-emoji">{{ emotionIcon }}</span>
                <div>
                  <h3>{{ analysis.emotion }} <span class="sub-state">+ 轻度{{ subState }}</span></h3>
                  <p class="ai-desc">"{{ trendText }}"</p>
                </div>
              </div>
              <div class="state-right">
                <div class="stat-row">
                  <span>🛡️ 稳定度</span>
                  <div class="stat-bar"><div class="fill" :style="{width: stabilityScore + '%', background: '#52c41a'}"></div></div>
                  <span class="stat-val">{{ stabilityScore }}</span>
                </div>
                <div class="stat-row">
                  <span>🌪️ 压力值</span>
                  <div class="stat-bar"><div class="fill" :style="{width: stressScore + '%', background: '#ff7875'}"></div></div>
                  <span class="stat-val">{{ stressLevel }}</span>
                </div>
              </div>
            </div>

            <div class="grid-2-col">
              <div class="section-card">
                <h4>📊 情绪成分拆解</h4>
                <div class="composition-list">
                  <div class="comp-item">
                    <div class="comp-label">{{ analysis.emotion }} (主导)</div>
                    <div class="comp-bar-bg"><div class="comp-bar-fill" :style="{width: '65%', background: emotionColor}"></div></div>
                    <div class="comp-val">65%</div>
                  </div>
                  <div class="comp-item">
                    <div class="comp-label">不确定感</div>
                    <div class="comp-bar-bg"><div class="comp-bar-fill" style="width: 20%; background: #bfbfbf"></div></div>
                    <div class="comp-val">20%</div>
                  </div>
                </div>
                <div class="tags-cloud">
                  <span class="ai-tag">#{{ trendName }}</span>
                  <span class="ai-tag">#自我觉察中</span>
                  <span class="ai-tag">#寻求认同</span>
                </div>
              </div>

              <div class="section-card ai-reasoning">
                <h4>🤖 AI 判读依据</h4>
                <ul class="reason-list">
                  <li>
                    <span class="dot"></span>
                    <span><strong>词汇信号：</strong>检测到“{{ keywords }}”等词出现频率增加。</span>
                  </li>
                  <li>
                    <span class="dot"></span>
                    <span><strong>语调分析：</strong>你的表达长度{{ msgLengthTrend }}，通常意味着{{ msgMeaning }}。</span>
                  </li>
                  <li>
                    <span class="dot"></span>
                    <span><strong>风险评估：</strong>当前无高风险负面表达 (安全)。</span>
                  </li>
                </ul>
              </div>
            </div>

            <div class="section-card strategy-box">
              <div class="strategy-header">
                <span class="strategy-badge">🎯 当前策略：{{ strategyName }}</span>
                <p>AI 正处于“{{ strategyDesc }}”模式</p>
              </div>
              <div class="suggestion-area">
                <h4>💡 此刻的温柔建议</h4>
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
import { computed } from 'vue';

// 1. 接收父组件传来的数据
const props = defineProps({
  show: Boolean,
  analysis: {
    type: Object,
    default: () => ({ emotion: '平静', score: 60, strategy: 'GENERAL_SUPPORT', trend: 'FIRST_CONTACT' })
  }
});

// 2. 定义事件，告诉父组件关闭弹窗
const emit = defineEmits(['close']);
const close = () => emit('close');

// 3. 这里的计算属性只服务于弹窗内部，不需要污染父组件
const emotionColor = computed(() => {
  const map = { '危机': '#ff4d4f', '愤怒': '#ff7875', '焦虑': '#fa8c16', '抑郁': '#8c8c8c', '平静': '#52c41a', '积极': '#fadb14' };
  return map[props.analysis.emotion] || '#722ed1';
});

const emotionIcon = computed(() => {
  const map = { '危机': '🆘', '愤怒': '😠', '焦虑': '😰', '抑郁': '🌧️', '平静': '🍃', '积极': '☀️', '迷茫': '😶‍🌫️' };
  return map[props.analysis.emotion] || '🧠';
});

const subState = computed(() => {
  if (['焦虑', '愤怒'].includes(props.analysis.emotion)) return '紧绷';
  if (['抑郁', '悲伤'].includes(props.analysis.emotion)) return '疲惫';
  return '放松';
});

const stabilityScore = computed(() => Math.max(20, 100 - (props.analysis.score || 50)));
const stressScore = computed(() => props.analysis.score || 40);
const stressLevel = computed(() => stressScore.value > 70 ? '高' : (stressScore.value > 40 ? '中' : '低'));

const trendName = computed(() => {
  const map = { "FIRST_CONTACT": "初次接触", "FLUCTUATING": "情绪波动", "IMPROVING": "正在好转", "WORSENING": "需关注", "PERSISTENT_NEGATIVE": "持续低落" };
  return map[props.analysis.trend] || "分析中";
});

const trendText = computed(() => {
  if (props.analysis.trend === 'IMPROVING') return '你的情绪正在从紧绷走向平缓，这是一个正在自我调节的信号。';
  if (props.analysis.trend === 'WORSENING') return '检测到情绪张力正在累积，也许我们需要停下来梳理一下。';
  return '在最近 30 分钟内，你的情绪指数保持相对平稳，状态可控。';
});

const keywords = computed(() => {
  if (['焦虑', '迷茫'].includes(props.analysis.emotion)) return '怎么办 / 担心 / 不确定';
  if (['抑郁', '难过'].includes(props.analysis.emotion)) return '没意义 / 累 / 不想动';
  return '还行 / 好的 / 嗯';
});

const msgLengthTrend = computed(() => ['焦虑', '愤怒'].includes(props.analysis.emotion) ? '变短且急促' : '相对完整');
const msgMeaning = computed(() => ['焦虑', '愤怒'].includes(props.analysis.emotion) ? '急于寻求答案' : '你可以理性思考');

const strategyName = computed(() => {
  const map = { "CRISIS_INTERVENTION": "危机干预", "DEEP_VALIDATION": "深度共情", "EMPATHY_SUPPORT": "情感支持", "COGNITIVE_RESTRUCTURING": "认知重构", "GENERAL_SUPPORT": "一般陪伴" };
  return map[props.analysis.strategy] || "一般陪伴";
});

const strategyDesc = computed(() => {
  const map = {
    "GENERAL_SUPPORT": "不进行强干预，以倾听和轻引导为主，提供安全空间。",
    "DEEP_VALIDATION": "侧重于接纳你的感受，让你知道这些情绪都是合理的。",
    "COGNITIVE_RESTRUCTURING": "尝试帮你识别想法中的逻辑误区，换个角度看问题。"
  };
  return map[props.analysis.strategy] || "以倾听为主，陪伴在你身边。";
});

const suggestionText = computed(() => {
  if (['焦虑', '紧张'].includes(props.analysis.emotion)) return '🌿 试着做 3 次深呼吸：吸气 4 秒，保持 4 秒，呼气 6 秒。让身体先慢下来。';
  if (['抑郁', '疲惫'].includes(props.analysis.emotion)) return '💧 也许可以先去喝一杯温水？不需要强迫自己振作，允许自己休息一会儿。';
  return '💡 你可以试着写一句：「我现在最困扰的一件小事是……」，把它具象化。';
});
</script>

<style scoped>
/* 这里只放跟模态框相关的 CSS，从原来 AsidePanel 里剪切过来的 */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.3); backdrop-filter: blur(8px); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.portrait-modal { width: 90%; max-width: 650px; max-height: 85vh; background: rgba(255, 255, 255, 0.95); border-radius: 24px; box-shadow: 0 25px 50px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.6); display: flex; flex-direction: column; position: relative; animation: modalPop 0.4s cubic-bezier(0.19, 1, 0.22, 1); }
.close-btn { position: absolute; top: 20px; right: 20px; background: none; border: none; font-size: 28px; color: #aaa; cursor: pointer; transition: 0.2s; z-index: 10; }
.close-btn:hover { color: #333; transform: rotate(90deg); }

.modal-header { padding: 24px 30px; border-bottom: 1px solid rgba(0,0,0,0.06); display: flex; gap: 16px; align-items: center; background: linear-gradient(to right, rgba(var(--primary-rgb),0.05), transparent); border-radius: 24px 24px 0 0; }
.header-icon { font-size: 36px; background: #fff; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.header-text h2 { margin: 0; font-size: 20px; color: #333; }
.header-text p { margin: 4px 0 0 0; font-size: 13px; color: #888; }

.modal-scroll-content { padding: 30px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }

/* 模块卡片通用 */
.section-card { background: #f8f9fa; border-radius: 16px; padding: 20px; border: 1px solid rgba(0,0,0,0.03); }
.section-card h4 { margin: 0 0 15px 0; font-size: 14px; color: #666; font-weight: 600; display: flex; align-items: center; gap: 6px; }

/* 核心状态区 */
.core-state { background: linear-gradient(135deg, #fff 0%, #f0f7ff 100%); display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(var(--primary-rgb), 0.1); box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
.state-left { display: flex; gap: 15px; align-items: center; width: 55%; }
.big-emoji { font-size: 48px; }
.state-left h3 { margin: 0; font-size: 22px; color: #333; display: flex; align-items: center; gap: 8px; }
.sub-state { font-size: 13px; color: #999; background: rgba(0,0,0,0.05); padding: 2px 8px; border-radius: 6px; font-weight: normal; }
.ai-desc { margin: 8px 0 0 0; font-size: 14px; color: var(--primary-color); font-weight: 500; font-style: italic; }

.state-right { width: 40%; display: flex; flex-direction: column; gap: 12px; border-left: 1px dashed #ddd; padding-left: 20px; }
.stat-row { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.stat-bar { flex: 1; height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
.fill { height: 100%; border-radius: 4px; }
.stat-val { font-weight: bold; width: 25px; text-align: right; color: #555; }

/* 网格布局 */
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* 成分拆解 */
.composition-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 15px; }
.comp-item { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.comp-label { width: 80px; color: #555; }
.comp-bar-bg { flex: 1; height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
.comp-bar-fill { height: 100%; border-radius: 4px; }
.comp-val { width: 30px; text-align: right; color: #999; font-size: 12px; }

.tags-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.ai-tag { font-size: 12px; color: #666; background: #fff; padding: 4px 10px; border-radius: 12px; border: 1px solid #eee; }

/* AI 判读 */
.reason-list { list-style: none; padding: 0; margin: 0; }
.reason-list li { display: flex; gap: 10px; font-size: 13px; color: #555; margin-bottom: 10px; line-height: 1.5; }
.dot { width: 6px; height: 6px; background: var(--primary-color); border-radius: 50%; margin-top: 7px; flex-shrink: 0; }

/* 策略 */
.strategy-box { background: #fffbf0; border-color: rgba(250, 173, 20, 0.2); }
.strategy-header { display: flex; flex-direction: column; gap: 5px; margin-bottom: 15px; border-bottom: 1px dashed rgba(0,0,0,0.05); padding-bottom: 15px; }
.strategy-badge { align-self: flex-start; background: #faad14; color: white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
.strategy-header p { margin: 0; font-size: 13px; color: #d48806; }
.suggestion-text { font-size: 14px; color: #555; background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #faad14; line-height: 1.6; }

/* 动画 */
@keyframes modalPop { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
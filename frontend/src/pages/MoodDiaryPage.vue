<template>
  <div class="page-container">
    <div class="content-wrapper">
      
      <div class="header">
        <button class="glass-btn back-btn" @click="$router.back()">
          <span class="icon">↩</span>
          <span>返回主页</span>
        </button>
        <div class="title-area">
          <h2>📝 情绪日记本</h2>
          <span class="sub-text">记录每一个当下的自己</span>
        </div>
        <div class="placeholder" style="width: 100px;"></div>
      </div>

      <div class="glass-card editor-card slide-in-down">
        <h3>今天感觉怎么样？</h3>
        
        <div class="mood-selector">
          <div 
            v-for="mood in moods" 
            :key="mood.value"
            class="mood-item"
            :class="{ active: currentMood === mood.value }"
            @click="currentMood = mood.value"
          >
            <span class="emoji">{{ mood.icon }}</span>
            <span class="label">{{ mood.label }}</span>
          </div>
        </div>

        <textarea 
          v-model="diaryContent" 
          placeholder="写下此刻的想法..." 
          class="diary-input"
        ></textarea>

        <button class="save-btn" @click="saveDiary" :disabled="!diaryContent.trim() || loading">
          {{ loading ? '云端同步中...' : '✨ 封存今日记忆' }}
        </button>
      </div>

      <div class="history-list slide-in-up">
        <h3 class="section-title">往昔足迹</h3>
        
        <div v-if="diaries.length === 0" class="empty-state">
          <span class="empty-icon">🍃</span>
          <p>还没有日记哦，写下第一篇吧</p>
        </div>

        <div v-else class="diary-grid">
          <div v-for="diary in diaries" :key="diary.id" class="glass-card diary-item">
            <div class="diary-header">
              <div class="meta-info">
                <span class="diary-mood">{{ getMoodIcon(diary.mood) }}</span>
                <span class="diary-date">{{ formatDate(diary.created_at) }}</span>
              </div>
              <button class="del-btn" @click="openDeleteModal(diary.id)">
                <span class="del-icon">🗑️</span> 删除
              </button>
            </div>
            <p class="diary-content">{{ diary.content }}</p>
          </div>
        </div>
      </div>

    </div>

    <Transition name="toast-fade">
      <div v-if="showSaveSuccess" class="custom-success-toast">
        <div class="toast-icon-box">✨</div>
        <div class="toast-text">
          <h4>保存成功</h4>
          <p>这段记忆已安全封存于云端档案</p>
        </div>
      </div>
    </Transition>

    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showDeleteModal" class="custom-modal-overlay" @click.self="showDeleteModal = false">
          <div class="custom-modal">
            <div class="modal-alert-icon">⚠️</div>
            <h3>确认删除记录？</h3>
            <p>这段心路历程一旦抹去将无法恢复，确定要删除吗？</p>
            <div class="modal-actions">
              <button class="modal-btn cancel" @click="showDeleteModal = false">再想想</button>
              <button class="modal-btn confirm" @click="executeDelete" :disabled="isDeleting">
                {{ isDeleting ? '删除中...' : '确定删除' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { authStore } from '../store.js';

// 基础数据字典
const moods = [
  { value: 'happy', icon: '😄', label: '开心' },
  { value: 'calm', icon: '😌', label: '平静' },
  { value: 'anxious', icon: '😰', label: '焦虑' },
  { value: 'sad', icon: '😔', label: '难过' },
  { value: 'angry', icon: '😠', label: '生气' },
];

// 状态管理
const currentMood = ref('calm');
const diaryContent = ref('');
const diaries = ref([]);
const loading = ref(false);

// ✨ 新增的弹窗控制状态
const showSaveSuccess = ref(false);
const showDeleteModal = ref(false);
const targetDeleteId = ref(null);
const isDeleting = ref(false);

const API_BASE_URL = 'http://localhost:8080/api/diaries';
const getUserId = () => authStore.user_id || localStorage.getItem('user_id');

// 1. 加载日记
const fetchDiaries = async () => {
  const userId = getUserId();
  if (!userId) return;
  try {
    const res = await fetch(`${API_BASE_URL}?user_id=${userId}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    if (data.success) {
      diaries.value = data.diaries;
    }
  } catch (error) {
    console.error("加载失败:", error);
  }
};

// 2. 升级版保存逻辑 (触发动画 Toast)
const saveDiary = async () => {
  if (!diaryContent.value.trim()) return;
  const userId = getUserId();
  
  loading.value = true;
  try {
    const res = await fetch(API_BASE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        mood: currentMood.value,
        content: diaryContent.value
      })
    });
    
    const data = await res.json();
    if (data.success) {
      diaries.value.unshift(data.new_diary);
      diaryContent.value = '';
      currentMood.value = 'calm';
      
      // 触发华丽的 Toast
      showSaveSuccess.value = true;
      setTimeout(() => { showSaveSuccess.value = false; }, 3000);
    } else {
      alert(data.message || '保存失败');
    }
  } catch (error) {
    alert('网络连接失败');
  } finally {
    loading.value = false;
  }
};

// 3. 升级版删除逻辑 (触发 Modal)
const openDeleteModal = (id) => {
  targetDeleteId.value = id;
  showDeleteModal.value = true;
};

const executeDelete = async () => {
  if (!targetDeleteId.value) return;
  isDeleting.value = true;
  
  try {
    const res = await fetch(`${API_BASE_URL}/${targetDeleteId.value}`, { method: 'DELETE' });
    const data = await res.json();
    
    if (data.success) {
      diaries.value = diaries.value.filter(d => d.id !== targetDeleteId.value);
      showDeleteModal.value = false;
      targetDeleteId.value = null;
    } else {
      alert('删除失败');
    }
  } catch (error) {
    alert('网络错误');
  } finally {
    isDeleting.value = false;
  }
};

onMounted(() => {
  fetchDiaries();
});

const getMoodIcon = (val) => moods.find(m => m.value === val)?.icon || '😐';

const formatDate = (iso) => {
  try {
    const d = new Date(iso);
    return `${d.getMonth()+1}月${d.getDate()}日 ${d.getHours()}:${d.getMinutes().toString().padStart(2,'0')}`;
  } catch (e) { return ''; }
};
</script>

<style scoped>
/* 原有基础样式保持不变 */

.content-wrapper { max-width: 800px; margin: 0 auto; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; position: relative; }
.title-area { text-align: center; }
.header h2 { margin: 0; color: #1d1d1f; font-size: 24px; font-weight: 700; letter-spacing: 0.5px; }
.sub-text { font-size: 13px; color: #86868b; margin-top: 4px; display: block; }

.glass-btn {
  display: flex; align-items: center; gap: 6px; padding: 10px 20px;
  background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px); border-radius: 30px; color: #1d1d1f; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.glass-btn:hover { background: #fff; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); color: #0071e3; }

.glass-card {
  background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 24px; padding: 30px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.04); transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.editor-card { margin-bottom: 40px; }
.editor-card h3 { margin: 0 0 24px 0; color: #1d1d1f; font-size: 18px; font-weight: 600; }

.mood-selector { display: flex; gap: 15px; margin-bottom: 24px; flex-wrap: wrap; }
.mood-item {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 12px 20px; border-radius: 16px; cursor: pointer;
  background: #f5f5f7; transition: all 0.2s; border: 2px solid transparent;
}
.mood-item:hover { transform: translateY(-3px); background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.mood-item.active { border-color: #0071e3; background: rgba(0, 113, 227, 0.08); }
.mood-item .emoji { font-size: 28px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.mood-item .label { font-size: 13px; color: #1d1d1f; font-weight: 500; }

.diary-input {
  width: 100%; height: 140px; border-radius: 16px; border: 1px solid #e5e5ea;
  background: #fff; padding: 20px; font-size: 16px; color: #1d1d1f;
  resize: vertical; outline: none; transition: all 0.3s; box-sizing: border-box;
}
.diary-input:focus { border-color: #0071e3; box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15); }

.save-btn {
  width: 100%; padding: 16px; background: linear-gradient(135deg, #0071e3 0%, #4facfe 100%);
  color: white; border: none; border-radius: 16px; font-weight: 600; font-size: 16px; cursor: pointer;
  transition: all 0.3s; margin-top: 20px; box-shadow: 0 8px 20px rgba(0, 113, 227, 0.25);
}
.save-btn:disabled { background: #a1cffd; box-shadow: none; cursor: not-allowed; }
.save-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(0, 113, 227, 0.35); }

.section-title { margin-bottom: 24px; color: #86868b; font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.diary-grid { display: grid; gap: 24px; }
.diary-item:hover { transform: translateY(-4px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }

.diary-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0; }
.meta-info { display: flex; align-items: center; gap: 12px; }
.diary-mood { font-size: 28px; }
.diary-date { font-size: 14px; color: #86868b; font-weight: 500; }
.diary-content { font-size: 16px; color: #333; line-height: 1.7; white-space: pre-wrap; margin: 0; }

/* 升级版：删除按钮样式 */
.del-btn { 
  display: flex; align-items: center; gap: 4px; background: rgba(255, 59, 48, 0.1); 
  border: none; color: #ff3b30; font-size: 13px; font-weight: 600; padding: 6px 12px; 
  border-radius: 12px; cursor: pointer; transition: all 0.2s; 
}
.del-btn:hover { background: #ff3b30; color: #fff; }
.del-icon { font-size: 14px; }

/* ==================== ✨ 新增：全局弹窗与交互 ==================== */

/* 保存成功 Toast */
.custom-success-toast {
  position: fixed; top: 40px; left: 50%; transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 20px;
  padding: 16px 24px; display: flex; align-items: center; gap: 16px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1); z-index: 9999;
}
.toast-icon-box { background: #34c759; color: white; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-size: 20px; }
.toast-text h4 { margin: 0 0 4px 0; color: #1d1d1f; font-size: 15px; font-weight: 700; }
.toast-text p { margin: 0; color: #86868b; font-size: 13px; }

/* 删除确认 Modal */
.custom-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(8px);
  z-index: 9999; display: flex; align-items: center; justify-content: center;
}
.custom-modal {
  background: #fff; width: 90%; max-width: 360px; border-radius: 24px;
  padding: 32px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.2);
  animation: modal-pop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-alert-icon { font-size: 48px; margin-bottom: 16px; filter: drop-shadow(0 4px 8px rgba(255, 59, 48, 0.2)); }
.custom-modal h3 { margin: 0 0 12px 0; color: #1d1d1f; font-size: 20px; font-weight: 700; }
.custom-modal p { color: #86868b; font-size: 14px; line-height: 1.6; margin-bottom: 32px; }

.modal-actions { display: flex; gap: 12px; }
.modal-btn { flex: 1; padding: 14px; border-radius: 14px; font-size: 15px; font-weight: 600; border: none; cursor: pointer; transition: 0.2s; }
.modal-btn.cancel { background: #f5f5f7; color: #1d1d1f; }
.modal-btn.cancel:hover { background: #e5e5ea; }
.modal-btn.confirm { background: #ff3b30; color: white; box-shadow: 0 4px 12px rgba(255, 59, 48, 0.3); }
.modal-btn.confirm:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255, 59, 48, 0.4); }
.modal-btn.confirm:disabled { opacity: 0.7; cursor: not-allowed; }

/* 动画过渡 */
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

@keyframes modal-pop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.slide-in-down { animation: slideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-in-up { animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideDown { from { opacity: 0; transform: translateY(-30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
</style>
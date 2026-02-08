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
          {{ loading ? '保存中...' : '✨ 保存记录' }}
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
              
              <div class="delete-action">
                <div v-if="deletingId === diary.id" class="confirm-box">
                  <button class="confirm-btn" @click="deleteDiary(diary.id)">确定?</button>
                  <button class="cancel-btn" @click="deletingId = null">取消</button>
                </div>
                <button v-else class="del-btn" @click="deletingId = diary.id">删除</button>
              </div>
            </div>
            <p class="diary-content">{{ diary.content }}</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { authStore } from '../store.js';

// 引入 Toast
let showToast = (msg, type) => alert(msg);
try {
  import('@/utils/toast').then(module => { if (module && module.showToast) showToast = module.showToast; });
} catch (e) {}

const moods = [
  { value: 'happy', icon: '😄', label: '开心' },
  { value: 'calm', icon: '😌', label: '平静' },
  { value: 'anxious', icon: '😰', label: '焦虑' },
  { value: 'sad', icon: '😔', label: '难过' },
  { value: 'angry', icon: '😠', label: '生气' },
];

const currentMood = ref('calm');
const diaryContent = ref('');
const diaries = ref([]);
const deletingId = ref(null);
const loading = ref(false);

// 提取后端地址常量，方便以后修改
// ✨✨✨ 修改点：端口改为 8080 ✨✨✨
const API_BASE_URL = 'http://localhost:8080/api/diaries';

const getUserId = () => authStore.user_id || localStorage.getItem('user_id');

// 2. 加载日记 (GET)
const fetchDiaries = async () => {
  const userId = getUserId();
  if (!userId) return;

  try {
    // ✨✨✨ 使用 8080 端口 ✨✨✨
    const res = await fetch(`${API_BASE_URL}?user_id=${userId}`);
    // 如果后端没启动，这里会直接抛出 TypeError
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    
    const data = await res.json();
    if (data.success) {
      diaries.value = data.diaries;
    }
  } catch (error) {
    console.error("加载失败:", error);
    // 只有在真的连不上时才提示
    // showToast("加载日记失败，请确认后端已启动", "error");
  }
};

// 3. 保存日记 (POST)
const saveDiary = async () => {
  if (!diaryContent.value.trim()) return;
  const userId = getUserId();
  
  loading.value = true;
  try {
    // ✨✨✨ 使用 8080 端口 ✨✨✨
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
      showToast('日记已保存至云端 ☁️', 'success');
    } else {
      showToast(data.message || '保存失败', 'error');
    }
  } catch (error) {
    showToast('网络连接失败 (8080)', 'error');
  } finally {
    loading.value = false;
  }
};

// 4. 删除日记 (DELETE)
const deleteDiary = async (id) => {
  try {
    // ✨✨✨ 使用 8080 端口 ✨✨✨
    const res = await fetch(`${API_BASE_URL}/${id}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    
    if (data.success) {
      diaries.value = diaries.value.filter(d => d.id !== id);
      deletingId.value = null;
      showToast('记录已删除 🗑️', 'success');
    } else {
      showToast('删除失败', 'error');
    }
  } catch (error) {
    showToast('网络错误', 'error');
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
.page-container {
  min-height: 100%; position: relative; overflow-y: auto; padding: 40px 20px;
}
.content-wrapper { max-width: 800px; margin: 0 auto; }

.header { 
  display: flex; justify-content: space-between; align-items: center; 
  margin-bottom: 30px; position: relative;
}
.title-area { text-align: center; }
.header h2 { margin: 0; color: var(--text-main); font-size: 24px; letter-spacing: 1px; }
.sub-text { font-size: 13px; color: #888; margin-top: 4px; display: block; }

.glass-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 30px;
  color: #555; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}
.glass-btn:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateX(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  color: var(--primary-color);
}
.glass-btn .icon { font-size: 16px; line-height: 1; }

.glass-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 20px; padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.05);
}
.editor-card { margin-bottom: 40px; }
.editor-card h3 { margin: 0 0 20px 0; color: #444; font-size: 18px; }

.mood-selector { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
.mood-item {
  display: flex; flex-direction: column; align-items: center; gap: 5px;
  padding: 10px 15px; border-radius: 12px; cursor: pointer;
  background: rgba(255,255,255,0.5); transition: 0.2s; border: 2px solid transparent;
}
.mood-item:hover { transform: translateY(-3px); background: #fff; }
.mood-item.active { border-color: var(--primary-color); background: rgba(var(--primary-rgb), 0.1); }
.mood-item .emoji { font-size: 24px; }
.mood-item .label { font-size: 12px; color: #666; }

.diary-input {
  width: 100%; height: 120px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.1);
  background: rgba(255,255,255,0.5); padding: 15px; font-size: 15px;
  resize: vertical; outline: none; transition: 0.3s;
  font-family: inherit; margin-bottom: 15px;
}
.diary-input:focus { background: #fff; border-color: var(--primary-color); }

.save-btn {
  width: 100%; padding: 12px; background: var(--primary-gradient);
  color: white; border: none; border-radius: 12px; font-weight: 600; cursor: pointer;
  transition: 0.2s;
}
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.save-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(var(--primary-rgb), 0.3); }

.section-title { margin-bottom: 20px; color: #666; font-size: 16px; border-left: 4px solid var(--primary-color); padding-left: 10px; }
.diary-grid { display: grid; gap: 20px; }
.diary-item { position: relative; transition: 0.3s; }
.diary-item:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); }

.diary-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px dashed rgba(0,0,0,0.1); }
.meta-info { display: flex; align-items: center; gap: 8px; }
.diary-mood { font-size: 24px; }
.diary-date { font-size: 13px; color: #999; }
.diary-content { font-size: 15px; color: #444; line-height: 1.6; white-space: pre-wrap; margin: 0; }

.del-btn { background: none; border: none; color: #ff4d4f; font-size: 12px; cursor: pointer; opacity: 0.6; transition: 0.2s; }
.del-btn:hover { opacity: 1; text-decoration: underline; }

.confirm-box { display: flex; gap: 8px; }
.confirm-btn { background: #ff4d4f; color: white; border: none; padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer; }
.cancel-btn { background: #ddd; color: #666; border: none; padding: 2px 8px; border-radius: 4px; font-size: 12px; cursor: pointer; }

.empty-state { text-align: center; color: #999; padding: 40px; display: flex; flex-direction: column; align-items: center; }
.empty-icon { font-size: 40px; margin-bottom: 10px; opacity: 0.5; }

.slide-in-down { animation: slideDown 0.6s ease; }
.slide-in-up { animation: slideUp 0.6s ease; }
@keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
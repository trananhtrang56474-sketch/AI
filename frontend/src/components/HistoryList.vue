<template>
  <div class="history-list-container">
    <ul class="list">
      <li 
        v-for="item in historyItems" 
        :key="item.id" 
        class="history-item"
        :class="{ 'active': isCurrentChat(item.id) }"
        @click="loadChat(item.id)"
      >
        <svg class="item-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
        </svg>
        
        <span class="item-title">{{ item.title }}</span>
      </li>
    </ul>
    
    <div v-if="historyItems.length === 0" class="empty-history">
      暂无历史记录
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute(); // 用于获取当前路由参数

// --- 示例数据 ---
const historyItems = ref([
  { id: '1', title: '关于考前焦虑的对话' },
  { id: '2', title: '昨天的情绪日志' },
  { id: '3', title: '关于人际关系的讨论' },
  { id: '4', title: '为什么我总是感到疲惫？' },
  { id: '5', title: '工作压力缓解建议' },
]);
// --- 示例数据结束 ---

// 判断是否是当前打开的聊天
const isCurrentChat = (id) => {
  // 假设路由是 /chat/:id
  return route.name === 'ChatWithId' && route.params.id === id;
};

const loadChat = (id) => {
  router.push({ name: 'ChatWithId', params: { id } });
};
</script>

<style scoped>
.history-list-container {
  width: 100%;
}

.list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 240px; /* 限制高度 */
  overflow-y: auto;  /* 允许滚动 */
  
  /* 增加右侧内边距，防止滚动条遮挡文字 */
  padding-right: 4px; 
}

/* 滚动条美化 */
.list::-webkit-scrollbar {
  width: 4px;
}
.list::-webkit-scrollbar-track {
  background: transparent;
}
.list::-webkit-scrollbar-thumb {
  background-color: #e0e0e0;
  border-radius: 4px;
}
.list::-webkit-scrollbar-thumb:hover {
  background-color: #ccc;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 8px 10px; /* 稍微紧凑一点 */
  margin-bottom: 4px;
  font-size: 13px;
  color: #666;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  /* 边框为了高亮时更清晰 */
  border: 1px solid transparent; 
}

.item-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* 文字超长显示省略号 */
  flex: 1;
}

/* 悬停效果 */
.history-item:hover {
  background-color: #f5f7fa;
  color: #333;
}

/* 选中高亮状态 */
.history-item.active {
  background-color: #e6f7ff; /* 浅蓝背景 */
  color: #1890ff; /* 蓝色文字 */
  font-weight: 500;
}

/* 图标样式 */
.item-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  flex-shrink: 0;
  color: #999;
  transition: color 0.2s;
}

.history-item:hover .item-icon {
  color: #666;
}

.history-item.active .item-icon {
  color: #1890ff; /* 选中时图标变蓝 */
}

.empty-history {
  font-size: 12px;
  color: #999;
  padding: 10px;
  text-align: center;
}
</style>
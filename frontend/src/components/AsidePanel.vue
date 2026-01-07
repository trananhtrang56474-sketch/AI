<template>
  <div class="aside-panel">
    
    <div class="aside-card emergency-card">
      <div class="card-header">
        <div class="icon-box alert-icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3>紧急帮助</h3>
      </div>
      <p class="emergency-text">如果你正处于危机中，请不要独自承受，立即寻求专业帮助。</p>
      <a href="tel:12345678" class="emergency-btn">
        <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
        </svg>
        拨打心理援助热线
      </a>
    </div>

    <div class="aside-card">
      <div class="section-header">
        <div class="title-group">
          <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h3>健康小贴士</h3>
        </div>
        <a href="#" class="more-link">更多</a>
      </div>
      <ul class="info-list">
        <li>
          <a href="#">如何应对突如其来的焦虑？</a>
        </li>
        <li>
          <a href="#">正念呼吸的 5 个简单步骤</a>
        </li>
        <li>
          <a href="#">建立积极的睡眠习惯</a>
        </li>
      </ul>
    </div>
    
    <div class="aside-card">
      <div class="section-header">
        <div class="title-group">
          <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3>使用教程</h3>
        </div>
        <a href="#" class="more-link">更多</a>
      </div>
      <ul class="info-list">
        <li><a href="#">如何理解我的情绪图表？</a></li>
        <li><a href="#">如何与 AI 进行有效的对话？</a></li>
      </ul>
    </div>

    <div class="aside-card">
      <div class="section-header">
        <div class="title-group">
          <svg class="section-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <h3>资源链接</h3>
        </div>
      </div>
      <ul class="info-list">
        <li><a href="#">推荐阅读：《蛤蟆先生去看心理医生》</a></li>
        <li><a href="#">推荐网站：中国心理卫生协会</a></li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 目前不需要脚本
</script>

<style scoped>
.aside-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* 增加底部 padding，防止滚动到底部时贴边 */
  padding-bottom: 20px; 
}

/* 通用卡片样式 */
.aside-card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); /* 与 Home 卡片一致 */
  border: 1px solid rgba(0,0,0,0.02);
  transition: transform 0.2s ease;
}

.aside-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
}

/* 标题栏 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f5f5f5;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-group h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.section-icon {
  width: 18px;
  height: 18px;
  color: #1890ff;
}

.more-link {
  font-size: 12px;
  color: #999;
  text-decoration: none;
  transition: color 0.2s;
}
.more-link:hover {
  color: #1890ff;
}

/* 列表样式 */
.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-list li {
  margin-bottom: 10px;
  position: relative;
  padding-left: 12px;
}

/* 自定义列表圆点 */
.info-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 8px;
  width: 4px;
  height: 4px;
  background-color: #d9d9d9;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.info-list li:hover::before {
  background-color: #1890ff;
}

.info-list a {
  text-decoration: none;
  color: #555;
  font-size: 13px;
  line-height: 1.5;
  transition: color 0.2s;
  display: block; /* 增加点击区域 */
}

.info-list a:hover {
  color: #1890ff;
}

/* -------------------
   紧急卡片特别样式
   ------------------- */
.emergency-card {
  background: linear-gradient(135deg, #fff1f0 0%, #fff 100%);
  border: 1px solid #ffccc7;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.1);
}

.emergency-card .card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.emergency-card h3 {
  margin: 0;
  font-size: 16px;
  color: #cf1322;
  font-weight: 700;
}

.alert-icon {
  color: #cf1322;
  width: 20px;
  height: 20px;
}

.emergency-text {
  font-size: 13px;
  color: #5c0011;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.emergency-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  background: linear-gradient(to right, #ff4d4f, #f5222d);
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  box-shadow: 0 4px 10px rgba(245, 34, 45, 0.3);
  transition: all 0.2s;
}

.emergency-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(245, 34, 45, 0.4);
  filter: brightness(1.1);
}

.btn-icon {
  width: 16px;
  height: 16px;
}
</style>
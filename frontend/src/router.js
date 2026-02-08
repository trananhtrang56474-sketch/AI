import { createRouter, createWebHistory } from 'vue-router';

// 1. 导入页面组件
import MainLayout from './layouts/MainLayout.vue';
import LandingPage from './pages/LandingPage.vue'; 
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';
import Home from './pages/Home.vue';
import MeditationPage from './pages/MeditationPage.vue';
import ArticlePage from './pages/ArticlePage.vue';

// ✨✨✨ 1. 导入日记页面 (确保你已经把组件移动到了 pages 目录并改名了) ✨✨✨
import MoodDiaryPage from './pages/MoodDiaryPage.vue';

// 2. 定义路由守卫 (检查是否登录)
const requireAuth = (to, from, next) => {
  const userId = localStorage.getItem('user_id');
  if (!userId) {
    // 没登录 -> 踢去登录页
    next('/login');
  } else {
    // 登录了 -> 放行
    next();
  }
};

const routes = [
  // ---------------------------------------------------------
  // 1. 落地页 (第一入口，公开)
  // ---------------------------------------------------------
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },

  // ---------------------------------------------------------
  // 2. 登录/注册页 (公开)
  // ---------------------------------------------------------
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/register',
    name: 'Register',
    redirect: to => {
      // 传递 mode='register' 让 LoginPage 自动切换界面
      return { path: '/login', query: { mode: 'register' } }
    }
  },

  // ---------------------------------------------------------
  // 3. 核心功能区 (受保护，需要登录)
  // ---------------------------------------------------------
  {
    path: '/', 
    component: MainLayout,
    beforeEnter: requireAuth, // 🔥 门神：没登录不准进
    children: [
      {
        path: 'home', 
        name: 'Home',
        component: Home
      },
      {
        path: 'chat', 
        name: 'Chat',
        component: ChatPage
      },
      
      // 🧘 冥想室
      {
        path: 'meditation',
        name: 'Meditation',
        component: MeditationPage
      },
      
      // 📖 文章详情页
      {
        path: 'article/:id',
        name: 'Article',
        component: ArticlePage
      },

      // ✨✨✨ 2. 新增路由：情绪日记 ✨✨✨
      {
        path: 'diary',
        name: 'MoodDiary',
        component: MoodDiaryPage
      }
    ]
  }
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 切换页面时自动滚回顶部
    return savedPosition || { top: 0 };
  },
});

export default router;
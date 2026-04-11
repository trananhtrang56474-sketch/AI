import { createRouter, createWebHistory } from 'vue-router';

// 1. 导入页面组件
import MainLayout from './layouts/MainLayout.vue';
import LandingPage from './pages/LandingPage.vue'; 
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';
import Home from './pages/Home.vue';
import MeditationPage from './pages/MeditationPage.vue';
import ArticlePage from './pages/ArticlePage.vue';

// 导入日记页面
import MoodDiaryPage from './pages/MoodDiaryPage.vue';

// ✨✨✨ 新增 1：导入心理报告页面 (ResourcesPage.vue) ✨✨✨
import ResourcesPage from './pages/ResourcesPage.vue';


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

      // 情绪日记
      {
        path: 'diary',
        name: 'MoodDiary',
        component: MoodDiaryPage
      },

      // ✨✨✨ 新增 2：注册心理报告路由 ✨✨✨
      {
        path: 'report',
        name: 'Report',
        component: ResourcesPage
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
import { createRouter, createWebHistory } from 'vue-router';

// 1. 导入页面组件
import MainLayout from './layouts/MainLayout.vue';
import LandingPage from './pages/LandingPage.vue'; // 确保你之前没删这个文件
import LoginPage from './pages/LoginPage.vue';
import ChatPage from './pages/ChatPage.vue';
import Home from './pages/Home.vue';

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
  // 访问域名根目录时，显示这个漂亮的介绍页
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

  // ---------------------------------------------------------
  // 3. 核心功能区 (受保护，需要登录)
  // 这里利用了 Vue Router 的匹配机制：
  // 只有访问 /home 或 /chat 时才会匹配到这里
  // ---------------------------------------------------------
  {
    path: '/', 
    component: MainLayout,
    beforeEnter: requireAuth, // 🔥 门神：没登录不准进这里面的子路由
    children: [
      {
        path: 'home', // 对应 URL: /home
        name: 'Home',
        component: Home
      },
      {
        path: 'chat', // 对应 URL: /chat
        name: 'Chat',
        component: ChatPage
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

export default router;
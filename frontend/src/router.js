import { createRouter, createWebHistory } from 'vue-router';
// 导入布局
import MainLayout from './layouts/MainLayout.vue';
// 导入页面
import Home from './pages/Home.vue';
import ChatPage from './pages/ChatPage.vue';
// 1. 导入新的着陆页组件
import LandingPage from './pages/LandingPage.vue'; 

const routes = [
  // ---------------------------------------------------------
  // 路由 1: 首页 (着陆页)
  // 访问 http://localhost:5173/ 时显示这个，没有侧边栏
  // ---------------------------------------------------------
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },

  // ---------------------------------------------------------
  // 路由 2: 应用主区域 (带 Sidebar 的三栏布局)
  // 访问 /home 或 /chat 时匹配这里
  // ---------------------------------------------------------
  {
    // 这里 path 依然写 '/'，但在 Vue Router 中，如果上面那个匹配了精确的 '/'，
    // 这里就会主要负责匹配 children (子路由)
    path: '/', 
    component: MainLayout,
    // 注意：我删掉了 redirect: '/home'，因为现在根路径要显示 LandingPage
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
      },
      {
        path: 'chat/:id', // 对应 URL: /chat/123
        name: 'ChatWithId',
        component: ChatPage,
        props: true
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  //哪怕页面切换了，为了体验好，我们可以让滚动条自动滚回顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

export default router;
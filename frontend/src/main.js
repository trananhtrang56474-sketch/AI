import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // 引入路由

import './assets/main.css';
import './assets/styles.css';

createApp(App)
  .use(router)  // 必须挂载路由
  .mount('#app');

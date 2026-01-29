import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// 🛑 注释掉旧的样式文件，防止它们覆盖我们的新设计
// import './assets/main.css';
// import './assets/styles.css';

const app = createApp(App);

app.use(router);
app.mount('#app');
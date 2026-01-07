import { reactive } from 'vue';

export const authStore = reactive({
  // 初始化时检查 localStorage
  isLoggedIn: !!localStorage.getItem('user_id'),
  username: localStorage.getItem('username') || '',

  // 登录动作
  login(userId, name) {
    this.isLoggedIn = true;
    this.username = name;
    localStorage.setItem('user_id', userId);
    localStorage.setItem('username', name);
  },

  // 退出动作
  logout() {
    this.isLoggedIn = false;
    this.username = '';
    localStorage.removeItem('user_id');
    localStorage.removeItem('username');
  }
});
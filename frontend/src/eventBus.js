// src/eventBus.js
import { reactive } from 'vue';

export const bus = reactive({
  refreshSessions: false,
  emitRefresh() {
    this.refreshSessions = !this.refreshSessions;
  }
});
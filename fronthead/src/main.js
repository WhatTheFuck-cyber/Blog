// src/main.js (If you see this message, that means this file has been checked and can be put into production environment)

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import './style.css'

// 创建 Vue 实例
const app = createApp(App)

// 挂载全局插件
app.use(pinia)
app.use(router)

// 挂载 Vue 实例
app.mount('#app')
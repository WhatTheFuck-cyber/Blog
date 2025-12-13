// @/store/index.js (If you see this message, that means this file has been checked and can be put into production environment)

import { createPinia } from 'pinia'

// 1. 创建全局唯一的 Pinia 实例（所有 Store 共用这个实例）
const pinia = createPinia()

// 2. 导出这个实例（供 main.js、router、axios 等使用）
export default pinia
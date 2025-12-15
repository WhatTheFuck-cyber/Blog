// ./ vite.config.js

// 导入Vite核心配置函数：提供TypeScript类型提示，规范配置格式
import { defineConfig } from 'vite'

// 导入Vue核心插件（必选）：让Vite能解析.vue单文件组件（template/script/style）
import vue from '@vitejs/plugin-vue'

// 导入Node内置路径模块：处理跨平台文件路径（如Windows的\和Linux的/）
import path from 'path'

// Vite配置导出：defineConfig包裹后可获得完整的配置提示
export default defineConfig({
  // ======================== 核心插件配置 ========================
  plugins: [vue()],    // 启用Vue插件（必选） 

  // ======================== 路径解析配置 ========================
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@assets': path.resolve(__dirname, 'src/assets'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@router': path.resolve(__dirname, 'src/router'),
      '@store': path.resolve(__dirname, 'src/store'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@views': path.resolve(__dirname, 'src/views'),
    },
    extensions: ['.vue', '.js'],
  },

  // ======================== 开发服务器配置 ========================
  server: {
    port: 7777,
    open: true,    // 启动Vite后自动打开浏览器
    host: 'localhost',//'0.0.0.0',
    proxy: {
      '/api': {
        target: 'https://localhost:8888',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },

  // ======================== 打包配置 ========================
  build: {
    sourcemap: false,    // 减小打包体积，避免源码泄露（生产环境禁用）
    rollupOptions: {
      output: {
        // 拆分第三方依赖，避免单文件体积过大（提升首屏加载速度）
        manualChunks: {
          // 拆分 Vue 生态核心库
          vue: ['vue', 'vue-router', 'pinia'],
          // 拆分 Axios
          axios: ['axios'],
          // 拆分 Element Plus（大型 UI 库）
          'element-plus': ['element-plus'],
          // 拆分 Markdown 相关库
          markdown: ['marked', 'highlight.js', 'md-editor-v3'],
        },
      },
    },
  }
})

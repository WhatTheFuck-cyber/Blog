<template>
  <!-- 根容器：Flex垂直布局，保证页面最小高度100vh，实现页脚固定在底部 -->
  <div class="app-container">
    <SidebarDrawer />
    <!-- 导航栏：粘性定位固定顶部，分左（导航链接）、中（搜索）、右（用户操作）三区 -->
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/app/about" class="nav-link">关于我们</router-link>
        <router-link to="/app/home" class="nav-link" exact-active-class="active-link">主页</router-link>
        <router-link to="/" class="nav-link" exact-active-class="active-link">开始</router-link>
      </div>

      <div class="search-container">
        <SearchBox 
          placeholder="搜索文章或作者..." 
          customClass="navbar-search"
          @search="handleSearch"
        />
      </div>

      <div class="nav-right">
        <router-link to="/app/login" class="auth-link" v-if="!userStore.isLoggedIn">登录</router-link>
        <router-link to="/app/register" class="auth-link" v-if="!userStore.isLoggedIn">注册</router-link>
        <router-link to="/userpage/userhome" class="user-info" v-if="userStore.isLoggedIn">欢迎回来，{{ userStore.username }}</router-link>
        <button @click="logout" class="logout-btn" v-if="userStore.isLoggedIn">登出</button>
      </div>
    </nav>

    <!-- 路由出口：渲染当前路由匹配的页面组件，占满剩余空间 -->
    <router-view class="main-content"></router-view>

    <!-- 页脚：自动填充当前年份，固定在页面底部 -->
    <div class="footer">
      <p>&copy; {{ new Date().getFullYear() }} 本博客由 github:WhatTheFuck-cyber 开发，保留所有权利</p>
    </div>
  </div>
</template>

<script setup>
/**
 * 全局布局组件（包含导航栏、内容区、页脚）
 * @description 实现全站通用布局：顶部粘性导航栏、中间自适应内容区、底部固定页脚
 * @feature 1. 导航栏根据登录状态展示不同操作项 2. 集成搜索组件并处理搜索跳转 3. 登出逻辑带容错兜底 4. 响应式适配小屏幕
 * @dependencies SearchBox组件、userStore（用户状态）、vue-router
 */
import { onMounted } from 'vue'
import { useRouter } from 'vue-router' 
import { useUserStore } from '@/store/user' 
import SearchBox from '@/components/SearchBox.vue'
import SidebarDrawer from '@/components/SidebarDrawer.vue'

const router = useRouter() // 路由实例
const userStore = useUserStore() // 用户状态实例

/**
 * 页面挂载时初始化登录状态
 * @description 恢复localStorage中存储的用户登录信息，避免页面刷新后登录态丢失
 * @returns {void}
 */
onMounted(() => {
  userStore.init()
})

/**
 * 处理用户登出逻辑
 * @description 调用userStore登出方法，跳转登录页；失败则清空本地存储并刷新页面
 * @returns {Promise<void>}
 * @feature 路由跳转失败时兜底刷新，保证登出状态生效
 */
const logout = async () => {
  try {
    await userStore.logout() // 执行登出核心逻辑
    router.replace('/app/login').catch(err => {
      console.warn('路由跳转异常，兜底刷新：', err)
      window.location.href = '/app/login'
    })
  } catch (error) {
    console.error('登出失败：', error)
    localStorage.removeItem('user')
    window.location.reload()
  }
}

/**
 * 搜索回调处理函数
 * @param {Object} params - 搜索参数对象
 * @param {string} params.query - 搜索关键词
 * @param {Object} params.strategy - 搜索策略
 * @returns {void}
 * @description 接收搜索组件的参数，跳转到搜索结果页并传递查询参数
 */
const handleSearch = (params) => {
  router.push({
    name: 'search-results',
    query: {
      q: params.query,
      s: JSON.stringify(params.strategy)
    }
  })
}
</script>

<style scoped>
/* 
 * 全局布局样式总说明：
 * 1. 采用Flex布局实现页脚固定、内容自适应填充
 * 2. 导航栏粘性定位+响应式布局，小屏幕自动垂直排列
 * 3. 交互元素（按钮/链接）添加hover/active反馈，提升体验
 * 4. 核心优先级：布局稳定性 > 响应式适配 > 视觉交互
 */

/* 根容器：Flex垂直布局，保证最小高度占满视口，页脚自动固定底部 */
.app-container {
  display: flex; /* 启用Flex布局 */
  flex-direction: column; /* 垂直排列子元素 */
  min-height: 100vh; /* 最小高度铺满视口，防止内容不足时页脚上移 */
}

/* 导航栏：粘性定位顶部，Flex水平布局分三区，添加阴影提升层级 */
.navbar {
  display: flex; /* Flex布局实现子元素水平排列 */
  justify-content: space-between; /* 子元素两端对齐，中间留空 */
  align-items: center; /* 子元素垂直居中 */
  padding: 1rem 2rem; /* 内边距，保证内容与边框间距 */
  background-color: #fff; /* 白色背景，提升辨识度 */
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* 轻微阴影，区分内容区 */
  position: sticky; /* 粘性定位，滚动时固定在顶部 */
  top: 0; /* 粘性定位的顶部偏移量 */
  z-index: 999; /* 高z-index，防止被其他元素遮挡 */
  gap: 1rem; /* 子元素间距，防止挤压 */
}

/* 左侧导航区：Flex布局，不被挤压，保证链接间距 */
.nav-left {
  display: flex; /* Flex布局排列导航链接 */
  gap: 2rem; /* 链接之间的间距 */
  flex-shrink: 0; /* 禁止收缩，防止被中间搜索区挤压 */
}

/* 导航链接：统一样式，添加hover/激活态反馈 */
.nav-link {
  text-decoration: none; /* 清除默认下划线 */
  color: #2d3748; /* 默认文字颜色 */
  font-weight: 500; /* 文字加粗，提升可读性 */
  transition: color 0.2s; /* 颜色过渡动画，交互更丝滑 */
  display: inline-block; /* 确保点击区域完整 */
  padding: 0.5rem 0; /* 扩大点击热区 */
}

/* 激活态链接：文字变色+底部下划线，标识当前页 */
.active-link {
  color: #3498db; /* 激活态文字色（主题色） */
  border-bottom: 2px solid #3498db; /* 底部下划线，强化激活态 */
}

.nav-link:hover {
  color: #3498db; /* hover时文字变色（主题色） */
}

/* 搜索容器：占中间剩余空间，限制最大宽度防止挤压 */
.search-container {
  flex: 1; /* 占满中间剩余空间 */
  max-width: 400px; /* 最大宽度限制，避免过宽 */
  text-align: center; /* 内容居中 */
  color: #94a3b8; /* 占位文字颜色 */
  font-size: 0.9rem; /* 字体大小适配 */
}

.placeholder {
  cursor: default; /* 鼠标样式为默认，提示不可点击 */
}

/* 右侧用户操作区：Flex布局，不被挤压，优化元素间距 */
.nav-right {
  display: flex; /* Flex布局排列操作项 */
  align-items: center; /* 垂直居中 */
  gap: 1.5rem; /* 元素间距 */
  flex-shrink: 0; /* 禁止收缩，防止被挤压 */
}

/* 登录/注册链接：优化点击区域和hover样式 */
.auth-link {
  text-decoration: none; /* 清除默认下划线 */
  color: #3498db; /* 文字色（主题色） */
  font-weight: 500; /* 文字加粗 */
  display: inline-block; /* 确保点击区域完整 */
  padding: 0.5rem 0; /* 扩大点击热区 */
}

.auth-link:hover {
  text-decoration: underline; /* hover时下划线，提示可点击 */
}

/* 用户信息：优化样式和交互，防止文字换行 */
.user-info {
  color: #2d3748; /* 文字颜色 */
  font-size: 0.95rem; /* 字体大小 */
  white-space: nowrap; /* 禁止文字换行，防止挤压 */
  display: inline-flex; /* 对齐图标/文字 */
  align-items: center; /* 垂直居中 */
  padding: 0.4rem 0.8rem; /* 扩大点击热区 */
  border-radius: 8px; /* 圆角，提升视觉体验 */
  cursor: pointer; /* 鼠标手型，提示可点击 */
  text-decoration: none; /* 清除默认下划线 */
  font-weight: 500; /* 文字加粗 */
  transition: all 0.2s ease-in-out; /* 所有属性过渡动画 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* 轻微阴影，提升层次 */
}

.user-info:hover {
  color: #4299e1; /* hover文字色（主题色） */
  background-color: #f5fafe; /* hover背景色 */
  transform: translateY(-1px); /* 轻微上移，灵动效果 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); /* hover加深阴影 */
}

.user-info:active {
  transform: translateY(0); /* 点击时回归原位 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* 点击时还原阴影 */
}

/* 登出按钮：优化样式和交互反馈，禁止收缩 */
.logout-btn {
  padding: 0.5rem 1.2rem; /* 内边距，扩大点击热区 */
  border: none; /* 清除默认边框 */
  border-radius: 4px; /* 圆角 */
  background-color: #e74c3c; /* 背景色（警示色） */
  color: #fff; /* 文字白色 */
  cursor: pointer; /* 鼠标手型 */
  font-size: 0.95rem; /* 字体大小 */
  transition: all 0.2s; /* 过渡动画 */
  flex-shrink: 0; /* 禁止收缩 */
}

.logout-btn:hover {
  background-color: #c0392b; /* hover加深背景色 */
  color: #3498db; /* hover文字色（主题色） */
}

.logout-btn:active {
  transform: scale(0.98); /* 点击时轻微缩放，反馈效果 */
}

/* 主内容区：占满剩余空间，设置内边距 */
.main-content {
  flex: 1; /* 占满根容器剩余空间 */
  padding: 2rem; /* 内边距，保证内容与边框间距 */
}

/* 页脚：自动固定底部，深色背景，文字适配 */
.footer {
  text-align: center; /* 文字居中 */
  padding: 2rem; /* 内边距 */
  color: #e2e8f0; /* 文字颜色（浅灰） */
  font-size: 0.9rem; /* 字体大小 */
  border-top: 1px solid #e2e8f0; /* 顶部边框，区分内容区 */
  background-color: #2c3e50; /* 深色背景 */
  margin-top: auto; /* 自动顶到底部（Flex布局特性） */
}

/* 响应式适配：小屏幕（≤768px）下导航栏垂直布局 */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column; /* 垂直排列子元素 */
    gap: 1.5rem; /* 增大子元素间距 */
    padding: 1rem; /* 减少内边距 */
  }
  
  .nav-left, .nav-right {
    gap: 1.5rem; /* 增大间距 */
    width: 100%; /* 宽度铺满 */
    justify-content: center; /* 内容居中 */
  }

  .search-container {
    max-width: 100%; /* 搜索区宽度铺满 */
  }

  .main-content {
    padding: 1rem; /* 减少内容区内边距 */
  }
}

/* 导航栏搜索组件专属样式：限制最大宽度 */
.navbar-search {
  max-width: 400px; /* 搜索组件最大宽度 */
}
</style>
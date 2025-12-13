<template>
  <!-- 加载状态区块：复用userInfo Store的isLoading状态，展示加载动画+提示文案，提升用户等待感知 -->
  <div v-if="userInfoStore.isLoading" class="user-info-loading">
    <div class="loading-spinner"></div>
    <p>正在加载个人信息...</p>
  </div>

  <!-- 错误状态区块：复用userInfo Store的error状态，展示错误提示+重新加载按钮，便捷恢复操作 -->
  <div v-else-if="userInfoStore.error" class="user-info-error">
    <p>❌ {{ userInfoStore.error }}</p>
    <button class="reload-btn" @click="userInfoStore.fetchUserBasicInfo">重新加载</button>
  </div>

  <!-- 用户信息主体区块：非加载/非错误状态下展示，复用userInfo Store的用户核心信息 -->
  <div v-else class="user-info-container">
    <div class="user-base-info">
      <!-- 用户名：核心标识，突出展示 -->
      <h2 class="username">{{ userInfoStore.username }}</h2>
      <!-- 邮箱信息行：标签+值分离布局，提升可读性 -->
      <div class="info-row">
        <span class="label">邮箱：</span>
        <span class="value">{{ userInfoStore.email }}</span>
      </div>
      <!-- 账号状态：根据激活状态展示不同样式（已激活/未激活），视觉区分状态 -->
      <div class="info-row">
        <span class="label">账号状态：</span>
        <span class="value status-active" v-if="userInfoStore.is_activate">已激活</span>
        <span class="value status-inactive" v-else>未激活</span>
      </div>
      <!-- 激活时间：格式化展示，提升时间可读性 -->
      <div class="info-row">
        <span class="label">激活时间：</span>
        <span class="value">{{ formatTime(userInfoStore.activate_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 用户主页组件（精简版）
 * @description 基于userInfo Store实现的用户基本信息展示组件，核心功能为复用Store中的状态/方法，展示用户核心信息（用户名/邮箱/账号状态/激活时间），包含加载/错误/正常三种状态反馈，支持响应式适配和动画偏好兼容
 * @feature 1. 状态复用：直接使用userInfo Store的isLoading/error/用户信息等状态，避免重复定义 2. 方法复用：调用Store的fetchUserBasicInfo方法获取用户信息，统一数据管理 3. 状态反馈：加载动画/错误提示+重试/正常信息展示 4. 时间格式化：标准化时间展示格式（年-月-日 时:分） 5. 生命周期适配：onMounted+onActivated确保组件挂载/激活时均能获取数据（兼容keep-alive） 6. 响应式布局：适配移动端/PC端展示 7. 动画兼容：支持prefers-reduced-motion减少动画偏好
 * @dependencies 
 *  - useUserStore: 校验用户登录状态（isLoggedIn）
 *  - useUserInfoStore: 提供用户信息状态（isLoading/error/username/email等）和数据获取方法（fetchUserBasicInfo）
 */
// 导入Vue核心生命周期钩子：onMounted（组件挂载）、onActivated（组件激活，兼容keep-alive）
import { onMounted, onActivated } from 'vue'
// 导入用户登录状态Store：校验用户是否已登录
import { useUserStore } from '@/store/user'
// 导入用户信息Store：复用状态（加载/错误/用户信息）和方法（获取用户信息）
import { useUserInfoStore } from '@/store/userInfo'

/**
 * Store实例初始化
 * @type {ReturnType<typeof useUserStore>} userStore - 用户登录状态Store，用于校验登录状态
 * @type {ReturnType<typeof useUserInfoStore>} userInfoStore - 用户信息Store，提供状态和数据获取方法
 */
const userStore = useUserStore()
const userInfoStore = useUserInfoStore()

/**
 * 时间格式化工具函数
 * @description 将后端返回的时间字符串格式化为「年-月-日 时:分」的标准化格式，兼容空值处理
 * @param {string | undefined | null} timeStr - 原始时间字符串（如ISO格式）
 * @returns {string} 格式化后的时间字符串，空值返回"无"
 */
const formatTime = (timeStr) => {
  // 空值兜底：无时间字符串返回"无"
  if (!timeStr) return '无'
  const date = new Date(timeStr)
  // 补零处理：月份/日期/小时/分钟不足两位时补0，保证格式统一
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

/**
 * 数据获取逻辑：登录状态下调用Store方法获取用户基本信息
 * @description 封装统一的获取逻辑，避免重复代码，仅在用户已登录时执行，防止无效请求
 * @returns {void}
 */
const fetchData = () => {
  // 登录状态校验：仅已登录用户才获取个人信息
  if (userStore.isLoggedIn) {
    userInfoStore.fetchUserBasicInfo()
  }
}

/**
 * 生命周期钩子：组件挂载时执行数据获取
 * @description 首次加载组件时触发，保证初始数据加载
 */
onMounted(fetchData)

/**
 * 生命周期钩子：组件激活时执行数据获取（兼容keep-alive）
 * @description 当组件被keep-alive缓存时，再次激活（如路由切换返回）会触发，保证数据最新
 */
onActivated(fetchData)
</script>

<style scoped>
/* 
 * 用户主页样式总说明：
 * 1. 设计原则：轻量化（仅保留核心展示样式）+ 视觉分层（卡片/状态色区分）+ 响应式适配（移动端/PC端）+ 无障碍兼容（减少动画偏好）
 * 2. 视觉风格：毛玻璃卡片（backdrop-filter）+ 柔和阴影 + 状态色区分（已激活绿/未激活红），符合个人中心的简洁调性
 * 3. 交互体验：按钮hover反馈（上浮+变色）、加载动画、状态文字背景色强化
 * 4. 兼容性：支持prefers-reduced-motion（减少动画）、移动端布局自适应
 * 5. 层级关系：标签（label）固定宽度+加粗，值（value）自适应，保证布局整齐；状态文字带背景色，强化视觉焦点
 */

/* 加载状态样式：居中展示+加载动画+提示文案，弱化等待焦虑 */
.user-info-loading {
  text-align: center;
  padding: 4rem 0;
  color: #fff;
  font-size: 1.2rem;
}

/* 加载动画：旋转圆环，柔和边框（半透明+实心），提升等待感知 */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3); /* 半透明边框，弱化视觉冲击 */
  border-top: 4px solid #000; /* 实心顶部边框，形成旋转效果 */
  border-radius: 50%; /* 圆形动画 */
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite; /* 匀速旋转动画 */
}

/* 旋转动画关键帧：0-360度旋转，模拟加载状态 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态样式：居中展示+错误图标+提示文案，清晰反馈异常 */
.user-info-error {
  text-align: center;
  padding: 4rem 0;
  color: #000;
  font-size: 1.2rem;
}

/* 重新加载按钮：高对比度背景+hover反馈，便捷重试操作 */
.reload-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: rgba(249, 68, 2, 0.8); /* 橙红色背景，突出重试按钮 */
  border: none;
  border-radius: 6px; /* 圆角弱化硬朗感 */
  color: #2d3748;
  cursor: pointer;
  transition: all 0.2s ease; /* 过渡动画，保证hover流畅 */
}
/* 重新加载按钮hover：白色背景+轻微上浮，强化交互反馈 */
.reload-btn:hover {
  background-color: #fff;
  transform: translateY(-1px); /* 向上偏移1px，模拟上浮 */
}

/* 空状态样式（预留）：居中展示+提示文案，适配无数据场景 */
.user-info-empty {
  text-align: center;
  padding: 4rem 0;
  color: #fff;
  font-size: 1.2rem;
}

/* 登录链接样式（预留）：蓝色背景+hover反馈，引导未登录用户登录 */
.login-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: #4299e1; /* 蓝色主色调，符合链接认知 */
  color: #fff;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s ease;
}
.login-link:hover {
  background-color: #3182ce; /* 深色蓝，强化hover反馈 */
  transform: translateY(-1px);
}

/* 用户信息容器：网格布局+最大宽度限制，保证内容居中且不超宽 */
.user-info-container {
  display: grid;
  grid-template-columns: 1fr; /* 单列布局，适配核心信息展示 */
  gap: 2rem; /* 间距保证呼吸感 */
  max-width: 800px; /* 限制最大宽度，避免宽屏拉伸 */
  margin: 0 auto; /* 水平居中 */
  padding: 0 1rem; /* 左右内边距，适配窄屏 */
}

/* 用户基础信息卡片：毛玻璃效果+内边距+阴影，提升视觉层次感 */
.user-base-info {
  background-color: rgba(255, 255, 255, 0.9); /* 高透明度白色，兼顾可读性 */
  backdrop-filter: blur(12px); /* 毛玻璃效果，提升质感 */
  padding: 2.5rem;
  border-radius: 16px; /* 大圆角，弱化硬朗感 */
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08); /* 柔和阴影，提升悬浮感 */
}

/* 用户名样式：大号字体+底部边框，突出核心标识，区分信息区块 */
.username {
  margin: 0 0 2rem;
  color: #2d3748; /* 深灰色主色调，保证可读性 */
  font-size: 2rem;
  font-weight: 600; /* 加粗，突出用户名 */
  padding-bottom: 1rem;
  border-bottom: 1px solid #f5f5f5; /* 浅灰分隔线，弱化视觉分割 */
}

/* 信息行样式：弹性布局+两端对齐，标签固定宽度，值自适应，保证布局整齐 */
.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  color: #4a5568; /* 中灰色，次要信息色调 */
  font-size: 1.15rem;
  justify-content: space-between; /* 两端对齐，提升布局整洁度 */
}

/* 标签样式：固定宽度+加粗+主色调，区分标签和值，提升可读性 */
.label {
  flex: 0 0 90px; /* 固定宽度，保证标签对齐 */
  font-weight: 500;
  color: #2d3748;
  text-align: left;
  margin-right: 1.2rem; /* 右侧间距，避免和值重叠 */
}

/* 值样式：自适应宽度+换行处理，兼容长文本（如邮箱） */
.value {
  flex: 1;
  word-break: break-all; /* 强制换行，避免长文本溢出 */
}

/* 已激活状态样式：绿色系+背景色，视觉区分激活状态，强化正面反馈 */
.status-active {
  color: #48bb78; /* 绿色主色调，代表正常/激活 */
  font-weight: 500;
  padding: 0.3rem 0.8rem; /* 内边距形成胶囊样式 */
  background-color: #f0fdf4; /* 浅绿背景，强化状态 */
  border-radius: 8px;
}

/* 未激活状态样式：红色系+背景色，视觉区分未激活状态，强化警示 */
.status-inactive {
  color: #e53e3e; /* 红色主色调，代表异常/未激活 */
  font-weight: 500;
  padding: 0.3rem 0.8rem;
  background-color: #fef2f2; /* 浅红背景，强化状态 */
  border-radius: 8px;
}

/* 移动端适配（768px以下）：简化尺寸/间距，适配小屏触控体验 */
@media (max-width: 768px) {
  /* 容器：减小间距+全屏宽度，适配小屏 */
  .user-info-container {
    gap: 1.5rem;
    max-width: 100%;
  }

  /* 信息卡片：减小内边距，节省屏幕空间 */
  .user-base-info {
    padding: 1.8rem 1.5rem;
  }

  /* 用户名：减小字号+间距，适配小屏 */
  .username {
    font-size: 1.7rem;
    margin-bottom: 1.5rem;
  }

  /* 信息行：强制单行布局+减小字号，适配小屏 */
  .info-row {
    flex-direction: row !important; /* 强制单行，避免布局错乱 */
    font-size: 1.1rem;
  }

  /* 标签：减小固定宽度+间距，适配小屏 */
  .label {
    flex: 0 0 80px;
    margin-right: 0.8rem;
  }

  /* 状态文字：减小内边距+字号，适配小屏 */
  .status-active, .status-inactive {
    padding: 0.2rem 0.6rem;
    font-size: 1rem;
  }
}

/* 兼容减少动画偏好：尊重用户动画设置，关闭加载旋转动画 */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation: none; /* 关闭旋转动画，提升无障碍体验 */
  }
}
</style>
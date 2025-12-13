<template>
  <!-- 用户中心页面容器：包含雪花动画背景、侧边栏抽屉、动态导航页眉、透明主体区、页脚，支持路由/插槽双渲染 -->
  <div class="user-page-container">
    <SidebarDrawerUser />
    <EmailBaseFloatingWindow />
    <canvas ref="snowCanvas" class="snow-canvas"></canvas>
    
    <!-- 页眉导航栏：左侧固定导航 + 中间搜索框 + 右侧动态路由导航（根据当前页面循环展示） -->
    <header class="user-header">
      <nav class="nav-left">
        <router-link to="/" class="nav-link">开始</router-link>
        <router-link to="/app/home" class="nav-link">主页</router-link>
      </nav>
      <div class="search-container">
        <SearchBox />
      </div>
      <nav class="nav-right">
        <router-link 
          v-for="(item, index) in rightNavItems" 
          :key="index" 
          :to="item.to" 
          class="nav-link"
        >
          {{ item.text }}
        </router-link>
      </nav>
    </header>

    <!-- 主体区域：透明化设计不遮挡背景，支持具名插槽自定义内容（默认渲染router-view） -->
    <main class="user-main">
      <slot name="main-content"><router-view /></slot>
    </main>

    <!-- 页脚：版权信息，动态年份 -->
    <footer class="user-footer">
      &copy; {{ currentYear }} 本博客由 github:WhatTheFuck-cyber 开发，保留所有权利
    </footer>
  </div>
</template>

<script setup>
/**
 * 用户中心页面容器组件
 * @description 集成雪花动画背景、动态导航、侧边栏抽屉的用户中心通用容器，支持路由视图/插槽双渲染，适配多端响应式
 * @feature 1. 自适应性能的雪花动画背景（低配/移动端自动降量） 2. 基于当前路由的动态右侧导航（循环展示用户子页面） 3. 半透明毛玻璃页眉/页脚 4. 透明主体区不遮挡背景 5. 动画偏好适配（减少动画时隐藏雪花） 6. 具名插槽兼容原有router-view逻辑
 * @constant {number} SNOW_COUNT - 雪花默认数量（400），实际根据设备性能自适应调整
 * @constant {number} MAX_SPEED - 雪花最大下落速度（5），影响动画流畅度
 * @dependencies 
 *  - vue-router: 路由跳转/当前路由判断
 *  - SearchBox: 搜索组件
 *  - SidebarDrawerUser: 用户版侧边栏抽屉组件
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import SearchBox from '@/components/SearchBox.vue'
import SidebarDrawerUser from '@/components/SidebarDrawerUser.vue'
import { useRoute } from 'vue-router'
import EmailBaseFloatingWindow from '@/components/EmailBaseFloatingWindow'

// 路由实例与基础计算属性
const route = useRoute()
/**
 * 计算属性：当前年份（用于页脚版权信息）
 * @returns {number} 当前年份（4位数字）
 */
const currentYear = computed(() => new Date().getFullYear())

/**
 * 计算属性：动态右侧导航项
 * @description 根据当前路由路径循环展示用户子页面导航（避免显示当前页），非用户子页面显示默认导航
 * @returns {Array<Object>} 导航项列表 {text: string, to: string}
 */
const rightNavItems = computed(() => {
  const currentPath = route.path
  // 匹配"我的主页"页面：展示"我的足迹"+"我的发表"
  if (currentPath.includes('/userpage/userhome')) {
    return [
      { text: '我的足迹', to: '/userpage/usertrack' },
      { text: '我的发表', to: '/userpage/userpublish' }
    ]
  }
  // 匹配"我的足迹"页面：展示"我的主页"+"我的发表"
  else if (currentPath.includes('/userpage/usertrack')) {
    return [
      { text: '我的主页', to: '/userpage/userhome' },
      { text: '我的发表', to: '/userpage/userpublish' }
    ]
  }
  // 匹配"我的发表"页面：展示"我的主页"+"我的足迹"
  else if (currentPath.includes('/userpage/userpublish')) {
    return [
      { text: '我的主页', to: '/userpage/userhome' },
      { text: '我的足迹', to: '/userpage/usertrack' }
    ]
  }
  // 默认fallback：非用户子页面时显示完整导航
  else {
    return [
      { text: '我的足迹', to: '/userpage/usertrack' },
      { text: '我的发表', to: '/userpage/userpublish' }
    ]
  }
})

// 雪花动画相关状态与常量
const snowCanvas = ref(null) // Canvas DOM引用
let canvas = null // Canvas实例
let ctx = null // Canvas 2D上下文
let snowflakes = [] // 雪花对象数组
let animationId = null // 动画帧ID（用于取消动画）
const SNOW_COUNT = 400 // 雪花默认数量（高配设备）
const MAX_SPEED = 5 // 雪花最大下落速度

/**
 * 雪花对象类
 * @description 封装雪花的位置、尺寸、速度、旋转等属性，提供重置/更新/绘制方法
 */
class Snowflake {
  constructor() {
    this.reset() // 初始化时重置雪花状态
  }

  /**
   * 重置雪花状态（位置/尺寸/速度/透明度等）
   * @description 雪花超出可视区域时调用，重新生成雪花初始属性
   * @returns {void}
   */
  reset() {
    const depth = Math.random() // 雪花深度（影响尺寸/速度/透明度）
    this.x = Math.random() * canvas.width // 初始X坐标
    this.y = Math.random() * -canvas.height // 初始Y坐标（从顶部外开始）
    this.size = depth * 8 + 1 // 雪花尺寸（1-9px）
    this.speedY = depth * MAX_SPEED + 0.5 // 垂直下落速度（0.5-5.5px/帧）
    this.speedX = (Math.random() - 0.5) * depth * 2 // 水平偏移速度（-1到1px/帧）
    this.alpha = depth * 0.8 + 0.2 // 透明度（0.2-1）
    this.angle = Math.random() * Math.PI * 2 // 初始旋转角度
    this.rotateSpeed = (Math.random() - 0.5) * 0.02 // 旋转速度（-0.01到0.01rad/帧）
  }

  /**
   * 更新雪花状态（位置/角度）
   * @description 每一帧调用，更新雪花位置，超出底部时重置
   * @returns {void}
   */
  update() {
    this.y += this.speedY // 垂直下落
    this.x += this.speedX + Math.sin(this.angle) * 0.5 // 水平偏移+正弦波动
    this.angle += this.rotateSpeed // 更新旋转角度
    if (this.y > canvas.height) this.reset() // 超出底部重置
  }

  /**
   * 绘制雪花
   * @description 绘制圆形主体+6个分支，实现六角雪花效果
   * @returns {void}
   */
  draw() {
    ctx.save() // 保存画布状态
    ctx.globalAlpha = this.alpha // 设置透明度
    // 绘制雪花主体
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
    // 绘制6个分支（六角雪花）
    for (let i = 0; i < 6; i++) {
      const angle = (i * Math.PI / 3) + this.angle
      const x2 = this.x + Math.cos(angle) * this.size
      const y2 = this.y + Math.sin(angle) * this.size
      ctx.beginPath()
      ctx.arc(x2, y2, this.size / 4, 0, Math.PI * 2)
      ctx.fill()
    }
    ctx.restore() // 恢复画布状态
  }
}

/**
 * 获取自适应雪花数量
 * @description 根据设备类型（移动端）/性能（CPU核心数）调整雪花数量，降低低配设备性能消耗
 * @returns {number} 适配后的雪花数量（低配/移动端120，高配400）
 */
function getAdaptiveSnowCount() {
  // 检测是否为移动设备
  const isMobile = /Android|iPhone|iPad|iPod/.test(navigator.userAgent)
  // 检测是否为低配设备（CPU核心数<4）
  const isLowPerformance = navigator.hardwareConcurrency < 4
  if (isMobile || isLowPerformance) {
    return 120 // 低配/移动端降量
  }
  return SNOW_COUNT // 高配设备默认数量
}

/**
 * 初始化雪花数组
 * @description 根据自适应数量创建雪花对象，填充雪花数组
 * @returns {void}
 */
function initSnowflakes() {
  snowflakes = []
  const adaptiveCount = getAdaptiveSnowCount()
  for (let i = 0; i < adaptiveCount; i++) {
    snowflakes.push(new Snowflake())
  }
}

/**
 * 调整Canvas尺寸
 * @description 窗口大小变化时调用，适配全屏显示
 * @returns {void}
 */
function resizeCanvas() {
  if (!canvas) return
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

/**
 * 雪花动画主循环
 * @description 每一帧清空画布→更新所有雪花状态→绘制所有雪花→请求下一帧
 * @returns {void}
 */
function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height) // 清空画布
  snowflakes.forEach(flake => {
    flake.update() // 更新雪花状态
    flake.draw() // 绘制雪花
  })
  animationId = requestAnimationFrame(animate) // 请求下一帧
}

/**
 * 组件挂载钩子
 * @description 初始化Canvas→调整尺寸→创建雪花→启动动画→绑定窗口resize监听
 * @returns {void}
 */
onMounted(() => {
  canvas = snowCanvas.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  resizeCanvas()
  initSnowflakes()
  animate()
  window.addEventListener('resize', resizeCanvas)
})

/**
 * 组件卸载钩子
 * @description 取消动画帧→解绑resize监听→清空雪花数组，防止内存泄漏
 * @returns {void}
 */
onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', resizeCanvas)
  snowflakes = []
})
</script>

<style scoped>
/* 
 * 用户中心页面样式总说明：
 * 1. 全屏容器+固定背景图，雪花Canvas作为顶层视觉层（不拦截交互）
 * 2. 页眉/页脚采用半透明毛玻璃效果，主体区完全透明不遮挡背景
 * 3. 导航项hover反馈强化交互，响应式适配移动端（垂直布局）
 * 4. 雪花动画支持性能适配+动画偏好适配，兼顾视觉与性能
 * 5. 核心优先级：视觉体验 > 交互体验 > 性能适配 > 响应式兼容
 */

/* 雪花Canvas：全屏覆盖，不拦截鼠标交互，最低层级 */
.snow-canvas {
  position: absolute; /* 绝对定位，覆盖整个容器 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 关键：不拦截鼠标点击/hover等交互，保证下层元素可操作 */
  z-index: 1; /* 最低层级，不遮挡其他内容 */
}

/* 页面容器：全屏布局，固定背景图，Flex垂直排列 */
.user-page-container {
  position: relative; /* 作为子元素绝对定位的基准 */
  width: 100%;
  min-height: 100vh; /* 最小高度铺满视口 */
  display: flex; /* Flex布局垂直排列子元素 */
  flex-direction: column; /* 垂直方向排列 */
  overflow: hidden; /* 隐藏溢出内容（防止雪花超出） */
  background-image: url('@/assets/images/userbackground.png'); /* 用户中心背景图 */
  background-size: cover; /* 背景图全屏覆盖 */
  background-position: center; /* 背景图居中显示 */
  background-repeat: no-repeat; /* 背景图不重复 */
  background-attachment: fixed; /* 滚动时背景固定，提升视觉体验 */
}

/* 页眉：半透明毛玻璃，Flex布局，高层级 */
.user-header {
  display: flex; /* Flex布局排列左/中/右区域 */
  justify-content: space-between; /* 两端对齐，中间自适应 */
  align-items: center; /* 垂直居中 */
  padding: 0.8rem 2rem; /* 内边距，控制间距 */
  background-color: rgba(255, 255, 255, 0.85); /* 半透明白色背景 */
  backdrop-filter: blur(8px); /* 毛玻璃模糊效果 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 轻微阴影，提升层级 */
  z-index: 99; /* 高层级，保证在雪花之上 */
  position: relative; /* 作为z-index的基准 */
}

/* 左右导航容器：Flex布局，统一间距 */
.nav-left, .nav-right {
  display: flex; /* Flex布局排列导航项 */
  gap: 1.5rem; /* 导航项之间的间距 */
}

/* 导航链接样式：hover反馈，过渡动画 */
.nav-link {
  color: #2d3748; /* 默认文字颜色 */
  font-size: 1rem; /* 字体大小 */
  font-weight: 500; /* 字体加粗，提升可读性 */
  text-decoration: none; /* 清除默认下划线 */
  padding: 0.4rem 0.8rem; /* 内边距，扩大点击热区 */
  border-radius: 6px; /* 圆角，弱化直角 */
  transition: all 0.2s ease; /* 所有属性过渡动画，交互更丝滑 */
}

.nav-link:hover {
  color: #4299e1; /* hover时文字变主题色 */
  background-color: #f5fafe; /* hover时浅蓝背景，强化反馈 */
  transform: translateY(-1px); /* hover时轻微上移，灵动效果 */
}

.nav-link:active {
  transform: translateY(0); /* 点击时回归原位，强化按压反馈 */
}

/* 搜索容器：自适应宽度，最大宽度400px */
.search-container {
  flex: 0 1 400px; /* 不放大，可缩小，基准宽度400px */
}

/* 主体区域：透明背景，自适应高度，高层级 */
.user-main {
  flex: 1; /* 占满剩余高度 */
  padding: 2rem; /* 内边距，控制内容间距 */
  z-index: 10; /* 层级高于雪花，低于页眉 */
  background-color: transparent; /* 完全透明，不遮挡背景 */
  backdrop-filter: none; /* 取消毛玻璃，保证背景可见 */
  margin: 0; /* 清除默认外边距 */
  border-radius: 0; /* 清除默认圆角 */
  box-shadow: none; /* 清除默认阴影 */
}

/* 页脚：半透明毛玻璃，居中版权信息 */
.user-footer {
  padding: 1rem; /* 内边距 */
  text-align: center; /* 文字居中 */
  color: #4a5568; /* 浅灰色文字，弱化视觉权重 */
  font-size: 0.9rem; /* 字体缩小，适配页脚 */
  background-color: rgba(255, 255, 255, 0.85); /* 半透明白色背景 */
  backdrop-filter: blur(8px); /* 毛玻璃模糊效果 */
  z-index: 10; /* 层级高于雪花 */
}

/* 响应式适配：平板/手机端（≤768px） */
@media (max-width: 768px) {
  .user-header {
    flex-direction: column; /* 垂直排列，节省横向空间 */
    gap: 1rem; /* 子元素间距 */
    padding: 1rem; /* 调整内边距 */
  }
  .search-container {
    width: 100%; /* 搜索框宽度铺满 */
  }
  .user-main {
    padding: 1rem; /* 缩小主体内边距 */
  }
  .snow-canvas {
    --snow-count: 80; /* 移动端雪花数量兜底，进一步降量 */
  }
}

/* 动画偏好适配：用户开启"减少动画"时隐藏雪花 */
@media (prefers-reduced-motion: reduce) {
  .snow-canvas {
    display: none; /* 隐藏雪花动画，提升体验+性能 */
  }
}
</style>
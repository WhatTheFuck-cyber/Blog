<template>
  <!-- 侧边栏抽屉组件：鼠标滑到左侧阈值触发显示，离开自动隐藏，带滑入/滑出动画 -->
  <transition name="sidebar-slide">
    <div 
      class="sidebar-drawer"
      v-show="isShowSidebar"
      @mouseleave="handleSidebarLeave"
    >
      <!-- 侧边栏核心内容区：包含艺术字体标题、中英文描述、导航菜单、签名图片 -->
      <div class="sidebar-content">
        <h3 class="sidebar-title art-font">Blogging</h3>
        <p class="sidebar-desc">
          <span class="desc-text">欢迎来到</span>
          <span class="art-font desc-art">Blogging</span>
        </p>
        <ul class="sidebar-menu">
          <li class="menu-item" @click="goToRoot">开始</li>
          <li class="menu-item" @click="goToHome">主页</li>
          <li class="menu-item" @click="goToAbout">关于我们</li>
        </ul>
        <div class="signature-wrapper">
          <img 
            src="@/assets/images/signature.png" 
            alt="签名" 
            class="signature-img"
          >
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
/**
 * 侧边栏抽屉组件
 * @description 鼠标滑至页面左侧阈值区域自动显示，离开侧边栏自动隐藏的悬浮抽屉，带滑入/滑出动画
 * @feature 1. 基于鼠标位置的无感触发/隐藏 2. 自定义艺术字体美化标题 3. 平滑滑入/滑出过渡动画 4. 路由跳转导航菜单 5. 组件卸载自动清理监听/定时器
 * @constant {number} LEFT_THRESHOLD - 鼠标触发侧边栏的左侧阈值（20px）
 * @constant {number} HOVER_DELAY - 触发显示的延迟时间（200ms），防止误触
 * @dependencies vue-router - 用于导航菜单的路由跳转
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

/** @type {import('vue-router').Router} 路由 */
const router = useRouter()
/** @type {Ref<boolean>} 侧边栏显示/隐藏状态，默认false（隐藏） */
const isShowSidebar = ref(false)
/** @type {number|null} 悬停触发定时器，用于控制显示延迟，防止误触 */
let hoverTimer = null
/** @constant {number} 鼠标触发侧边栏的左侧像素阈值 */
const LEFT_THRESHOLD = 20
/** @constant {number} 触发侧边栏显示的延迟时间（毫秒） */
const HOVER_DELAY = 200

/**
 * 跳转到根路由（开始页面）
 * @description 点击"开始"菜单触发，跳转至网站根路径
 * @returns {void}
 */
const goToRoot = () => {
  router.push('/')
}

/**
 * 跳转到主页路由
 * @description 点击"主页"菜单触发，跳转至/app/home路径
 * @returns {void}
 */
const goToHome = () => {
  router.push('/app/home')
}

/**
 * 跳转到关于我们路由
 * @description 点击"关于我们"菜单触发，跳转至/app/about路径
 * @returns {void}
 */
const goToAbout = () => {
  router.push('/app/about')
}

/**
 * 全局鼠标移动监听处理
 * @param {MouseEvent} e - 鼠标移动事件对象
 * @description 监听鼠标X坐标，小于阈值时延迟显示侧边栏，否则清除定时器取消显示
 * @returns {void}
 */
const handleMouseMove = (e) => {
  if (e.clientX < LEFT_THRESHOLD) {
    if (hoverTimer) clearTimeout(hoverTimer)
    hoverTimer = setTimeout(() => {
      isShowSidebar.value = true
    }, HOVER_DELAY)
  } else {
    if (hoverTimer) {
      clearTimeout(hoverTimer)
      hoverTimer = null
    }
  }
}

/**
 * 鼠标离开侧边栏处理
 * @param {MouseEvent} e - 鼠标离开事件对象
 * @description 鼠标离开侧边栏且X坐标超出阈值时，隐藏侧边栏
 * @returns {void}
 */
const handleSidebarLeave = (e) => {
  if (e.clientX >= LEFT_THRESHOLD) {
    isShowSidebar.value = false
  }
}

/**
 * 组件挂载钩子
 * @description 绑定全局鼠标移动监听，初始化侧边栏触发逻辑
 * @returns {void}
 */
onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
})

/**
 * 组件卸载钩子
 * @description 解绑全局鼠标监听，清除未执行的定时器，防止内存泄漏
 * @returns {void}
 */
onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  if (hoverTimer) clearTimeout(hoverTimer)
})
</script>

<style scoped>
/* 
 * 侧边栏抽屉样式总说明：
 * 1. 采用fixed定位悬浮在页面左侧，自定义艺术字体美化视觉
 * 2. 内容区居中布局，中英文适配对齐，菜单/签名图分层展示
 * 3. 滑入/滑出动画提升交互体验，hover反馈强化可点击性
 * 4. 核心优先级：视觉美观 > 交互体验 > 响应式适配
 */

/* 引入自定义艺术字体（Barett Street），匹配签名风格 */
@font-face {
  font-family: 'Barett Street'; /* 自定义字体名称 */
  src: url('@/assets/fonts/Barett-Street/Barett Street.ttf') format('truetype'); /* 字体文件路径 */
  font-weight: normal; /* 字体权重 */
  font-style: normal; /* 字体样式 */
}

/* 侧边栏抽屉主体：fixed定位，悬浮层，圆角+阴影提升质感 */
.sidebar-drawer {
  position: fixed; /* 固定定位，不随页面滚动 */
  top: 3vh; /* 顶部间距3%视口高度 */
  left: 3vh; /* 左侧间距3%视口高度 */
  width: 350px; /* 固定宽度 */
  height: 94vh; /* 高度=视口高度-6%，匹配上下间距 */
  background-color: #ffffff; /* 白色背景 */
  border-radius: 12px; /* 圆角，弱化直角 */
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1); /* 轻微阴影，提升层级 */
  z-index: 999; /* 高z-index，确保在最上层 */
  overflow-y: auto; /* 内容超出时垂直滚动 */
}

/* 艺术字体通用样式：应用自定义字体，统一行高和颜色 */
.art-font {
  font-family: 'Barett Street', cursive; /* 优先使用自定义字体，降级为手写体 */
  color: #2d3748; /* 深灰色文字，提升可读性 */
  line-height: 1; /* 压缩行高，匹配字体舒展度 */
}

/* 侧边栏标题：超大字号，居中显示，底部间距 */
.sidebar-title {
  margin: 0 0 1rem 0; /* 清除默认边距，仅保留底部间距 */
  font-size: 3.2em; /* 超大字号，突出标题 */
  text-align: center; /* 居中显示 */
}

/* 描述文本容器：Flex布局实现中英文垂直/水平居中 */
.sidebar-desc {
  margin: 0 0 2rem 0; /* 底部间距，区分标题和菜单 */
  display: flex; /* Flex布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  gap: 0.5rem; /* 中英文之间的间距 */
}

/* 描述中的中文文本：字号放大，浅灰色，与英文协调 */
.desc-text {
  font-size: 1.5rem; /* 放大字号，匹配英文视觉权重 */
  color: #718096; /* 浅灰色，弱化视觉权重 */
}

/* 描述中的英文艺术字体：字号适配，强化视觉效果 */
.desc-art {
  font-size: 2.3em; /* 字号适配中文，保持协调 */
}

/* 侧边栏内容容器：统一内边距，控制内容区域 */
.sidebar-content {
  padding: 2rem 1.5rem; /* 上下2rem，左右1.5rem内边距 */
}

/* 导航菜单容器：清除默认样式，居中显示 */
.sidebar-menu {
  list-style: none; /* 清除默认列表样式 */
  padding: 0; /* 清除默认内边距 */
  margin: 0 0 2rem 0; /* 底部间距，区分菜单和签名图 */
  text-align: center; /* 菜单居中，提升视觉协调度 */
}

/* 菜单项样式：hover反馈，过渡动画，强化可点击性 */
.menu-item {
  padding: 1rem 0; /* 上下内边距，扩大点击热区 */
  color: #4a5568; /* 默认文字颜色 */
  cursor: pointer; /* 鼠标手型，提示可点击 */
  transition: all 0.2s ease; /* 所有属性过渡动画 */
  font-size: 1.3rem; /* 字号放大，提升可读性 */
}

.menu-item:hover {
  color: #2b6cb0; /* hover时文字变主题色 */
  padding-left: 0.5rem; /* hover时轻微左移，强化反馈 */
}

/* 签名图片容器：顶部边框分隔，居中显示 */
.signature-wrapper {
  margin-top: 2rem; /* 顶部间距 */
  padding-top: 1.5rem; /* 顶部内边距，与边框形成间距 */
  border-top: 1px solid #f0f0f0; /* 顶部浅边框，分隔菜单和签名 */
  text-align: center; /* 图片居中 */
}

/* 签名图片样式：自适应宽度，圆角+阴影提升质感 */
.signature-img {
  max-width: 80%; /* 最大宽度80%，防止溢出 */
  height: auto; /* 高度自适应，保持比例 */
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); /* 轻微阴影，提升质感 */
}

/* 侧边栏滑入/滑出过渡动画：仅X轴位移，实现顺滑显隐 */
.sidebar-slide-enter-from,
.sidebar-slide-leave-to {
  transform: translateX(-100%); /* 初始/结束状态：向左移出可视区域 */
}
.sidebar-slide-enter-active,
.sidebar-slide-leave-active {
  transition: transform 0.3s ease; /* 位移过渡动画，0.3秒顺滑完成 */
}
.sidebar-slide-enter-to,
.sidebar-slide-leave-from {
  transform: translateX(0); /* 目标/起始状态：原位显示 */
}
</style>
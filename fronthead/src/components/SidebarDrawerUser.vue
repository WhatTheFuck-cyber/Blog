<template>
  <!-- 侧边栏抽屉组件：鼠标滑到左侧阈值触发显示，支持用户名展示、登出/注销（仅登录态显示），带滑入/滑出动画 -->
  <transition name="sidebar-slide">
    <div 
      class="sidebar-drawer"
      v-show="isShowSidebar"
      @mouseleave="handleSidebarLeave"
    >
      <!-- 侧边栏核心内容区：艺术字体标题、带用户名的欢迎语、导航菜单、签名图、登出/注销按钮（登录态） -->
      <div class="sidebar-content">
        <h3 class="sidebar-title art-font">Blogging</h3>
        <p class="sidebar-desc">
          <span class="desc-text">欢迎{{ userName || '访客' }}来到</span>
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
          <!-- 登出/注销按钮容器：仅登录状态显示 -->
          <div class="sidebar-btns" v-if="isLoggedIn">
            <button class="sidebar-btn logout-btn" @click="handleLogout">登出</button>
            <button class="sidebar-btn delete-btn" @click="handleDeleteAccount">注销</button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
/**
 * 侧边栏抽屉组件（带用户态管理）
 * @description 鼠标滑至页面左侧阈值区域自动显示，支持用户名展示、登出/注销操作（仅登录态可见），带滑入/滑出动画
 * @feature 1. 基于鼠标位置的无感触发/隐藏 2. 展示登录用户名（未登录显示"访客"） 3. 登出（清理状态/本地存储/接口通知） 4. 注销账号（二次确认+后端接口+登出） 5. 响应式适配移动端 6. 自定义艺术字体美化视觉
 * @constant {number} LEFT_THRESHOLD - 鼠标触发侧边栏的左侧阈值（20px）
 * @constant {number} HOVER_DELAY - 触发显示的延迟时间（200ms），防止误触
 * @dependencies 
 *  - vue-router: 导航菜单/登出跳转
 *  - userInfoStore: 获取/清除用户信息
 *  - userStore: 基础用户状态（token/登录态）
 *  - request: 后端接口请求（登出/注销）
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserInfoStore } from '@/store/userInfo' // 用户信息store（用户名/ID等）
import { useUserStore } from '@/store/user' // 基础用户store（token/登录态/刷新定时器等）
import request from '@/utils/request' // 后端请求工具

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

// Store实例初始化
const userInfoStore = useUserInfoStore() // 用户信息store实例
const userStore = useUserStore() // 基础用户store实例（存储token/登录态等）

// 计算属性：用户态相关
/**
 * 计算属性：获取当前用户名
 * @description 优先取userInfoStore的用户名，无则取userStore，均无显示空（模板中显示"访客"）
 * @returns {string} 用户名/空字符串
 */
const userName = computed(() => {
  return userInfoStore.username || (userStore?.username || '')
})

/**
 * 计算属性：判断是否登录
 * @description 优先取userInfoStore的用户ID，无则取userStore的登录态，均无则false
 * @returns {boolean} 登录状态（true=已登录，false=未登录）
 */
const isLoggedIn = computed(() => {
  return !!userInfoStore.id || (userStore?.isLoggedIn || false)
})

// 导航菜单路由跳转方法
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

// 登出/注销核心逻辑
/**
 * 处理用户登出逻辑
 * @description 1. 清理定时器/监听 2. 调用后端登出接口 3. 重置store状态 4. 清除本地存储/请求头 5. 跳转登录页
 * @returns {Promise<void>}
 */
const handleLogout = async () => {
  try {
    // 1. 清理用户store中的定时器（防止内存泄漏）
    if (userStore?.refreshTimer) {
      clearTimeout(userStore.refreshTimer)
      userStore.refreshTimer = null
    }

    // 2. 移除页面可见性监听（若有）
    if (userStore?.visibilityChangeListener) {
      document.removeEventListener('visibilitychange', userStore.visibilityChangeListener)
      userStore.visibilityChangeListener = null
    }

    // 3. 调用后端登出接口（携带token）
    const token = userStore?.token || (localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).token : '')
    if (token) {
      try {
        await request.post('/users/logout', { token })
        console.log('后端登出成功')
      } catch (error) {
        console.error('后端登出失败：', error)
      }
    }

    // 4. 重置store状态
    userInfoStore.clearUserInfo() // 清除用户详细信息
    if (userStore?.resetState) {
      userStore.resetState() // 重置基础用户状态
    }

    // 5. 清除本地存储和请求头
    localStorage.removeItem('user') // 清除本地用户存储
    delete request.defaults.headers.common['Authorization'] // 清除请求头token

    // 6. 跳转登录页
    await router.push('/app/login')
  } catch (err) {
    console.error('登出处理异常：', err)
  }
}

/**
 * 处理用户注销账号逻辑
 * @description 1. 二次确认防止误操作 2. 校验用户ID 3. 调用后端注销接口 4. 注销成功后执行登出逻辑 5. 异常提示用户
 * @returns {Promise<void>}
 */
const handleDeleteAccount = async () => {
  // 二次确认：防止误操作（不可逆操作）
  if (!confirm('确认要注销账号吗？此操作不可逆，所有数据将被删除！')) {
    return
  }

  try {
    // 校验用户ID
    const userId = userInfoStore.id
    if (!userId) {
      alert('无法获取用户ID，注销失败')
      return
    }

    // 调用后端注销接口
    await request.delete(`/users/${userId}`)
    alert('账号注销成功')

    // 注销成功后执行登出逻辑
    await handleLogout()
  } catch (error) {
    console.error('注销账号失败：', error)
    // 友好的错误提示（优先取后端返回信息）
    alert(`注销失败：${error.response?.data?.message || '服务器异常'}`)
  }
}

// 鼠标监听逻辑
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

// 生命周期钩子：监听绑定/清理
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
 * 1. 采用fixed定位悬浮在页面左侧，自定义艺术字体美化视觉，宽度调整为600px适配更多内容
 * 2. 内容区居中布局，支持用户名动态展示，新增登出/注销按钮（仅登录态显示）
 * 3. 按钮区分普通操作（登出）和危险操作（注销）的视觉风格，hover反馈强化交互
 * 4. 响应式适配移动端：宽度收缩、按钮垂直排列
 * 5. 核心优先级：视觉美观 > 交互体验 > 响应式适配 > 功能适配
 */

/* 引入自定义艺术字体（Barett Street），匹配签名风格 */
@font-face {
  font-family: 'Barett Street'; /* 自定义字体名称 */
  src: url('@/assets/fonts/Barett-Street/Barett Street.ttf') format('truetype'); /* 字体文件路径 */
  font-weight: normal; /* 字体权重 */
  font-style: normal; /* 字体样式 */
}

/* 侧边栏抽屉主体：fixed定位，悬浮层，宽度调整为600px适配用户信息/按钮 */
.sidebar-drawer {
  position: fixed; /* 固定定位，不随页面滚动 */
  top: 3vh; /* 顶部间距3%视口高度 */
  left: 3vh; /* 左侧间距3%视口高度 */
  width: 600px; /* 加宽至600px，适配新增的用户信息和按钮 */
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

/* 描述文本容器：Flex布局实现中英文+用户名垂直/水平居中 */
.sidebar-desc {
  margin: 0 0 2rem 0; /* 底部间距，区分标题和菜单 */
  display: flex; /* Flex布局 */
  align-items: center; /* 垂直居中 */
  justify-content: center; /* 水平居中 */
  gap: 0.5rem; /* 文本之间的间距 */
}

/* 描述中的中文+用户名样式：字号放大，浅灰色，与英文协调 */
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

/* 签名图片容器：顶部边框分隔，居中显示，适配按钮布局 */
.signature-wrapper {
  margin-top: 2rem; /* 顶部间距 */
  padding-top: 1.5rem; /* 顶部内边距，与边框形成间距 */
  border-top: 1px solid #f0f0f0; /* 顶部浅边框，分隔菜单和签名/按钮 */
  text-align: center; /* 内容居中 */
}

/* 签名图片样式：自适应宽度，底部间距给按钮留出空间 */
.signature-img {
  max-width: 80%; /* 最大宽度80%，防止溢出 */
  height: auto; /* 高度自适应，保持比例 */
  border-radius: 8px; /* 圆角 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); /* 轻微阴影，提升质感 */
  margin-bottom: 1.5rem; /* 底部间距，给按钮留出空间 */
}

/* 按钮容器：Flex布局，居中排列，内边距适配 */
.sidebar-btns {
  display: flex; /* Flex布局排列按钮 */
  gap: 1rem; /* 按钮之间的间距 */
  justify-content: center; /* 水平居中 */
  margin-top: 1.5rem; /* 顶部间距，与签名图区分 */
  padding: 0 1rem; /* 左右内边距，防止按钮贴边 */
}

/* 按钮通用样式：统一内边距、圆角、字体、过渡动画 */
.sidebar-btn {
  padding: 0.8rem 1.5rem; /* 内边距，扩大点击热区 */
  border-radius: 8px; /* 圆角，弱化直角 */
  border: none; /* 清除默认边框 */
  cursor: pointer; /* 鼠标手型，提示可点击 */
  font-size: 1rem; /* 字体大小适配 */
  transition: all 0.2s ease; /* 所有属性过渡动画，交互更丝滑 */
  font-weight: 500; /* 字体加粗，提升可读性 */
}

/* 登出按钮样式：中性色，区分普通操作 */
.logout-btn {
  background-color: #e2e8f0; /* 浅灰背景，中性色 */
  color: #2d3748; /* 深灰色文字，提升可读性 */
}
.logout-btn:hover {
  background-color: #cbd5e1; /* hover背景色加深，强化反馈 */
}

/* 注销按钮样式：危险色，区分高危操作 */
.delete-btn {
  background-color: #fef2f2; /* 浅红背景，危险色基调 */
  color: #dc2626; /* 红色文字，强化危险提示 */
}
.delete-btn:hover {
  background-color: #fee2e2; /* hover背景色加深，强化危险提示 */
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

/* 响应式适配：移动端（≤480px） */
@media (max-width: 480px) {
  .sidebar-drawer {
    width: 280px; /* 收缩宽度至280px，适配手机屏幕 */
  }
  .sidebar-btns {
    flex-direction: column; /* 按钮垂直排列，节省横向空间 */
    gap: 0.8rem; /* 缩小按钮间距 */
  }
  .sidebar-btn {
    width: 100%; /* 按钮宽度铺满容器，提升点击体验 */
  }
}
</style>
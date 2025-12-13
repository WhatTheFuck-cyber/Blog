<template>
  <!-- 悬浮预览面板：通过teleport挂载到body，支持拖拽/拉伸，存储位置/大小到本地 -->
  <teleport to="body">
    <div
      v-if="visible"
      ref="floatPanel"
      class="markdown-float-panel"
      :style="{
        top: `${position.top}px`,
        left: `${position.left}px`,
        width: `${size.width}px`,
        height: `${size.height}px`,
      }"
      @mousedown="handlePanelMouseDown"
    >
      <!-- 悬浮框头部：拖拽区域，包含标题和关闭按钮 -->
      <div class="float-panel-header" @mousedown.stop="handleHeaderMouseDown">
        <h3 class="panel-title">Markdown 预览</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- 预览内容区：承载Markdown预览组件，自适应面板大小 -->
      <div class="float-panel-content">
        <MdPreview :modelValue="content" previewOnly class="preview-content" />
      </div>

      <!-- 拉伸手柄：右下角拖拽实现面板大小调整 -->
      <div class="resize-handle" @mousedown="handleResizeMouseDown"></div>
    </div>
  </teleport>
</template>

<script setup>
/**
 * Markdown 悬浮预览面板组件
 * @description 支持拖拽移动、拉伸调整大小的Markdown预览面板，位置/大小状态持久化到本地存储
 * @feature 1. 拖拽移动（头部区域） 2. 拉伸调整尺寸（右下角手柄） 3. 位置/大小本地存储 4. 边界限制（不超出可视区域） 5. 滚动条美化
 * @props {boolean} visible - 面板显示/隐藏状态（必填）
 * @props {string} content - Markdown预览内容（必填）
 * @props {Object} defaultPosition - 默认位置 {top: number, left: number}，默认{top:100, left:100}
 * @props {Object} defaultSize - 默认尺寸 {width: number, height: number}，默认{width:600, height:500}
 * @emits {update:visible} - 关闭面板时派发，更新visible状态
 * @dependencies MdPreview（md-editor-v3）
 */
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { MdPreview } from 'md-editor-v3'

// 组件Props定义
const props = defineProps({
  visible: { type: Boolean, required: true, default: false },
  content: { type: String, required: true, default: '' },
  defaultPosition: { type: Object, default: () => ({ top: 100, left: 100 }) },
  defaultSize: { type: Object, default: () => ({ width: 600, height: 500 }) },
})

// 组件事件派发
const emits = defineEmits(['update:visible'])

// 核心状态
const floatPanel = ref(null)
/**
 * 悬浮面板位置状态
 * @type {Ref<Object>} - {top: number, left: number}，默认取props.defaultPosition
 */
const position = ref({ ...props.defaultPosition })
/**
 * 悬浮面板尺寸状态
 * @type {Ref<Object>} - {width: number, height: number}，默认取props.defaultSize
 */
const size = ref({ ...props.defaultSize })

// 拖拽相关状态
/** @type {Ref<boolean>} 拖拽状态标识（true=正在拖拽） */
const isDragging = ref(false)
/** @type {Ref<Object>} 拖拽起始坐标 {x: number, y: number} */
const dragStart = ref({ x: 0, y: 0 })

// 拉伸相关状态
/** @type {Ref<boolean>} 拉伸状态标识（true=正在拉伸） */
const isResizing = ref(false)
/** @type {Ref<Object>} 拉伸起始信息 {x: number, y: number, width: number, height: number} */
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })

/**
 * 从本地存储加载面板位置/尺寸状态
 * @description 读取localStorage中保存的位置和尺寸，加载失败则使用默认值
 * @returns {void}
 */
const loadPanelState = () => {
  try {
    const savedPos = localStorage.getItem('markdown-float-pos')
    const savedSize = localStorage.getItem('markdown-float-size')
    if (savedPos) position.value = JSON.parse(savedPos)
    if (savedSize) size.value = JSON.parse(savedSize)
  } catch (e) {
    console.error('加载悬浮框状态失败:', e)
  }
}

/**
 * 保存面板位置/尺寸到本地存储
 * @description 将当前位置和尺寸序列化后存入localStorage，持久化状态
 * @returns {void}
 */
const savePanelState = () => {
  try {
    localStorage.setItem('markdown-float-pos', JSON.stringify(position.value))
    localStorage.setItem('markdown-float-size', JSON.stringify(size.value))
  } catch (e) {
    console.error('保存悬浮框状态失败:', e)
  }
}

/**
 * 头部拖拽开始处理
 * @param {MouseEvent} e - 鼠标按下事件对象
 * @description 记录拖拽起始偏移量，标记拖拽状态为开始
 * @returns {void}
 */
const handleHeaderMouseDown = (e) => {
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - position.value.left,
    y: e.clientY - position.value.top,
  }
  e.preventDefault()
}

/**
 * 面板点击事件处理
 * @param {MouseEvent} e - 鼠标按下事件对象
 * @description 阻止事件冒泡，避免点击内容区触发拖拽
 * @returns {void}
 */
const handlePanelMouseDown = (e) => e.stopPropagation()

/**
 * 拉伸手柄按下处理
 * @param {MouseEvent} e - 鼠标按下事件对象
 * @description 记录拉伸起始坐标和面板尺寸，标记拉伸状态为开始
 * @returns {void}
 */
const handleResizeMouseDown = (e) => {
  isResizing.value = true
  resizeStart.value = {
    x: e.clientX,
    y: e.clientY,
    width: size.value.width,
    height: size.value.height,
  }
  e.preventDefault()
}

/**
 * 全局鼠标移动处理
 * @param {MouseEvent} e - 鼠标移动事件对象
 * @description 处理拖拽移动和拉伸调整尺寸逻辑，添加边界限制防止超出可视区域
 * @returns {void}
 */
const handleMouseMove = (e) => {
  // 拖拽逻辑：计算新位置并限制边界
  if (isDragging.value) {
    const newLeft = e.clientX - dragStart.value.x
    const newTop = e.clientY - dragStart.value.y
    position.value = {
      left: Math.max(20, Math.min(newLeft, window.innerWidth - size.value.width - 20)),
      top: Math.max(20, Math.min(newTop, window.innerHeight - size.value.height - 20)),
    }
  }

  // 拉伸逻辑：计算新尺寸并限制最小/最大值
  if (isResizing.value) {
    const deltaX = e.clientX - resizeStart.value.x
    const deltaY = e.clientY - resizeStart.value.y
    position.value = {
      left: Math.max(20, Math.min(position.value.left, window.innerWidth - 300)),
      top: Math.max(20, Math.min(position.value.top, window.innerHeight - 300)),
    }
    size.value = {
      width: Math.max(300, Math.min(resizeStart.value.width + deltaX, window.innerWidth - 40)),
      height: Math.max(300, Math.min(resizeStart.value.height + deltaY, window.innerHeight - 40)),
    }
  }
}

/**
 * 全局鼠标松开处理
 * @description 结束拖拽/拉伸状态，保存当前面板位置/尺寸到本地存储
 * @returns {void}
 */
const handleMouseUp = () => {
  if (isDragging.value) {
    isDragging.value = false
    savePanelState()
  }
  if (isResizing.value) {
    isResizing.value = false
    savePanelState()
  }
}

/**
 * 关闭悬浮面板
 * @description 派发update:visible事件，将面板状态设为隐藏
 * @returns {void}
 */
const handleClose = () => emits('update:visible', false)

/**
 * 监听面板显示状态
 * @description 面板显示时加载本地存储的位置/尺寸，立即执行一次
 */
watch(() => props.visible, (newVal) => newVal && loadPanelState(), { immediate: true })

/**
 * 组件挂载钩子
 * @description 绑定全局鼠标移动/松开事件，处理拖拽/拉伸逻辑
 * @returns {void}
 */
onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

/**
 * 组件卸载钩子
 * @description 解绑全局鼠标事件，防止内存泄漏
 * @returns {void}
 */
onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})
</script>

<style scoped>
/* 
 * Markdown悬浮预览面板样式总说明：
 * 1. 面板采用fixed定位，支持拖拽/拉伸，视觉层叠优先级高（z-index:9999）
 * 2. 头部为拖拽区域，内容区自适应高度，右下角手柄支持拉伸
 * 3. 优化滚动条样式，添加hover交互反馈，提升视觉体验
 * 4. 核心优先级：交互体验 > 视觉样式 > 细节适配
 */

/* 悬浮框主体：fixed定位，白色背景，阴影提升层级，溢出隐藏 */
.markdown-float-panel {
  position: fixed; /* 固定定位，脱离文档流 */
  background: #fff; /* 白色背景 */
  border-radius: 8px; /* 圆角设计，弱化直角 */
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); /* 初始阴影，提升层级 */
  z-index: 9999; /* 高z-index，确保在最上层 */
  overflow: hidden; /* 隐藏溢出内容 */
  border: 1px solid #e2e8f0; /* 浅边框，区分面板 */
  transition: box-shadow 0.2s ease; /* 阴影过渡动画 */
}
.markdown-float-panel:hover {
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2); /* hover加深阴影，强化交互 */
}

/* 悬浮框头部：Flex布局，拖拽区域，禁止文字选中 */
.float-panel-header {
  display: flex; /* Flex布局排列标题和关闭按钮 */
  justify-content: space-between; /* 两端对齐 */
  align-items: center; /* 垂直居中 */
  padding: 0.8rem 1rem; /* 内边距，保证内容间距 */
  background: #f8fafc; /* 浅灰背景，区分头部 */
  border-bottom: 1px solid #e2e8f0; /* 底部边框，分隔内容区 */
  cursor: move; /* 鼠标手型，提示可拖拽 */
  user-select: none; /* 禁止文字选中，优化拖拽体验 */
}
.panel-title {
  margin: 0; /* 清除默认外边距 */
  font-size: 1rem; /* 字体大小 */
  color: #2d3748; /* 文字颜色 */
  font-weight: 600; /* 文字加粗 */
}
.close-btn {
  width: 24px; /* 固定宽度 */
  height: 24px; /* 固定高度 */
  border: none; /* 清除默认边框 */
  background: transparent; /* 透明背景 */
  color: #718096; /* 文字颜色 */
  font-size: 1.2rem; /* 字体大小 */
  cursor: pointer; /* 鼠标手型 */
  border-radius: 4px; /* 圆角 */
  transition: all 0.2s ease; /* 过渡动画 */
}
.close-btn:hover {
  background: #e2e8f0; /* hover背景色 */
  color: #2d3748; /* hover文字色 */
}

/* 预览内容区：自适应高度，内边距，垂直滚动 */
.float-panel-content {
  width: 100%; /* 宽度铺满 */
  height: calc(100% - 57px); /* 高度=面板高度-头部高度 */
  padding: 1rem; /* 内边距 */
  box-sizing: border-box; /* 内边距计入宽高 */
  overflow-y: auto; /* 垂直滚动 */
}
.preview-content {
  width: 100%; /* 宽度铺满 */
  height: 100%; /* 高度铺满 */
}

/* 拉伸手柄：右下角定位，蓝色背景，拉伸光标 */
.resize-handle {
  position: absolute; /* 绝对定位 */
  right: 0; /* 靠右 */
  bottom: 0; /* 靠下 */
  width: 16px; /* 宽度 */
  height: 16px; /* 高度 */
  background: #4299e1; /* 主题色背景 */
  border-radius: 0 0 8px 0; /* 右下角圆角，匹配面板 */
  cursor: se-resize; /* 拉伸光标（东南方向） */
}
.resize-handle::after {
  content: ''; /* 伪元素实现拉伸图标 */
  position: absolute; /* 绝对定位 */
  top: 50%; /* 垂直居中 */
  left: 50%; /* 水平居中 */
  transform: translate(-50%, -50%); /* 精准居中 */
  width: 8px; /* 图标宽度 */
  height: 8px; /* 图标高度 */
  border-right: 2px solid white; /* 右侧边框（白色） */
  border-bottom: 2px solid white; /* 底部边框（白色） */
}

/* 滚动条美化：仅作用于内容区滚动条 */
.float-panel-content::-webkit-scrollbar {
  width: 6px; /* 滚动条宽度 */
  height: 6px; /* 滚动条高度 */
}
.float-panel-content::-webkit-scrollbar-track {
  background: #f1f5f9; /* 滚动条轨道背景 */
  border-radius: 3px; /* 轨道圆角 */
}
.float-panel-content::-webkit-scrollbar-thumb {
  background: #cbd5e1; /* 滚动条滑块背景 */
  border-radius: 3px; /* 滑块圆角 */
}
.float-panel-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8; /* hover滑块背景色 */
}
</style>
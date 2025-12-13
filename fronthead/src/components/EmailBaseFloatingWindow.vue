<template>
  <teleport to="body">
    <transition name="card-slide">
      <div
        v-if="isShowCard"
        ref="floatCard"
        class="float-card"
        :style="{
          top: `${position.top}px`,
          left: `${position.left}px`,
          width: `${size.width}px`,
          height: `${size.height}px`,
          backgroundImage: `url('${backgroundImage}')`,
          backgroundSize: 'auto',
          backgroundPosition: `${bgPosition.x}px ${bgPosition.y}px`,
        }"
        @mousedown="handleCardMouseDown"
      >
        <!-- 卡片头部 -->
        <div class="card-header" @mousedown.stop="handleHeaderMouseDown">
          <div class="drag-hint">和朋友说两句~</div>
          <div class="card-title" @click="isShowWhiteboard = !isShowWhiteboard">邮箱</div>
          <button 
            class="close-btn" 
            @click="handleClose"
            :style="{
              width: `max(10px, min(${closeBtnSize}px, 32px))`,
              height: `max(10px, min(${closeBtnSize}px, 32px))`,
              fontSize: `${closeBtnSize * 0.6}px`
            }"
          >×</button>
        </div>

        <!-- 核心：悬浮框内部的白板面板（在悬浮框里） -->
        <transition name="whiteboard-fade">
          <div v-if="isShowWhiteboard" class="whiteboard">
            <button class="whiteboard-close" @click="isShowWhiteboard = false">×</button>
            <MessagePage class="whiteboard-content" />
          </div>
        </transition>

        <!-- 拉伸手柄 -->
        <div 
          class="resize-handle" 
          @mousedown="handleResizeMouseDown"
          :style="{
            width: `max(10px, min(${resizeHandleSize}px, 32px))`,
            height: `max(10px, min(${resizeHandleSize}px, 32px))`
          }"
        ></div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import MessagePage from '@/components/MessagePage.vue' 

const MIN_WIDTH = 500 // 最小宽度
const MIN_HEIGHT = 400 // 最小高度

// 背景图路径（保留窗移效果）
const backgroundImage = ref(new URL('@/assets/images/emailbackground.png', import.meta.url).href)

// 核心状态：悬浮框+内部白板
const floatCard = ref(null)
const isShowCard = ref(false)
const isShowWhiteboard = ref(false) // 控制悬浮框内部白板的显示/隐藏
const position = ref({ top: 100, left: window.innerWidth - 420 })
const size = ref({ width: 500, height: 400 })
const bgPosition = ref({ x: 0, y: 0 })
const resizeHandleSize = ref(20) 
const closeBtnSize = ref(36) 
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const isResizing = ref(false)
const resizeStart = ref({ x: 0, y: 0, width: 0, height: 0 })
const bgImageSize = ref({ width: 0, height: 0 })
const RIGHT_THRESHOLD = 20  
const TRIGGER_DELAY = 150   
let triggerTimer = null     

/** 保留背景图的窗移效果逻辑 */
const loadBgImage = () => {
  const img = new Image()
  img.src = backgroundImage.value
  img.onload = () => {
    bgImageSize.value = { width: img.width, height: img.height }
    calculateBgPosition()
  }
}
const calculateBgPosition = () => {
  if (!bgImageSize.value.width || !bgImageSize.value.height) return
  const viewportCenterX = window.innerWidth / 2
  const viewportCenterY = window.innerHeight / 2
  const bgCenterX = bgImageSize.value.width / 2
  const bgCenterY = bgImageSize.value.height / 2

  bgPosition.value = {
    x: -position.value.left + (viewportCenterX - bgCenterX),
    y: -position.value.top + (viewportCenterY - bgCenterY)
  }

  bgPosition.value.x = Math.max(-(bgImageSize.value.width - size.value.width), Math.min(0, bgPosition.value.x))
  bgPosition.value.y = Math.max(-(bgImageSize.value.height - size.value.height), Math.min(0, bgPosition.value.y))
}

/** 原尺寸/存储/鼠标交互逻辑（全部保留） */
const updateHandleSizeByCard = () => {
  const cardRatio = (size.value.width + size.value.height) / 800 
  resizeHandleSize.value = Math.floor(10 + cardRatio * 20) 
}
const updateCloseBtnSize = () => {
  const cardRatio = (size.value.width + size.value.height) / 800 
  closeBtnSize.value = Math.floor(24 + cardRatio * 18) 
}
const loadCardState = () => {
  try {
    const savedPos = localStorage.getItem('viewfinder-pos')
    const savedSize = localStorage.getItem('viewfinder-size')
    if (savedPos) position.value = JSON.parse(savedPos)
    if (savedSize) {
      const parsedSize = JSON.parse(savedSize)
      // 确保加载的尺寸不小于最小值
      size.value = {
        width: Math.max(MIN_WIDTH, parsedSize.width),
        height: Math.max(MIN_HEIGHT, parsedSize.height)
      }
    }
    calculateBgPosition()
    updateHandleSizeByCard()
    updateCloseBtnSize()
  } catch (e) {
    console.error('加载取景框状态失败:', e)
  }
}
const saveCardState = () => {
  try {
    localStorage.setItem('viewfinder-pos', JSON.stringify(position.value))
    localStorage.setItem('viewfinder-size', JSON.stringify(size.value))
  } catch (e) {
    console.error('保存取景框状态失败:', e)
  }
}
const handleMouseMove = (e) => {
  const distanceToRight = window.innerWidth - e.clientX
  if (distanceToRight < RIGHT_THRESHOLD) {
    if (triggerTimer) clearTimeout(triggerTimer)
    triggerTimer = setTimeout(() => {
      isShowCard.value = true
      loadCardState()
    }, TRIGGER_DELAY)
  } else {
    if (triggerTimer) {
      clearTimeout(triggerTimer)
      triggerTimer = null
    }
  }
}
const handleHeaderMouseDown = (e) => {
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - position.value.left,
    y: e.clientY - position.value.top,
  }
  e.preventDefault()
}
const handleCardMouseDown = (e) => e.stopPropagation()
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
const handleGlobalMouseMove = (e) => {
  if (isDragging.value) {
    const newLeft = e.clientX - dragStart.value.x
    const newTop = e.clientY - dragStart.value.y
    position.value = {
      left: Math.max(20, Math.min(newLeft, window.innerWidth - size.value.width - 20)),
      top: Math.max(20, Math.min(newTop, window.innerHeight - size.value.height - 20)),
    }
    calculateBgPosition()
  }

  if (isResizing.value) {
    const deltaX = e.clientX - resizeStart.value.x
    const deltaY = e.clientY - resizeStart.value.y
    size.value = {
      // 用MIN_WIDTH/MIN_HEIGHT限制最小尺寸
      width: Math.max(MIN_WIDTH, Math.min(resizeStart.value.width + deltaX, window.innerWidth - 40)),
      height: Math.max(MIN_HEIGHT, Math.min(resizeStart.value.height + deltaY, window.innerHeight - 40)),
    }
    position.value = {
      left: Math.max(20, Math.min(position.value.left, window.innerWidth - size.value.width - 20)),
      top: Math.max(20, Math.min(position.value.top, window.innerHeight - size.value.height - 20)),
    }
    calculateBgPosition()
    updateHandleSizeByCard()
    updateCloseBtnSize()
  }
}
const handleMouseUp = () => {
  if (isDragging.value) {
    isDragging.value = false
    saveCardState()
  }
  if (isResizing.value) {
    isResizing.value = false
    saveCardState()
  }
}
const handleClose = () => {
  isShowCard.value = false
  isShowWhiteboard.value = false
}

// 窗口变化逻辑
const handleWindowResize = () => {
  calculateBgPosition()
  // 确保悬浮窗尺寸不小于最小值
  size.value = {
    width: Math.max(MIN_WIDTH, size.value.width),
    height: Math.max(MIN_HEIGHT, size.value.height)
  }
  position.value = {
    left: Math.max(20, Math.min(position.value.left, window.innerWidth - size.value.width - 20)),
    top: Math.max(20, Math.min(position.value.top, window.innerHeight - size.value.height - 20)),
  }
  updateHandleSizeByCard()
  updateCloseBtnSize()
}

// 挂载/卸载
onMounted(() => {
  loadBgImage()
  window.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mousemove', handleGlobalMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('resize', handleWindowResize)
})
onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mousemove', handleGlobalMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  window.removeEventListener('resize', handleWindowResize)
  if (triggerTimer) clearTimeout(triggerTimer)
})
</script>

<style scoped>
/* 原样式保留，调整白板为悬浮框内部元素 */
.resize-handle {
  position: absolute;
  right: 2px;
  bottom: 2px;
  border-radius: 6px;
  cursor: se-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  background-color: rgba(255, 255, 255, 0.2);
}
.resize-handle::after {
  content: '';
  width: calc(55% - 1px); 
  height: calc(55% - 1px);
  border-right: 3px solid #000;
  border-bottom: 3px solid #000;
}
.resize-handle:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.close-btn {
  border: none;
  background-color: transparent;
  color: #000;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  border-radius: 50%;
}
.close-btn:hover {
  color: #ff4444;
  transform: scale(1.1);
  background-color: rgba(255, 255, 255, 0.1);
}

:global(body::before) {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: v-bind('backgroundImage');
  background-size: auto;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
  pointer-events: none;
  opacity: 0;
}
:global(body) {
  margin: 0;
  padding: 0;
  min-height: 100vh;
  background-color: #f9f9f9;
}

.card-slide-enter-from {
  transform: translateX(100%);
}
.card-slide-enter-active {
  transition: transform 0.3s ease;
}
.card-slide-enter-to {
  transform: translateX(0);
}

.float-card {
  position: fixed;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  overflow: hidden; /* 内部元素不超出悬浮框 */
  background-color: transparent;
  border: 2px solid rgba(255, 255, 255, 0.8);
  transition: box-shadow 0.2s ease;
  background-repeat: no-repeat;
}
.float-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.card-header {
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
  cursor: move;
  user-select: none;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.card-title {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 36px;
  font-weight: 500;
  color: #000;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  cursor: pointer;
}
.card-title:hover {
  color: #2c3e50;
}

.drag-hint {
  font-size: 18px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.whiteboard {
  position: absolute;
  /* 上下左右边距设置（可自定义数值，这里以10px为例） */
  top: calc(50px + 30px); /* 上：header高度(50px) + 顶部边距(10px) */
  left: 30px;             /* 左：距离悬浮窗左侧10px */
  right: 30px;            /* 右：距离悬浮窗右侧10px */
  bottom: 30px;           /* 下：距离悬浮窗底部10px */
  /* 磨砂玻璃核心样式（保留） */
  background-color: rgba(255, 255, 255, 0.8); 
  backdrop-filter: blur(12px); 
  -webkit-backdrop-filter: blur(12px); 
  /* 增强质感（保留+微调） */
  border-radius: 8px; /* 新增圆角，适配边距后更美观 */
  border: 1px solid rgba(255, 255, 255, 0.5); /* 替换原border-top，全边框更协调 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); /* 微调阴影，适配边距后的层次感 */
  z-index: 10; 
  overflow: hidden;
}

.whiteboard-close {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background-color: rgba(0, 0, 0, 0.05);
  font-size: 24px;
  cursor: pointer;
  color: #333333;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.8);
}
.whiteboard-close:hover {
  color: #ff4444;
  transform: scale(1.1);
  background-color: rgba(255, 255, 255, 0.1);
}
/* 白板过渡动画 */
.whiteboard-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.whiteboard-fade-enter-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.whiteboard-fade-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.whiteboard-content {
  flex: 1; /* 占满白板剩余空间 */
  width: 100%;
  height: 100%;
  overflow: auto; /* 组件内容超出时滚动 */
}
</style>
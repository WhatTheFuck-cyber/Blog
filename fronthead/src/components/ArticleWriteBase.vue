<template>
  <!-- 文章编辑/创作页面通用布局基座：承载背景与核心内容容器 -->
  <div class="article-write-base">
    <!-- 核心内容容器：半透明白色毛玻璃面板，承载创作/编辑子组件 -->
    <div class="write-content-wrapper">
      <router-view />
    </div>
  </div>
</template>

<script setup>
/**
 * 文章创作/编辑页面布局基座组件
 * @description 提供全屏背景+居中毛玻璃内容容器，作为 ArticleCreate/ArticleRevise 组件的父布局
 * @feature 1. 背景图全屏固定且等比适配 2. 内容容器响应式适配不同屏幕 3. 毛玻璃视觉效果增强体验
 */
// 无需额外逻辑，仅作为布局基座
</script>

<style scoped>
/* 
 * 文章编辑布局样式总说明：
 * 1. 外层容器实现全屏背景图适配，保证不同屏幕下背景不拉伸变形
 * 2. 内容容器采用毛玻璃半透明效果，响应式适配大屏/小屏/手机端
 * 3. 核心属性优先级：适配性 > 视觉体验 > 细节样式
 */

/* 外层背景容器：全屏承载背景图，实现内容垂直水平居中 */
.article-write-base {
  width: 100%; /* 宽度铺满屏幕 */
  min-height: 100vh; /* 最小高度铺满视口，保证全屏展示 */
  background: url('@/assets/images/articleWriteBackground.png') no-repeat center center fixed; /* 背景图固定居中，不随滚动移动 */
  background-size: cover; /* 背景图等比缩放铺满容器，避免拉伸变形 */
  background-color: #f5f7fa; /* 背景图加载失败时的兜底底色 */
  display: flex; /* 弹性布局实现子容器居中 */
  justify-content: center; /* 子容器水平居中 */
  align-items: center; /* 子容器垂直居中 */
  padding: 1rem; /* 容器内边距，避免内容贴边 */
  box-sizing: border-box; /* 内边距计入宽高，防止容器溢出 */
}

/* 核心内容容器：半透明白色毛玻璃面板，承载创作/编辑组件 */
.write-content-wrapper {
  width: 90%; /* 大屏宽度占视口90% */
  max-width: 1400px; /* 大屏最大宽度限制，避免过宽 */
  min-height: 90vh; /* 大屏高度占视口90%，接近全屏 */
  background-color: rgba(255, 255, 255, 0.9); /* 90%不透明度的白色背景，半透明效果 */
  backdrop-filter: blur(8px); /* 毛玻璃模糊效果，增强视觉层次 */
  border-radius: 16px; /* 圆角设计，弱化直角生硬感 */
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); /* 轻微阴影，提升面板立体感 */
  padding: 3rem; /* 内部留白，保证内容与边框间距 */
  box-sizing: border-box; /* 内边距计入宽高，防止内容溢出 */
}

/* 响应式适配：平板/小屏设备 */
@media (max-width: 768px) {
  .write-content-wrapper {
    width: 95%; /* 小屏宽度占比提升至95% */
    min-height: 95vh; /* 小屏高度占比提升至95% */
    padding: 2rem; /* 减少内部留白，适配小屏 */
    border-radius: 12px; /* 缩小圆角，适配小屏视觉 */
  }
}

/* 响应式适配：手机端设备 */
@media (max-width: 480px) {
  .write-content-wrapper {
    width: 98%; /* 手机端几乎全屏，仅留少量边距 */
    min-height: 98vh; /* 手机端高度接近全屏 */
    padding: 1.5rem; /* 进一步减少留白，适配手机屏幕 */
  }
}
</style>
<template>
  <!-- 关于页面根容器：全屏布局，包含装饰条、核心内容卡片，集成侧边栏抽屉，整体浅灰背景+居中对齐 -->
  <div class="about-container">
    <!-- 顶部渐变装饰条：视觉分隔，提升页面层次感 -->
    <div class="about-header-decoration"></div>
    
    <!-- 核心内容卡片：承载标题、签名图、介绍文本、技术栈、源码链接，带渐入动画 -->
    <div class="about-card">
      <!-- 标题区：标题与签名图左右布局，垂直居中 -->
      <div class="title-wrapper">
        <h2 class="about-title">关于我们</h2>
        <img 
          src="@/assets/images/signature.png" 
          alt="个性签名" 
          class="signature-img"
        >
      </div>
      <!-- 标题下方渐变分隔线：强化标题区与内容区的视觉分隔 -->
      <div class="about-divider"></div>
      
      <!-- 主体内容区：包含博客介绍、开发目的、技术栈展示、源码链接 -->
      <div class="about-content">
        <p class="about-paragraph">
          本博客是一个基于 Vue3 + Vite 开发的个人博客系统，支持文章发布、分类浏览、点赞互动等功能。
        </p>
        <p class="about-paragraph">
          开发目的：用于展示个人技术文章、分享学习心得，同时实践前后端分离开发模式。
        </p>
        
        <!-- 技术栈展示模块：浅蓝背景卡片，带图标+hover交互 -->
        <div class="tech-stack-section">
          <p class="tech-stack-title">技术栈：</p>
          <ul class="tech-stack-list">
            <li class="tech-stack-item">
              <span class="tech-icon">💻</span>
              前端：Vue3、Vite、Vue Router、Pinia、Axios
            </li>
            <li class="tech-stack-item">
              <span class="tech-icon">⚙️</span>
              后端：FastAPI
            </li>
            <li class="tech-stack-item">
              <span class="tech-icon">🗄️</span>
              数据库：sqlite
            </li>
          </ul>
        </div>
        
        <!-- 源码链接模块：带图标+hover渐变交互的外链 -->
        <div class="source-link-section">
          <p class="about-paragraph">
            源码地址：
            <a 
              href="https://github.com/WhatTheFuck-cyber/Blog" 
              target="_blank" 
              class="source-link"
            >
              <span class="link-icon">🔗</span>
              github:WhatTheFuck-cyber/Blog
            </a>
          </p>
        </div>
      </div>
    </div>
    
    <!-- 底部渐变装饰条：与顶部呼应，完成页面视觉闭环 -->
    <div class="about-footer-decoration"></div>
  </div>
</template>

<script setup>
/**
 * 关于页面组件
 * @description 展示博客系统介绍、开发目的、技术栈、源码链接的静态页面，集成侧边栏抽屉，带渐入动画和响应式适配
 * @feature 1. 核心内容卡片渐入动画（挂载后触发） 2. 渐变装饰条提升视觉层次感 3. 技术栈模块hover交互反馈 4. 源码链接渐变hover效果 5. 多维度响应式适配（768px/480px断点） 6. 签名图自适应缩放
 * @dependencies SidebarDrawer - 侧边栏抽屉组件
 */
import { onMounted } from 'vue'


/**
 * 组件挂载钩子
 * @description 1. 打印挂载日志便于调试 2. 触发内容卡片渐入动画，提升页面加载体验
 * @returns {void}
 */
onMounted(() => {
  console.log('About page mounted') // 调试日志：标记页面挂载完成
  // 为内容卡片添加渐入动画类，触发动画
  document.querySelector('.about-card').classList.add('fade-in')
})
</script>

<style scoped>
/* 
 * 关于页面样式总说明：
 * 1. 整体采用居中布局+浅灰背景，核心内容卡片白色底+阴影提升层级
 * 2. 装饰条/分隔线使用渐变样式，强化视觉层次感
 * 3. 交互元素（技术栈项/源码链接）添加hover反馈，提升体验
 * 4. 多断点响应式适配（768px/480px），适配平板/手机端
 * 5. 内容卡片默认隐藏，挂载后触发渐入动画，优化加载体验
 * 6. 核心优先级：视觉层次感 > 交互体验 > 响应式兼容 > 细节美化
 */

/* 标题区布局：Flex实现标题与签名图左右对齐、垂直居中，底部间距分隔 */
.title-wrapper {
  display: flex; /* Flex布局 */
  align-items: center; /* 垂直居中 */
  justify-content: space-between; /* 左右两端对齐 */
  margin-bottom: 0.5rem; /* 底部间距，与分隔线区分 */
}

/* 签名图片样式：自适应高度，最大宽度限制，响应式缩放 */
.signature-img {
  height: 6rem; /* 基础高度 */
  width: auto; /* 宽度自适应，保持比例 */
  max-width: 500px; /* 最大宽度限制，防止溢出 */
  object-fit: contain; /* 保持图片比例，不拉伸 */
  opacity: 0.9; /* 轻微透明，弱化视觉权重 */
}

/* 根容器：全屏最小高度，居中布局，浅灰背景，统一字体 */
.about-container {
  min-height: 100vh; /* 最小高度铺满视口 */
  padding: 2rem 1rem; /* 上下2rem，左右1rem内边距 */
  background-color: #f8f9fa; /* 浅灰背景，提升阅读舒适度 */
  display: flex; /* Flex布局 */
  flex-direction: column; /* 垂直排列子元素 */
  align-items: center; /* 水平居中 */
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; /* 多字体降级，适配不同系统 */
}

/* 顶部/底部装饰条：渐变样式，视觉分隔，统一宽度/高度/圆角 */
.about-header-decoration,
.about-footer-decoration {
  width: 80%; /* 宽度80%，与内容卡片匹配 */
  max-width: 800px; /* 最大宽度限制，适配大屏 */
  height: 8px; /* 装饰条高度 */
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); /* 蓝紫渐变，提升视觉效果 */
  border-radius: 4px; /* 圆角，弱化直角 */
  margin: 0.5rem 0; /* 上下间距 */
  opacity: 0.8; /* 轻微透明，避免视觉过重 */
}
.about-footer-decoration {
  margin-top: 1rem; /* 底部装饰条顶部间距加大，与卡片区分 */
}

/* 核心内容卡片：默认隐藏（动画准备），白色底+阴影+圆角，适配宽度 */
.about-card {
  width: 100%; /* 宽度100% */
  max-width: 800px; /* 最大宽度限制，适配大屏 */
  background: #ffffff; /* 白色背景，提升内容可读性 */
  border-radius: 16px; /* 大圆角，现代感 */
  box-shadow: 0 8px 24px rgba(129, 140, 153, 0.1); /* 轻微阴影，提升层级 */
  padding: 2.5rem 2rem; /* 内边距，控制内容间距 */
  margin: 1rem 0; /* 上下间距 */
  transform: translateY(20px); /* 初始向下偏移20px（动画准备） */
  opacity: 0; /* 初始透明（动画准备） */
  transition: all 0.6s ease-out; /* 所有属性过渡动画，0.6秒缓出，动画更丝滑 */
}

/* 卡片渐入动画：触发后恢复原位+完全显示 */
.fade-in {
  transform: translateY(0); /* 恢复默认位置 */
  opacity: 1; /* 完全显示 */
}

/* 标题样式：大号字体+深灰色+底部内边距，强化视觉层级 */
.about-title {
  font-size: 2rem; /* 大号字体，突出标题 */
  color: #2d3748; /* 深灰色，提升可读性 */
  margin: 0 0 1rem 0; /* 清除上下边距，保留底部间距 */
  font-weight: 600; /* 字体加粗，强化标题 */
  position: relative; /* 为伪元素/装饰预留定位基准 */
  padding-bottom: 0.5rem; /* 底部内边距，与分隔线区分 */
}

/* 标题下方分隔线：短渐变横线，强化标题与内容的视觉分隔 */
.about-divider {
  height: 2px; /* 分隔线高度 */
  width: 60px; /* 短横线，避免视觉过长 */
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); /* 与装饰条同渐变，保持风格统一 */
  border-radius: 1px; /* 圆角，弱化直角 */
  margin-bottom: 2rem; /* 底部间距，与内容区分 */
}

/* 内容区：字体大小+行高+浅灰色，提升阅读体验 */
.about-content {
  color: #4a5568; /* 浅灰色，降低视觉疲劳 */
  line-height: 1.8; /* 加大行高，提升阅读舒适度 */
  font-size: 1.05rem; /* 字体微放大，适配阅读 */
}

/* 段落样式：文本两端对齐+底部间距，提升排版整洁度 */
.about-paragraph {
  margin-bottom: 1.5rem; /* 底部间距，区分段落 */
  text-align: justify; /* 文本两端对齐，提升排版美观度 */
}

/* 技术栈模块：浅蓝背景+圆角+内边距，区分内容模块 */
.tech-stack-section {
  margin: 2rem 0; /* 上下间距，与段落区分 */
  padding: 1.5rem; /* 内边距，控制内容间距 */
  background-color: #f0f4f8; /* 浅蓝背景，区分模块 */
  border-radius: 12px; /* 圆角，现代感 */
}

/* 技术栈标题：加粗+深灰色+底部间距，强化模块标题 */
.tech-stack-title {
  font-weight: 600; /* 字体加粗 */
  color: #2d3748; /* 深灰色，提升可读性 */
  margin-bottom: 1rem; /* 底部间距，与列表区分 */
  font-size: 1.1rem; /* 字体微放大，突出标题 */
}

/* 技术栈列表：清除默认样式，自定义内边距 */
.tech-stack-list {
  margin: 0; /* 清除默认外边距 */
  padding-left: 1rem; /* 左侧内边距，避免内容贴边 */
  list-style: none; /* 清除默认列表样式 */
}

/* 技术栈列表项：Flex布局+hover交互+白色背景+圆角，提升交互体验 */
.tech-stack-item {
  margin-bottom: 0.8rem; /* 底部间距，区分列表项 */
  padding: 0.8rem 1rem; /* 内边距，扩大点击热区（视觉） */
  background-color: #ffffff; /* 白色背景，突出列表项 */
  border-radius: 8px; /* 圆角，现代感 */
  transition: all 0.3s ease; /* 过渡动画，交互更丝滑 */
  display: flex; /* Flex布局，对齐图标和文本 */
  align-items: center; /* 垂直居中 */
}
.tech-stack-item:hover {
  transform: translateX(5px); /* hover时轻微右移，灵动效果 */
  box-shadow: 0 4px 12px rgba(129, 140, 153, 0.1); /* hover时添加阴影，提升层级 */
}

/* 技术栈图标：固定宽度+居中，保证对齐一致性 */
.tech-icon {
  font-size: 1.2rem; /* 图标放大，提升视觉效果 */
  margin-right: 0.8rem; /* 右侧间距，与文本区分 */
  width: 24px; /* 固定宽度，保证所有图标对齐 */
  text-align: center; /* 图标居中，提升美观度 */
}

/* 源码链接模块：顶部间距，与技术栈模块区分 */
.source-link-section {
  margin-top: 2rem; /* 顶部间距，区分模块 */
}

/* 源码链接样式：渐变hover+Flex布局+圆角，提升交互体验 */
.source-link {
  color: #667eea; /* 主题色文字，突出链接 */
  text-decoration: none; /* 清除默认下划线 */
  padding: 0.4rem 0.8rem; /* 内边距，扩大点击热区 */
  border-radius: 6px; /* 圆角，现代感 */
  transition: all 0.3s ease; /* 过渡动画，交互更丝滑 */
  display: inline-flex; /* Flex布局，对齐图标和文本 */
  align-items: center; /* 垂直居中 */
}
.source-link:hover {
  background-color: #667eea; /* hover时背景变主题色 */
  color: #ffffff; /* hover时文字变白，对比鲜明 */
  text-decoration: none; /* 清除下划线 */
  transform: translateY(-2px); /* hover时轻微上移，灵动效果 */
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); /* hover时添加渐变阴影，提升视觉效果 */
}

/* 链接图标：右侧间距，与文本区分 */
.link-icon {
  margin-right: 0.5rem; /* 右侧间距，避免图标与文本重叠 */
}

/* 响应式适配：平板端（≤768px） */
@media (max-width: 768px) {
  .about-card {
    padding: 2rem 1.5rem; /* 缩小内边距，适配小屏 */
  }
  .about-title {
    font-size: 1.7rem; /* 标题缩小，适配小屏 */
  }
  .about-content {
    font-size: 1rem; /* 内容字体缩小，适配小屏 */
  }
  .tech-stack-section {
    padding: 1rem; /* 技术栈模块内边距缩小 */
  }
  /* 签名图响应式调整：缩小高度和最大宽度 */
  .signature-img {
    height: 4rem; /* 高度缩小 */
    max-width: 120px; /* 最大宽度限制，适配小屏 */
  }
}

/* 响应式适配：手机端（≤480px） */
@media (max-width: 480px) {
  .about-container {
    padding: 1rem 0.5rem; /* 根容器内边距进一步缩小 */
  }
  .about-card {
    padding: 1.5rem 1rem; /* 内容卡片内边距缩小 */
    border-radius: 12px; /* 圆角缩小，适配小屏视觉 */
  }
  .tech-stack-item {
    padding: 0.6rem 0.8rem; /* 技术栈列表项内边距缩小 */
    font-size: 0.95rem; /* 字体缩小，适配小屏 */
  }
}
</style>
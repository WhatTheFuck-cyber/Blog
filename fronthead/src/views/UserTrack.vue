<template>
  <!-- 根容器：用户互动轨迹（点赞/收藏）总容器，限制最大宽度+居中+响应式内边距，保证布局规整 -->
  <div class="user-track-container">
    <!-- 我的点赞板块：展示用户点赞的文章列表，包含空状态、展开/收起功能，仅展示基础信息（标题/作者/发布时间） -->
    <section class="track-section">
      <h2>我的点赞</h2>
      <!-- 空状态：无点赞文章时显示，反馈无内容状态，提升用户感知 -->
      <div class="empty-tip" v-if="userInfoStore.likeArticles.length === 0">
        暂无点赞的文章
      </div>
      <!-- 点赞文章列表：复用userInfoStore的likeArticles数据，支持展开/收起（默认显示前2条），优化长列表展示 -->
      <div class="article-list" v-else>
        <div 
          class="article-card" 
          v-for="article in (likeExpanded ? userInfoStore.likeArticles : userInfoStore.likeArticles.slice(0, 2))"
          :key="article.id"
        >
          <!-- 文章标题链接：跳转对应文章详情页（新窗口），标题为空时兜底（依赖后端保证非空） -->
          <a 
            :href="`/app/articles/${article.id}`" 
            class="article-title"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ article.title }}
          </a>
          <!-- 文章作者：展示内容创建者，提升信息完整性 -->
          <p class="author">作者：{{ article.owner_name }}</p>
          <!-- 发布时间：格式化展示，标准化时间呈现形式 -->
          <p class="publish-time">发布时间：{{ formatTime(article.created_at) }}</p>
        </div>
        <!-- 展开/收起按钮：仅当点赞文章数>2时显示，切换展开状态，优化列表展示体验 -->
        <button 
          class="expand-btn"
          v-if="userInfoStore.likeArticles.length > 2"
          @click="likeExpanded = !likeExpanded"
        >
          {{ likeExpanded ? '收起' : '展开更多' }}
        </button>
      </div>
    </section>

    <!-- 我的收藏板块：结构与点赞板块完全一致，展示用户收藏的文章列表 -->
    <section class="track-section">
      <h2>我的收藏</h2>
      <!-- 空状态：无收藏文章时显示 -->
      <div class="empty-tip" v-if="userInfoStore.collectArticles.length === 0">
        暂无收藏的文章
      </div>
      <!-- 收藏文章列表：复用userInfoStore的collectArticles数据，支持展开/收起 -->
      <div class="article-list" v-else>
        <div 
          class="article-card" 
          v-for="article in (collectExpanded ? userInfoStore.collectArticles : userInfoStore.collectArticles.slice(0, 2))"
          :key="article.id"
        >
          <a 
            :href="`/app/articles/${article.id}`" 
            class="article-title"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ article.title }}
          </a>
          <p class="author">作者：{{ article.owner_name }}</p>
          <p class="publish-time">发布时间：{{ formatTime(article.created_at) }}</p>
        </div>
        <!-- 展开/收起按钮：仅当收藏文章数>2时显示 -->
        <button 
          class="expand-btn"
          v-if="userInfoStore.collectArticles.length > 2"
          @click="collectExpanded = !collectExpanded"
        >
          {{ collectExpanded ? '收起' : '展开更多' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * 用户互动轨迹组件（点赞+收藏）
 * @description 基于userInfo Store实现的用户点赞/收藏文章展示组件，核心功能为展示用户互动过的文章列表，支持展开/收起长列表，包含空状态反馈，适配响应式布局，仅登录用户加载数据
 * @feature 1. 状态复用：直接使用userInfo Store的likeArticles/collectArticles数据，统一数据管理 2. 列表优化：默认显示前2条，展开/收起控制长列表展示，避免页面冗余 3. 状态反馈：空状态提示，提升无内容时的用户体验 4. 数据加载：仅登录用户加载互动数据，且仅未获取时触发请求，避免重复请求 5. 时间格式化：标准化时间展示（年-月-日 时:分），兼容空值处理 6. 交互优化：卡片hover反馈、链接跳转新窗口、按钮hover变色 7. 响应式适配：移动端布局自适应，保证触控体验
 * @dependencies 
 *  - useUserInfoStore: 提供点赞/收藏文章数据，统一获取用户互动数据（fetchMyInteractions）
 *  - useUserStore: 校验用户登录状态，仅登录用户加载互动数据
 */
// 导入Vue核心API：响应式数据(ref)、生命周期钩子(onMounted)、类型定义(Ref)
import { ref, onMounted } from 'vue'
// 导入用户信息Store：复用点赞/收藏文章数据、互动数据获取方法
import { useUserInfoStore } from '@/store/userInfo'
// 导入用户登录状态Store：校验用户是否已登录，避免未登录用户加载无效数据
import { useUserStore } from '@/store/user'

/**
 * Store实例初始化
 * @type {ReturnType<typeof useUserInfoStore>} userInfoStore - 用户信息Store，提供点赞(likeArticles)/收藏(collectArticles)文章数据和互动数据获取方法(fetchMyInteractions)
 * @type {ReturnType<typeof useUserStore>} userStore - 用户登录状态Store，校验登录状态（isLoggedIn）
 */
const userInfoStore = useUserInfoStore()
const userStore = useUserStore()

/**
 * 响应式状态：控制列表展开/收起，默认false（收起，仅显示前2条）
 * @type {Ref<boolean>} likeExpanded - 点赞文章列表展开状态
 * @type {Ref<boolean>} collectExpanded - 收藏文章列表展开状态
 */
const likeExpanded = ref(false)
const collectExpanded = ref(false)

/**
 * 生命周期钩子：组件挂载时加载用户互动数据
 * @description 1. 校验用户登录状态（仅登录用户加载数据） 2. 校验互动数据是否已获取（my_likes/my_collects均为空时） 3. 调用fetchMyInteractions获取点赞/收藏数据，避免重复请求
 * @returns {void}
 */
onMounted(async () => {
  // 仅登录用户执行数据加载逻辑，防止未登录状态下的无效请求
  if (userStore.isLoggedIn) {
    // 校验互动数据是否未获取：点赞和收藏列表均为空时，主动获取
    if (!userInfoStore.my_likes.length && !userInfoStore.my_collects.length) {
      await userInfoStore.fetchMyInteractions()
    }
  }
})

/**
 * 时间格式化工具函数
 * @description 将后端返回的时间字符串格式化为「年-月-日 时:分」的标准化格式，空值返回"无"，保证展示统一且兼容异常数据
 * @param {string | undefined | null} timeStr - 原始时间字符串（如ISO格式）
 * @returns {string} 格式化后的时间字符串，空值返回"无"
 */
const formatTime = (timeStr) => {
  // 空值兜底：无时间字符串时返回"无"，避免页面显示空值
  if (!timeStr) return '无'
  const date = new Date(timeStr)
  // 补零处理：月份/日期/小时/分钟不足两位时补0，保证时间格式统一（如2025-05-01 09:05）
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}
</script>

<style scoped>
/* 
 * 用户互动轨迹组件样式总说明：
 * 1. 设计原则：轻量化展示（仅核心信息）+ 视觉分层（卡片/板块区分）+ 交互反馈（hover效果）+ 响应式适配（移动端/PC端）
 * 2. 视觉风格：毛玻璃卡片（backdrop-filter）+ 柔和阴影 + 主题蓝左边框（统一点赞/收藏板块视觉）+ 低饱和度文字层级，符合个人中心的简洁调性
 * 3. 交互体验：卡片hover上浮/变色、链接下划线/变色、展开/收起按钮hover加深，提升操作感知
 * 4. 兼容性：移动端布局自适应（减小内边距/卡片尺寸），保证触控体验；空状态居中展示，弱化无内容的负面感知
 * 5. 层级关系：板块标题（加粗+底边框）> 文章卡片（左边框+背景色）> 辅助信息（作者/时间低饱和度），视觉焦点清晰
 */

/* 根容器：限制最大宽度（1200px）+ 水平居中 + 响应式内边距，保证内容不超宽、适配不同屏幕 */
.user-track-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 互动板块通用样式：毛玻璃效果+内边距+阴影+底部间距，区分点赞/收藏板块，提升视觉层次感 */
.track-section {
  margin-bottom: 2.5rem; /* 板块间间距，保证呼吸感 */
  background-color: rgba(255, 255, 255, 0.85); /* 85%透明度白色，兼顾可读性与通透感 */
  backdrop-filter: blur(8px); /* 毛玻璃效果，匹配个人中心整体视觉风格 */
  padding: 1.8rem;
  border-radius: 12px; /* 大圆角，弱化硬朗感 */
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08); /* 柔和阴影，提升悬浮感 */
}

/* 板块标题：加粗+底边框+内边距，突出板块标识，区分内容区域 */
.track-section h2 {
  margin: 0 0 1.5rem;
  color: #2d3748; /* 深灰色主色调，保证可读性 */
  font-size: 1.5rem;
  font-weight: 600; /* 加粗，突出标题 */
  border-bottom: 1px solid #e8f4f8; /* 浅蓝分隔线，弱化视觉分割 */
  padding-bottom: 0.8rem;
}

/* 文章列表：纵向flex布局+固定间距，保证列表项排列整齐且有呼吸感 */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem; /* 列表项间距，避免拥挤 */
}

/* 文章卡片：主题蓝左边框+浅灰背景+hover反馈，统一点赞/收藏板块卡片样式，突出互动属性 */
.article-card {
  padding: 1.2rem;
  background-color: #f8fafc; /* 浅灰背景，区分板块主体 */
  border-radius: 8px;
  border-left: 3px solid #4299e1; /* 主题蓝左边框，标识互动类内容 */
  transition: all 0.2s ease; /* 所有属性过渡动画，保证hover效果流畅 */
}

/* 文章卡片hover：加深背景+轻微上浮+柔和阴影，模拟物理交互，强化操作反馈 */
.article-card:hover {
  background-color: #f1f5f9; /* 加深背景色，提升层次感 */
  transform: translateY(-2px); /* 向上偏移2px，模拟上浮 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); /* 新增柔和阴影，提升悬浮感 */
}

/* 文章标题链接：主题蓝+下划线+hover变色，符合链接视觉认知，保证可点击性 */
.article-title {
  color: #3182ce;
  text-decoration: underline; /* 下划线标识可点击 */
  font-size: 1.15rem;
  cursor: pointer;
  display: block; /* 块级展示，提升点击热区 */
  margin-bottom: 0.5rem;
}

/* 标题链接hover：深色蓝，强化交互反馈 */
.article-title:hover {
  color: #2b6cb0;
}

/* 作者信息：中灰色+适中字号，清晰展示且不抢占标题焦点 */
.author {
  color: #4a5568;
  font-size: 0.95rem;
  margin: 0 0 0.3rem;
}

/* 发布时间：浅灰色+小号字体，弱化展示，作为辅助信息不干扰核心内容 */
.publish-time {
  color: #718096;
  font-size: 0.9rem;
  margin: 0;
}

/* 展开/收起按钮：浅灰背景+hover加深，中性色调不抢占视觉焦点，仅作为列表控制工具 */
.expand-btn {
  padding: 0.5rem 1rem;
  background-color: #e2e8f0; /* 浅灰背景，中性色调 */
  border: none;
  border-radius: 6px;
  color: #2d3748;
  cursor: pointer;
  transition: background-color 0.2s ease;
  align-self: flex-start; /* 左对齐，符合阅读习惯 */
  margin-top: 0.5rem;
}

/* 展开/收起按钮hover：加深灰色，强化交互反馈 */
.expand-btn:hover {
  background-color: #cbd5e1;
}

/* 空状态提示：居中+浅灰背景+内边距，弱化无内容的负面感知，提升用户体验 */
.empty-tip {
  color: #718096;
  text-align: center;
  padding: 2rem 0;
  font-size: 1rem;
  background-color: #f8fafc;
  border-radius: 8px;
}

/* 移动端适配（768px以下）：减小内边距/卡片尺寸，适配小屏触控体验 */
@media (max-width: 768px) {
  /* 根容器：减小内边距，节省屏幕空间 */
  .user-track-container {
    padding: 1rem;
  }
  /* 板块：减小内边距，适配小屏 */
  .track-section {
    padding: 1.2rem;
  }
  /* 文章卡片：减小内边距，适配小屏触控 */
  .article-card {
    padding: 1rem;
  }
}
</style>
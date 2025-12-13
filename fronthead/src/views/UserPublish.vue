<template>
  <!-- 根容器：用户发布内容总容器，限制最大宽度+居中+响应式内边距，保证布局规整 -->
  <div class="user-publish-container">
    <!-- 我发布的文章板块：包含创作入口、加载/空状态、文章列表、展开收起、修改功能 -->
    <section class="publish-section">
      <!-- 板块头部：标题+立刻创作按钮，行布局（两端对齐），突出创作入口 -->
      <div class="section-header">
        <h2>我发布的文章</h2>
        <!-- 立刻创作按钮：跳转文章创作页，核心操作入口 -->
        <button class="create-btn" @click="goToCreateArticle">
          立刻创作
        </button>
      </div>

      <!-- 加载状态：仅在加载中且无文章时显示，提示用户等待 -->
      <div class="loading-tip" v-if="userInfoStore.isLoading && userInfoStore.articles.length === 0">
        加载中...
      </div>
      <!-- 空状态：非加载且无文章时显示，反馈无内容状态 -->
      <div class="empty-tip" v-else-if="userInfoStore.articles.length === 0">
        暂无发布的文章
      </div>
      <!-- 文章列表：复用userInfoStore的articles数据，支持展开/收起（默认显示前2条） -->
      <div class="article-list" v-else>
        <div 
          class="article-card" 
          v-for="article in (articleExpanded ? userInfoStore.articles : userInfoStore.articles.slice(0, 2))"
          :key="article.id"
        >
          <!-- 文章信息区域：标题（跳转详情）、发布时间、点赞/收藏数 -->
          <div class="article-info">
            <a 
              :href="`/app/articles/${article.id}`" 
              class="article-title"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ article.title || '无标题' }} <!-- 标题空值兜底 -->
            </a>
            <p class="publish-time">发布时间：{{ formatTime(article.created_at) }}</p>
            <p class="stats">点赞数：{{ article.like_count }} | 收藏数：{{ article.collect_count }}</p>
          </div>
          <!-- 修改创意按钮：每个文章卡片独立，跳转对应文章修改页（携带ID） -->
          <button 
            class="delete-btn" 
            @click="deleteArticle(article.id)"
          >
            删除
          </button>
          <button 
            class="revise-btn" 
            @click="goToReviseArticle(article.id)"
          >
            修改创意
          </button>
        </div>
        <!-- 展开/收起按钮：仅当文章数>2时显示，切换展开状态，优化列表展示 -->
        <button 
          class="expand-btn"
          v-if="userInfoStore.articles.length > 2"
          @click="articleExpanded = !articleExpanded"
        >
          {{ articleExpanded ? '收起' : '展开更多' }}
        </button>
      </div>
    </section>

    <!-- 我发布的评论板块：结构与文章板块一致，无创作/修改按钮，仅展示评论信息 -->
    <section class="publish-section">
      <h2>我发布的评论</h2>
      <!-- 加载状态：仅在加载中且无评论时显示 -->
      <div class="loading-tip" v-if="userInfoStore.isLoading && userInfoStore.comments.length === 0">
        加载中...
      </div>
      <!-- 空状态：非加载且无评论时显示 -->
      <div class="empty-tip" v-else-if="userInfoStore.comments.length === 0">
        暂无发布的评论
      </div>
      <!-- 评论列表：复用userInfoStore的comments数据，支持展开/收起（默认显示前2条） -->
      <div class="comment-list" v-else>
        <div 
          class="comment-card" 
          v-for="comment in (commentExpanded ? userInfoStore.comments : userInfoStore.comments.slice(0, 2))"
          :key="comment.id"
        >
          <!-- 关联文章链接：跳转对应文章详情页，标注文章ID -->
          <a 
            :href="`/app/articles/${comment.article_id}`" 
            class="article-title"
            target="_blank"
            rel="noopener noreferrer"
          >
            关联文章（ID：{{ comment.article_id }}）
          </a>
          <!-- 评论内容：空值兜底，保证布局完整 -->
          <p class="comment-content">评论内容：{{ comment.content || '无内容' }}</p>
          <!-- 发布时间：格式化展示 -->
          <p class="publish-time">发布时间：{{ formatTime(comment.created_at) }}</p>
        </div>
        <!-- 展开/收起按钮：仅当评论数>2时显示 -->
        <button 
          class="expand-btn"
          v-if="userInfoStore.comments.length > 2"
          @click="commentExpanded = !commentExpanded"
        >
          {{ commentExpanded ? '收起' : '展开更多' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
/**
 * 用户发布内容组件（文章+评论）
 * @description 基于userInfo Store实现的用户发布内容展示组件，核心功能为展示用户发布的文章/评论，支持创作新文章、修改已有文章、展开/收起长列表，包含加载/空状态反馈，适配响应式布局
 * @feature 1. 状态复用：直接使用userInfo Store的articles/comments/isLoading等状态，统一数据管理 2. 核心操作：立刻创作（跳转创作页）、修改创意（跳转修改页，携带文章ID） 3. 列表优化：默认显示前2条，展开/收起控制长列表展示 4. 状态反馈：加载/空状态提示，提升用户感知 5. 时间格式化：标准化时间展示（年-月-日 时:分） 6. 响应式适配：移动端卡片/按钮布局自适应 7. 交互优化：卡片hover反馈、按钮hover变色、链接跳转新窗口
 * @dependencies 
 *  - useUserInfoStore: 提供文章/评论数据、加载状态，统一获取用户发布内容
 *  - useUserStore: 校验用户登录状态，仅登录用户加载数据
 *  - useRouter: 实现创作/修改页的路由跳转
 */
// 导入Vue核心API：响应式数据(ref)、生命周期钩子(onMounted)
import { ref, onMounted } from 'vue'
// 导入用户信息Store：复用文章/评论数据、加载状态、数据获取方法
import { useUserInfoStore } from '@/store/userInfo'
// 导入用户登录状态Store：校验用户登录状态
import { useUserStore } from '@/store/user'
// 导入Vue Router：实现创作/修改页的编程式跳转
import { useRouter } from 'vue-router'
// 导入请求工具：实现文章删除请求
import request from '@/utils/request';

/**
 * 路由实例初始化
 * @type {import('vue-router').Router}
 * 用途：跳转文章创作页（/article/create）、文章修改页（/article/revise/:id）
 */
const router = useRouter()

/**
 * Store实例初始化
 * @type {ReturnType<typeof useUserInfoStore>} userInfoStore - 用户信息Store，提供文章/评论数据和加载状态
 * @type {ReturnType<typeof useUserStore>} userStore - 用户登录状态Store，校验登录状态
 */
const userInfoStore = useUserInfoStore()
const userStore = useUserStore()

/**
 * 响应式状态：控制列表展开/收起
 * @type {Ref<boolean>} articleExpanded - 文章列表展开状态，默认false（收起，显示前2条）
 * @type {Ref<boolean>} commentExpanded - 评论列表展开状态，默认false（收起，显示前2条）
 */
const articleExpanded = ref(false)
const commentExpanded = ref(false)

/**
 * 生命周期钩子：组件挂载时加载用户发布内容
 * @description 1. 校验用户登录状态 2. 若未获取用户ID（无基础信息），调用fetchAllUserInfo获取完整用户信息（含文章/评论） 3. 保证组件初始化时数据完整
 * @returns {void}
 */
onMounted(async () => {
  // 仅登录用户加载数据，避免无效请求
  if (userStore.isLoggedIn) {
    // 校验基础信息是否已加载，未加载则获取完整用户信息
    if (!userInfoStore.id) {
      await userInfoStore.fetchAllUserInfo()
    }
  }
})

/**
 * 时间格式化工具函数
 * @description 将后端返回的时间字符串格式化为「年-月-日 时:分」的标准化格式，空值返回"无"，保证展示统一
 * @param {string | undefined | null} timeStr - 原始时间字符串（如ISO格式）
 * @returns {string} 格式化后的时间字符串，空值返回"无"
 */
const formatTime = (timeStr) => {
  if (!timeStr) return '无'
  const date = new Date(timeStr)
  // 补零处理：月份/日期/小时/分钟不足两位时补0，保证格式统一
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

/**
 * 跳转文章创作页
 * @description 编程式路由跳转至/article/create，提供新文章创作入口
 * @returns {Promise<void>}
 */
const goToCreateArticle = () => {
  router.push('/article/create')
}

/**
 * 跳转文章修改页
 * @description 携带文章ID编程式路由跳转至/article/revise/:id，支持单篇文章修改
 * @param {number | string} articleId - 待修改文章的ID
 * @returns {Promise<void>}
 */
const goToReviseArticle = (articleId) => {
  console.log('从个人主页跳转到文章修改页，文章ID：', articleId)
  router.push(`/article/revise/${articleId}`)
}

/**
 * 删除文章
 * @description 确认删除后调用DELETE接口，成功后刷新文章列表
 * @param {number | string} articleId - 待删除文章的ID
 * @returns {Promise<void>}
 */
const deleteArticle = async (articleId) => {
  // 二次确认删除，防止误操作
  if (!confirm('确定要删除这篇文章吗？删除后无法恢复！')) return;
  
  try {
    // 调用DELETE接口
    await request.delete(`/articles/${articleId}`);
    // 提示删除成功
    alert('文章删除成功！');
    // 刷新用户发布的文章列表（复用Store的方法）
    await userInfoStore.fetchAllUserInfo();
  } catch (error) {
    console.error('删除文章失败：', error);
    alert('文章删除失败，请重试！');
  }
};
</script>

<style scoped>
/* 
 * 用户发布内容组件样式总说明：
 * 1. 设计原则：轻量化展示+核心操作突出（创作/修改）+ 视觉分层（卡片/状态色）+ 响应式适配（移动端/PC端）
 * 2. 视觉风格：毛玻璃卡片（backdrop-filter）+ 柔和阴影 + 主题色区分（文章青绿色/评论紫色）+ 按钮主题蓝/紫，符合个人中心的简洁调性
 * 3. 交互体验：卡片hover上浮/变色、按钮hover加深、链接下划线/变色、展开/收起控制长列表
 * 4. 兼容性：移动端卡片/按钮布局自适应（纵向排列），保证触控体验
 * 5. 层级关系：板块标题（加粗+底边框）> 卡片（左边框+背景色）> 操作按钮（高对比度），视觉焦点清晰
 */

/* 根容器：限制最大宽度+居中+响应式内边距，保证内容不超宽、居中展示 */
.user-publish-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 发布板块通用样式：毛玻璃效果+内边距+阴影+间距，区分不同板块，提升层次感 */
.publish-section {
  margin-bottom: 2.5rem;
  background-color: rgba(255, 255, 255, 0.85); /* 高透明度白色，兼顾可读性 */
  backdrop-filter: blur(8px); /* 毛玻璃效果，提升质感 */
  padding: 1.8rem;
  border-radius: 12px; /* 圆角弱化硬朗感 */
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08); /* 柔和阴影，提升悬浮感 */
}

/* 板块头部：标题+创作按钮行布局，两端对齐，突出创作入口 */
.section-header {
  display: flex;
  justify-content: space-between; /* 标题左，按钮右 */
  align-items: center; /* 垂直居中 */
  margin: 0 0 1.5rem;
}

/* 板块标题：加粗+底边框+内边距，突出板块标识，区分内容区域 */
.section-header h2, .publish-section h2 {
  margin: 0 0 1.5rem;
  color: #2d3748; /* 深灰色主色调，保证可读性 */
  font-size: 1.5rem;
  font-weight: 600;
  border-bottom: 1px solid #e8f4f8; /* 浅蓝分隔线，弱化视觉分割 */
  padding-bottom: 0.8rem;
  flex: 1; /* 标题占满左侧空间，按钮右对齐 */
}

/* 立刻创作按钮：主题蓝+圆角+hover加深，突出核心操作入口 */
.create-btn {
  padding: 0.6rem 1.2rem;
  background-color: #4299e1; /* 蓝色主色调，代表创作/新增 */
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease; /* 过渡动画，hover流畅 */
  font-size: 0.95rem;
}
/* 创作按钮hover：加深蓝色，强化交互反馈 */
.create-btn:hover {
  background-color: #3182ce;
}

/* 文章/评论列表：纵向布局+间距，保证列表项呼吸感 */
.article-list, .comment-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem; /* 列表项间距，避免拥挤 */
}

/* 文章卡片：flex布局（信息左，按钮右）+ 青绿色左边框+hover反馈，区分文章卡片 */
.article-card {
  padding: 1.2rem;
  background-color: #f8fafc; /* 浅灰背景，区分板块主体 */
  border-radius: 8px;
  border-left: 3px solid #38b2ac; /* 青绿色左边框，标识文章板块 */
  transition: all 0.2s ease; /* 所有属性过渡，hover流畅 */
  display: flex; /* 横向布局：信息+按钮 */
  justify-content: space-between; /* 内容左右分布 */
  align-items: center; /* 垂直居中 */
}

/* 文章信息区域：占满左侧空间，保证信息展示完整 */
.article-info {
  flex: 1;
}

/* 修改创意按钮：紫色系+圆角+hover加深，和评论板块边框呼应，区分创作按钮 */
.revise-btn {
  padding: 0.5rem 1rem;
  background-color: #9f7aea; /* 紫色系，代表修改/编辑 */
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  white-space: nowrap; /* 防止按钮文字换行，保证按钮完整性 */
  margin-left: 1rem; /* 和文章信息拉开距离，避免拥挤 */
}
/* 修改按钮hover：加深紫色，强化交互反馈 */
.revise-btn:hover {
  background-color: #805ad5;
}

/* 文章卡片hover：加深背景+轻微上浮+阴影，强化交互反馈 */
.article-card:hover {
  background-color: #f1f5f9;
  transform: translateY(-2px); /* 轻微上浮，模拟物理交互 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05); /* 柔和阴影，提升悬浮感 */
}

/* 评论卡片：紫色左边框+hover反馈，区分文章卡片，视觉统一 */
.comment-card {
  padding: 1.2rem;
  background-color: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #9f7aea; /* 紫色左边框，标识评论板块 */
  transition: all 0.2s ease;
}
/* 评论卡片hover：同文章卡片，保证交互体验统一 */
.comment-card:hover {
  background-color: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

/* 文章/关联文章链接：蓝色+下划线+hover变色，符合链接视觉认知 */
.article-title {
  color: #3182ce;
  text-decoration: underline;
  font-size: 1.15rem;
  cursor: pointer;
  display: block; /* 块级展示，保证点击热区 */
  margin-bottom: 0.5rem;
}
.article-title:hover {
  color: #2b6cb0; /* 深色蓝，强化hover反馈 */
}

/* 发布时间：浅灰+小号字体，弱化显示，不抢占内容焦点 */
.publish-time {
  color: #718096;
  font-size: 0.9rem;
  margin: 0 0 0.3rem;
}

/* 文章统计（点赞/收藏）：中灰+适中字号，清晰展示数据，不弱化 */
.stats {
  color: #4a5568;
  font-size: 0.95rem;
  margin: 0;
}

/* 评论内容：中灰+适中行高，提升长评论可读性 */
.comment-content {
  color: #4a5568;
  font-size: 0.95rem;
  margin: 0 0 0.3rem;
  line-height: 1.5; /* 宽松行高，提升阅读体验 */
}

/* 展开/收起按钮：浅灰背景+hover加深，弱化显示，不抢占操作焦点 */
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
.expand-btn:hover {
  background-color: #cbd5e1; /* 加深灰色，强化hover反馈 */
}

/* 空/加载状态提示：居中+浅灰背景+内边距，弱化无内容/加载的负面体验 */
.empty-tip, .loading-tip {
  color: #718096;
  text-align: center;
  padding: 2rem 0;
  font-size: 1rem;
  background-color: #f8fafc;
  border-radius: 8px;
}
/* 加载状态：蓝色文字，区分空状态，提示加载中 */
.loading-tip {
  color: #4299e1;
}

/* 删除按钮样式：红色背景，hover加深，与修改按钮间距 */
.delete-btn {
  padding: 0.6rem 1.2rem;
  background: #e53e3e; /* 红色主题 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-right: 0.8rem; /* 与修改按钮间距 */
}
.delete-btn:hover {
  background: #c53030; /* hover加深 */
}

/* 移动端适配（768px以下）：简化布局+调整卡片/按钮排列，适配触控体验 */
@media (max-width: 768px) {
  /* 根容器：减小内边距，节省屏幕空间 */
  .user-publish-container {
    padding: 1rem;
  }
  /* 板块：减小内边距，适配小屏 */
  .publish-section {
    padding: 1.2rem;
  }
  /* 文章卡片：改为纵向布局，按钮移至下方，适配小屏触控 */
  .article-card, .comment-card {
    padding: 1rem;
    flex-direction: column; /* 纵向布局 */
    align-items: flex-start; /* 左对齐，符合阅读习惯 */
  }
  /* 修改按钮：取消左间距，增加上间距，移至文章信息下方 */
  .revise-btn {
    margin-left: 0;
    margin-top: 0.8rem;
    align-self: flex-start; /* 左对齐，保证布局整齐 */
  }
  /* 删除按钮：移动端适配 */
  .delete-btn {
    margin-right: 0; /* 取消PC端的右间距 */
    margin-top: 0.8rem; /* 增加上间距，和修改按钮纵向排列 */
    align-self: flex-start; /* 左对齐，和修改按钮保持一致 */
  }
  /* 板块头部：改为纵向布局，创作按钮移至标题下方 */
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.8rem; /* 标题和按钮间距，避免拥挤 */
  }
  /* 创作按钮：左对齐，保证布局整齐 */
  .create-btn {
    align-self: flex-start;
  }
}
</style>
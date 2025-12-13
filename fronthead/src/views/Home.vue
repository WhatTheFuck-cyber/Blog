<template>
  <!-- 首页根容器：整合最新文章列表、分类列表两大核心模块，采用响应式网格布局，包含加载/错误/空状态提示，最大宽度居中展示 -->
  <div class="container">
    <!-- 最新文章区块：展示系统最新发布的文章列表，支持点赞/收藏互动、跳转详情页 -->
    <section class="section">
      <h2 class="section-title">最新文章</h2>
      <div class="section-divider"></div>

      <!-- 加载状态提示：文章数据加载中显示，提升用户等待体验 -->
      <div class="loading" v-if="articleStore.isLoading">正在加载中...</div>
      <!-- 错误提示：文章数据加载失败时显示错误信息 -->
      <div class="error-message" v-if="articleStore.error && !articleStore.isLoading">
        {{ articleStore.error }}
      </div>

      <!-- 最新文章列表：加载成功且无错误时显示，响应式网格布局 -->
      <div v-if="!articleStore.isLoading && !articleStore.error" class="article-grid">
        <div v-for="article in articleStore.latestArticleList" :key="article.id" class="article-card">
          <div class="article-card__header">
            <h3 class="article-card__title">{{ article.title }}</h3>
          </div>
          <!-- 文章元信息：展示作者/发布时间/点赞数/收藏数，空值兜底处理 -->
          <div class="article-card__meta">
            <span class="meta-item">作者：{{ article.owner_name || '未知' }}</span>
            <span class="meta-divider">|</span>
            <span class="meta-item">{{ formatDate(article.created_at) }}</span>
            <span class="meta-divider">|</span>
            <span class="meta-item like-count">
              <i class="like-icon">❤</i> {{ article.like_count || 0 }}
            </span>
            <span class="meta-divider">|</span>
            <span class="meta-item collect-count">
              <i class="collect-icon">⭐</i> {{ article.collect_count || 0 }}
            </span>
          </div>
          <!-- 文章操作区：阅读（跳转详情）、点赞/收藏（状态切换，未登录跳转登录） -->
          <div class="article-card__actions">
            <router-link 
              class="btn btn-read" 
              :to="{ name: 'article-detail', params: { id: article.id } }"
            >
              阅读
            </router-link>
            <button 
              class="btn btn-like" 
              @click="handleLike(article.id)"
              :class="{ 'liked': articleStore.isArticleLiked(article.id) }"
            >
              <i class="like-icon">❤</i> 
              {{ articleStore.isArticleLiked(article.id) ? '已点赞' : '点赞' }}
            </button>
            <button 
              class="btn btn-collect" 
              @click="handleCollect(article.id)"  
              :class="{ 'liked': articleStore.isArticleCollected(article.id) }"
            >
              <i class="collect-icon">⭐</i>
              {{ articleStore.isArticleCollected(article.id) ? '已收藏' : '收藏' }}
            </button>
          </div>
        </div>

        <!-- 空状态提示：无最新文章时显示，跨列居中，友好提示用户 -->
        <div v-if="articleStore.latestArticleList.length === 0" class="empty-state">
          还没有文章哦～
        </div>
      </div>
    </section>

    <!-- 分类区块：展示所有文章分类，点击跳转分类详情页 -->
    <section class="section">
      <div class="category-title-wrapper">
        <h2 class="section-title">分类</h2>
        <button 
          v-if="userStore.isLoggedIn"
          class="add-category-btn"
          @click="isCreateCategoryDialogShow = true"
        >
          +
        </button>
      </div>
      <div class="section-divider"></div>

      <!-- 分类列表：响应式网格布局，展示分类名称/描述/文章数 -->
      <div class="category-grid">
        <div v-for="category in articleStore.categoryList" :key="category.id" class="category-card">
          <router-link 
            :to="{ name: 'category', params: { id: category.id } }"
            class="category-link"
          >
            <span class="category-name">{{ category.name }}</span>
            <span class="category-desc">{{ category.description }}</span>
            <span class="category-count">{{ category.articles.length }} 篇文章</span>
          </router-link>
        </div>

        <!-- 空状态提示：无分类时显示，跨列居中 -->
        <div v-if="articleStore.categoryList.length === 0" class="empty-state">
          还没有分类哦～
        </div>
      </div>
    </section>

    <div class="category-dialog" v-if="isCreateCategoryDialogShow">
      <div class="dialog-content">
        <h3>创建新分类</h3>
        <div class="dialog-form">
          <label>分类名称：</label>
          <input 
            v-model="newCategoryName" 
            type="text" 
            placeholder="请输入分类名称（必填）" 
            maxlength="20"
          />
          <label>分类描述：</label>
          <textarea 
            v-model="newCategoryDesc" 
            placeholder="请输入分类描述（选填）" 
            maxlength="100"
          ></textarea>
        </div>
        <div class="dialog-btns">
          <button @click="isCreateCategoryDialogShow = false">取消</button>
          <button class="confirm-btn" @click="createCategory">确定创建</button>
        </div>
      </div>
    </div>

    <!-- 自定义全局提示框：居中偏上，自动消失 -->
    <div 
      v-if="showCustomToast" 
      class="custom-toast"
      :class="toastType === 'success' ? 'toast-success' : 'toast-error'"
    >
      {{ toastText }}
    </div>
  </div>
</template>

<script setup>
/**
 * 首页组件
 * @description 系统首页核心页面，展示最新文章列表（支持点赞/收藏互动、跳转详情）和文章分类列表（跳转分类详情），包含加载/错误/空状态处理，已登录用户加载点赞/收藏互动数据，未登录用户操作引导登录
 * @feature 1. 加载首页核心数据（最新文章、分类列表） 2. 文章列表响应式网格布局，支持点赞/收藏状态切换 3. 分类列表响应式网格布局，点击跳转分类详情 4. 未登录用户点赞/收藏引导登录 5. 加载/错误/空状态友好提示 6. 日期本地化格式化 7. 已登录用户加载个人互动数据（点赞/收藏记录）
 * @dependencies 
 *  - pinia (useArticleStore/useUserStore): 文章/分类/用户状态管理（加载数据、互动操作）
 *  - vue-router: 路由跳转（文章详情/分类详情/登录页）
 */
// 导入Vue核心API：生命周期（组件挂载）
import { onMounted, ref } from 'vue'
// 导入Vue Router实例：路由跳转（登录页/文章详情/分类详情）
import { useRouter } from 'vue-router'
// 导入Pinia状态管理：文章/分类数据与互动操作
import { useArticleStore } from '@/store/article'
// 导入Pinia状态管理：用户登录态判断
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

// 初始化核心实例
const articleStore = useArticleStore() // 文章/分类状态管理（加载数据、点赞/收藏操作）
const userStore = useUserStore() // 用户状态管理（登录态判断）
const router = useRouter() // 路由跳转（登录页/文章详情/分类详情）
const isCreateCategoryDialogShow = ref(false)
const newCategoryName = ref('') // 新分类名称
const newCategoryDesc = ref('') // 新分类描述

// 自定义提示框响应式数据
const showCustomToast = ref(false) // 提示框显示状态
const toastType = ref('success') // success/error
const toastText = ref('') // 提示文案
let toastTimer = null // 定时器，用于自动关闭

/**
 * 自定义提示框方法
 * @param {string} type - success/error
 * @param {string} text - 提示文案
 */
const showToast = (type, text) => {
  // 清除之前的定时器（避免多次触发叠加）
  if (toastTimer) clearTimeout(toastTimer)
  // 设置提示状态
  toastType.value = type
  toastText.value = text
  showCustomToast.value = true
  // 2秒后自动关闭
  toastTimer = setTimeout(() => {
    showCustomToast.value = false
  }, 2000)
}

/**
 * 日期格式化函数
 * @description 将ISO格式时间字符串转为中文本地化日期时间格式（年-月-日 时:分），空值返回"未知时间"
 * @param {string} dateString - 原始ISO时间字符串（如：2025-12-11T10:00:00Z）
 * @returns {string} 格式化后的时间字符串（如：2025/12/11 18:00）
 */
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 创建新分类
 * @description 校验名称非空 → 调用POST /categories接口 → 成功后刷新分类列表/关闭弹窗/提示 → 失败提示错误
 */
const createCategory = async () => {
  try {
    // 1. 表单校验：名称必填
    if (!newCategoryName.value.trim()) {
      showToast('error', '分类名称不能为空')
      return
    }

    // 2. 调用后端POST接口创建分类
    await request.post('/categories', {
      name: newCategoryName.value.trim(),
      description: newCategoryDesc.value.trim() || '' // 描述为空则传空字符串
    })

    // 3. 成功处理：提示 + 关闭弹窗+刷新分类列表+重置表单
    showToast('success', '分类创建成功')
    isCreateCategoryDialogShow.value = false
    // 刷新分类列表（复用store的获取首页数据方法）
    await articleStore.fetchHomeData()
    // 重置表单
    newCategoryName.value = ''
    newCategoryDesc.value = ''
  } catch (err) {
    // 4. 失败处理：提示错误
    showToast('error', '分类创建失败，请重试')
  }
}

/**
 * 处理文章点赞/取消点赞
 * @description 调用store切换点赞状态，提示操作结果；未登录时引导跳转登录页，错误时提示具体信息
 * @param {string|number} articleId - 要操作的文章ID
 * @returns {Promise<void>} 异步操作Promise
 */
const handleLike = async (articleId) => {
  try {
    const result = await articleStore.toggleLike(articleId)
    // 操作成功提示（区分点赞/取消点赞）
    showToast('success', result.isLiked ? '点赞成功' : '取消点赞成功')
  } catch (err) {
    // 未登录处理：提示并跳转登录页
    if (err.message.includes('请先登录')) {
      showToast('error', '请先登录后再进行点赞操作')
      router.push({ name: 'Login' })
    } else {
      // 其他错误提示
      showToast('error', err.message || '点赞失败')
    }
  }
}

/**
 * 处理文章收藏/取消收藏
 * @description 逻辑同点赞操作，仅切换收藏状态
 * @param {string|number} articleId - 要操作的文章ID
 * @returns {Promise<void>} 异步操作Promise
 */
const handleCollect = async (articleId) => {
  try {
    const result = await articleStore.toggleCollect(articleId)
    // 操作成功提示（区分收藏/取消收藏）
    showToast('success', result.isCollected ? '收藏成功' : '取消收藏成功')
  } catch (err) {
    // 未登录处理：提示并跳转登录页
    if (err.message.includes('请先登录')) {
      showToast('error', '请先登录后再进行收藏操作')
      router.push({ name: 'Login' })
    } else {
      // 其他错误提示
      showToast('error', err.message || '收藏失败')
    }
  }
}

/**
 * 生命周期：组件挂载
 * @description 页面首次加载时执行：1. 加载首页核心数据（最新文章、分类列表） 2. 已登录用户加载个人互动数据（点赞/收藏记录），保证互动状态正确展示
 */
onMounted(async () => {
  await articleStore.fetchHomeData() // 加载首页基础数据
  // 已登录用户加载互动数据（点赞/收藏记录）
  if (userStore.isLoggedIn) {
    await articleStore.fetchMyInteractions()
  }
})
</script>

<style scoped>
/* 
 * 首页样式总说明：
 * 1. 整体布局：最大宽度2000px居中，内边距适配不同屏幕，区块化展示（最新文章+分类）
 * 2. 响应式设计：768px以下网格改为单列，按钮垂直布局，标题字号缩小
 * 3. 交互体验：卡片hover上移+阴影加深，按钮/标题hover变色，点赞/收藏激活态差异化样式
 * 4. 状态提示：加载/错误/空状态差异化样式，空状态跨列居中，错误状态红色系，加载状态灰色系
 * 5. 视觉层级：标题深灰色突出，元信息浅灰色弱化，分隔线渐变强化区块分割
 */

/* 根容器：最大宽度2000px+水平居中+内边距，适配宽屏展示，盒模型包含内边距 */
.container {
  max-width: 2000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  width: 100%;
}

/* 区块通用样式：底部大间距+宽度100%，区分不同功能区块 */
.section {
  margin-bottom: 4rem;
  width: 100%;
}

/* 区块标题：字号+深灰色+字重+底部间距，突出区块层级 */
.section-title {
  font-size: 1.8rem;
  color: #2d3748;
  margin: 0 0 1rem;
  font-weight: 600;
}

/* 区块分隔线：渐变短横线+圆角，视觉分割标题与内容，强化区块边界 */
.section-divider {
  height: 3px;
  width: 80px;
  background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
  border-radius: 2px;
  margin-bottom: 2.5rem;
}

/* 最新文章网格：响应式自动填充列数（最小280px/列），统一间距，适配不同屏幕宽度 */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

/* 文章卡片：白色背景+轻微阴影+圆角+内边距+垂直布局+hover动画，提升交互质感 */
.article-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 1.8rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  width: 100%;
}
/* 卡片hover效果：轻微上移+阴影加深，强化可交互感知 */
.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

/* 文章标题：字号+深灰色+hover变色+行高，适配长标题展示，保留行数限制扩展空间 */
.article-card__title {
  font-size: 1.3rem;
  color: #2d3748;
  margin: 0 0 1.2rem;
  line-height: 1.4;
  transition: color 0.2s ease;
}
/* 标题hover变色：与阅读按钮颜色统一，视觉联动 */
.article-card:hover .article-card__title {
  color: #3498db;
}

/* 文章元信息：Flex布局+自动换行+浅灰色+小字号+间距，适配小屏展示，空值兜底 */
.article-card__meta {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #718096;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* 元信息分隔符：浅灰边框色+左右间距，弱化分割线视觉，提升可读性 */
.meta-divider {
  color: #cbd5e0;
  margin: 0 0.3rem;
}

/* 点赞图标：红色+右间距，视觉突出互动元素 */
.like-icon {
  color: #e53e3e;
  margin-right: 4px;
}
/* 收藏图标：橙色+右间距，与点赞图标区分，视觉突出 */
.collect-icon {
  color: #ed8936;
  margin-right: 4px;
}

/* 文章操作区：Flex布局+自动顶边距，按钮贴卡片底部，保证布局一致性 */
.article-card__actions {
  display: flex;
  gap: 0.8rem;
  margin-top: auto;
}

/* 按钮基础样式：统一内边距+圆角+过渡+无装饰+无边框，保证所有按钮样式一致性 */
.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  text-align: center;
  border: none;
}

/* 阅读按钮：蓝色背景+白色文字+自适应宽度，卡片内占满剩余空间，突出核心操作 */
.btn-read {
  background-color: #3498db;
  color: white;
  flex: 1;
}
/* 阅读按钮hover：背景色加深，强化交互反馈 */
.btn-read:hover {
  background-color: #2980b9;
}

/* 点赞按钮：基础样式（浅灰背景+深灰文字+浅边框）+ hover效果 + 激活态样式 */
.btn-like {
  background-color: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}
.btn-like:hover {
  background-color: #edf2f7;
  color: #2d3748;
}
/* 点赞激活态：浅红背景+红色文字+红边框，视觉区分已点赞状态 */
.btn-like.liked {
  background-color: #fef2f2;
  color: #e53e3e;
  border-color: #fecaca;
}

/* 收藏按钮：基础样式同点赞 + hover效果 + 激活态样式 */
.btn-collect {
  background-color: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}
.btn-collect:hover {
  background-color: #edf2f7;
  color: #2d3748;
}
/* 收藏激活态：浅橙背景+橙色文字+橙边框，视觉区分已收藏状态 */
.btn-collect.liked {
  background-color: #fffaf0;
  color: #ed8936;
  border-color: #fcd34d;
}

/* 分类网格：响应式自动填充列数（同文章网格），保证布局一致性 */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* 分类卡片：白色背景+轻微阴影+圆角+内边距+hover动画，与文章卡片视觉统一 */
.category-card {
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  transition: all 0.3s ease;
}
/* 分类卡片hover：轻微上移+阴影加深，强化可点击感知 */
.category-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.07);
}

/* 分类链接：去除下划线+垂直布局+间距，保证分类信息层级清晰 */
.category-link {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 分类名称：字号+字重+深灰色+hover变色，突出分类核心信息 */
.category-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  transition: color 0.2s ease;
}
/* 分类名称hover：与主题色统一，视觉联动 */
.category-card:hover .category-name {
  color: #3498db;
}

/* 分类描述：小字号+浅灰色+透明度，弱化次要信息 */
.category-desc {
  font-size: 0.85rem;
  color: #718096;
  opacity: 0.8;
  margin-top: 0.3rem;
}

/* 分类文章数：小字号+浅灰色，展示分类下文章数量 */
.category-count {
  font-size: 0.9rem;
  color: #718096;
}

/* 空状态提示：跨列居中+内边距+浅背景+虚线边框，友好提示无数据状态，视觉统一 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem 1rem;
  color: #718096;
  background-color: #f7fafc;
  border-radius: 10px;
  border: 1px dashed #e2e8f0;
}

/* 加载状态：跨列居中+内边距+灰色文字，弱化等待感知，统一布局 */
.loading {
  color: #666;
  padding: 3rem;
  text-align: center;
  grid-column: 1 / -1;
}

/* 错误提示：跨列居中+红色系（文字/边框/背景）+圆角，突出错误状态，提示用户 */
.error-message {
  color: #e74c3c;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid #fadbd8;
  border-radius: 8px;
  background-color: #fff5f5;
  grid-column: 1 / -1;
}

/* 响应式适配：768px以下（平板/手机） */
@media (max-width: 768px) {
  /* 文章/分类网格改为单列，适配小屏展示 */
  .article-grid,
  .category-grid {
    grid-template-columns: 1fr;
  }
  /* 区块标题字号缩小，适配小屏视觉 */
  .section-title {
    font-size: 1.5rem;
  }
  /* 文章操作区按钮垂直布局，避免横向空间不足 */
  .article-card__actions {
    flex-direction: column;
  }
}

/* 标题+加号按钮容器：Flex布局，对齐居中，间距适配 */
.category-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.8rem; /* 标题和加号的间距 */
}

/* 加号按钮：略小于分类标题，圆形，主题色背景，hover加深 */
.add-category-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  margin: 0 1rem 0.65rem;
}
.add-category-btn:hover {
  background-color: #2980b9;
}

/* 创建分类弹窗：遮罩层+居中内容，与现有样式视觉统一 */
.category-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.dialog-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
}
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}
.dialog-form input,
.dialog-form textarea {
  padding: 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 0.9rem;
}
.dialog-form textarea {
  min-height: 80px;
  resize: vertical;
}
.dialog-btns {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}
.dialog-btns button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}
.dialog-btns button:first-child {
  background: #e2e8f0;
  color: #4a5568;
}
.confirm-btn {
  background: #3498db;
  color: white;
}
.confirm-btn:hover {
  background: #2980b9;
}
</style>

<!-- 全局样式：自定义提示框（匹配文章详情页ElMessage样式） -->
<style>
/* 自定义提示框：瘦长扁平样式，与文章详情页ElMessage视觉统一 */
.custom-toast {
  position: fixed;
  top: 15%;
  left: 50%;
  transform: translate(-50%, 0);
  margin: 0 !important;
  z-index: 9999;
  background: #fff !important;
  opacity: 1 !important;
  border-radius: 4px;
  max-width: 280px;
  padding: 8px 16px !important;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  line-height: 1.4;
}

/* 成功提示：绿色边框+绿色文字 */
.custom-toast.toast-success {
  border: 1px solid #e6f7ed !important;
  color: #52c41a !important;
}

/* 失败提示：红色边框+红色文字 */
.custom-toast.toast-error {
  border: 1px solid #fff1f0 !important;
  color: #f5222d !important;
}
</style>
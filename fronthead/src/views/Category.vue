<template>
  <!-- 分类详情页根容器：整合加载/错误状态、分类基础信息、分类下文章列表、返回首页功能，复用首页布局风格，支持响应式适配 -->
  <div class="container">
    <!-- 加载状态提示：分类数据加载中显示，提升用户等待体验 -->
    <div class="loading" v-if="articleStore.isLoading">正在加载分类数据...</div>
    
    <!-- 错误提示 + 重新加载按钮：加载失败时显示错误信息，支持重新触发分类数据加载 -->
    <div class="error-message" v-if="articleStore.error && !articleStore.isLoading">
      {{ articleStore.error }}
      <button class="btn btn-reload" @click="fetchCategoryData">重新加载</button>
    </div>

    <!-- 分类内容区：加载成功且无错误、存在分类数据时显示，包含分类信息+文章列表+返回按钮 -->
    <div v-if="!articleStore.isLoading && !articleStore.error && articleStore.currentCategory">
      <!-- 分类基础信息区：展示分类名称/描述/创建时间/文章总数，底部分隔线区分模块 -->
      <div class="category-header">
        <h1 class="category-title">{{ articleStore.currentCategory.name || '未知分类' }}</h1>
        <p class="category-desc">{{ articleStore.currentCategory.description || '无描述' }}</p>
        <div class="category-meta">
          <span>创建时间：{{ formatDate(articleStore.currentCategory.created_at) }}</span>
          <span class="article-total">{{ articleStore.currentCategory.articles.length || 0 }} 篇文章</span>
        </div>
      </div>

      <!-- 分类下的文章列表区：对齐首页布局风格，包含标题/分隔线/网格布局/空状态 -->
      <section class="section">
        <h2 class="section-title">该分类下的文章</h2>
        <div class="section-divider"></div>

        <!-- 文章网格布局：响应式自动填充列数，适配不同屏幕宽度 -->
        <div class="article-grid">
          <div v-for="article in articleStore.currentCategory.articles || []" :key="article.id" class="article-card">
            <div class="article-card__header">
              <h3 class="article-card__title">{{ article.title }}</h3>
            </div>
            <!-- 文章元信息：仅展示作者/发布时间（移除点赞收藏，适配分类列表场景） -->
            <div class="article-card__meta">
              <span class="meta-item">作者：{{ article.owner_name || '未知' }}</span>
              <span class="meta-divider">|</span>
              <span class="meta-item">{{ formatDate(article.created_at) }}</span>
            </div>
            <div class="article-card__actions">
              <router-link 
                class="btn btn-read" 
                :to="{ name: 'article-detail', params: { id: article.id } }"
              >
                查看详情
              </router-link>
            </div>
          </div>
        </div>

        <!-- 空状态提示：分类下无文章时显示，跨列居中，友好提示用户 -->
        <div v-if="(articleStore.currentCategory.articles.length || 0) === 0" class="empty-state">
          该分类下暂无文章哦～
        </div>
      </section>

      <!-- 返回首页按钮：统一样式，点击跳转首页 -->
      <router-link class="btn btn-back" to="/app/home">返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
/**
 * 分类详情页组件
 * @description 展示指定分类的基础信息（名称/描述/创建时间/文章数）及该分类下的所有文章列表，包含加载/错误状态处理，复用首页布局风格，支持响应式适配
 * @feature 1. 从路由参数获取分类ID，加载分类详情数据 2. 分类信息展示（名称/描述/创建时间/文章总数） 3. 分类下文章列表网格布局（响应式） 4. 文章卡片点击跳转详情页 5. 空状态/加载/错误状态提示 6. 路由参数监听（ID变化重新加载） 7. 时间格式化（对齐首页逻辑）
 * @dependencies 
 *  - pinia (useArticleStore): 分类/文章状态管理（加载分类详情）
 *  - vue-router: 路由参数获取/文章详情跳转/返回首页
 */
// 导入Vue核心API：生命周期（挂载）、监听（路由参数变化）
import { onMounted, watch } from 'vue'
// 导入Vue Router：获取路由参数、路由跳转实例（保留便于扩展）
import { useRoute, useRouter } from 'vue-router'
// 导入Pinia状态管理：分类/文章数据与操作
import { useArticleStore } from '@/store/article'

// 初始化核心实例
const route = useRoute() // 当前路由实例（获取分类ID参数）
const router = useRouter() // 路由跳转实例（保留便于扩展，如返回首页/跳转文章详情）
const articleStore = useArticleStore() // 文章/分类状态管理（加载分类详情）

/**
 * 时间格式化函数
 * @description 将ISO时间字符串转为中文本地化格式（年/月/日 时/分），处理空值边界，对齐首页时间展示逻辑
 * @param {string} dateStr - 原始时间字符串（如ISO格式）
 * @returns {string} 格式化后的时间字符串（空值返回"未知时间"）
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '未知时间'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 获取分类详情数据
 * @description 从路由参数提取分类ID，调用store的fetchCategoryDetail方法加载分类详情（包含分类信息+旗下文章列表）
 * @returns {Promise<void>} 异步操作Promise
 */
const fetchCategoryData = async () => {
  await articleStore.fetchCategoryDetail(route.params.id)
}

/**
 * 生命周期：组件挂载
 * @description 页面首次加载时获取分类详情数据
 */
onMounted(() => {
  fetchCategoryData()
})

/**
 * 监听路由参数变化
 * @description 分类ID变化时重新加载详情（如从分类列表页跳转不同分类）
 */
watch(() => route.params.id, () => {
  fetchCategoryData()
})
</script>

<style scoped>
/* 
 * 分类详情页样式总说明：
 * 1. 复用首页布局风格（网格/卡片/按钮），保证视觉一致性
 * 2. 分类信息区：底部分隔线区分模块，元信息突出文章总数
 * 3. 文章列表：响应式网格布局（自动填充列数），卡片hover动画提升交互体验
 * 4. 空状态：跨列居中，虚线边框+浅背景，友好提示
 * 5. 加载/错误状态：差异化样式（错误红色系/加载灰色系）
 * 6. 响应式适配（768px以下）：网格单列、标题字号缩小、按钮垂直布局
 * 7. 核心优先级：视觉一致性 > 响应式适配 > 交互体验 > 状态提示
 */

/* 根容器：最大宽度2000px+居中+内边距，适配宽屏展示，复用首页容器样式 */
.container {
  max-width: 2000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  width: 100%;
}

/* 分类基础信息区：底部分隔线+上下间距，区分分类信息与文章列表模块 */
.category-header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}
/* 分类标题：字号+深灰色+字重+间距，突出层级 */
.category-title {
  font-size: 1.8rem;
  color: #2d3748;
  margin: 0 0 0.8rem;
  font-weight: 600;
}
/* 分类描述：浅灰色+字号+间距，次要信息弱化展示 */
.category-desc {
  font-size: 1rem;
  color: #718096;
  margin: 0 0 1rem;
}
/* 分类元信息：Flex布局+间距+浅灰色+字号，展示创建时间和文章总数 */
.category-meta {
  display: flex;
  gap: 1.5rem;
  color: #718096;
  font-size: 0.95rem;
}
/* 文章总数：蓝色突出显示，强调分类下文章数量 */
.article-total {
  color: #3498db;
}

/* 文章列表区块：底部大间距，保证与返回按钮的距离 */
.section {
  margin-bottom: 4rem;
  width: 100%;
}
/* 区块标题：字号+深灰色+字重+间距，与分类标题层级一致 */
.section-title {
  font-size: 1.8rem;
  color: #2d3748;
  margin: 0 0 1rem;
  font-weight: 600;
}
/* 区块分隔线：渐变短横线+圆角，视觉分割标题与列表 */
.section-divider {
  height: 3px;
  width: 80px;
  background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);
  border-radius: 2px;
  margin-bottom: 2.5rem;
}

/* 文章网格布局：响应式自动填充列数（最小280px/列），统一间距 */
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

/* 文章卡片：白色背景+轻微阴影+圆角+内边距+hover动画，提升交互质感 */
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
/* 卡片hover效果：轻微上移+阴影加深，强化可点击感知 */
.article-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}
/* 文章标题：行数限制（2行）+溢出隐藏+hover变色，适配长标题展示 */
.article-card__title {
  font-size: 1.3rem;
  color: #2d3748;
  margin: 0 0 1.2rem;
  line-height: 1.4;
  transition: color 0.2s ease;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
/* 标题hover变色：与查看按钮颜色统一，视觉联动 */
.article-card:hover .article-card__title {
  color: #3498db;
}

/* 文章元信息：Flex布局+换行+浅灰色+字号+间距，适配小屏展示 */
.article-card__meta {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: #718096;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}
/* 元信息分隔符：浅灰边框色+左右间距，弱化分割线视觉 */
.meta-divider {
  color: #cbd5e0;
  margin: 0 0.3rem;
}

/* 文章操作区：Flex布局+自动顶边距，按钮贴卡片底部 */
.article-card__actions {
  display: flex;
  gap: 0.8rem;
  margin-top: auto;
}
/* 按钮基础样式：统一内边距+圆角+过渡+无装饰，保证按钮样式一致性 */
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
/* 查看详情按钮：蓝色背景+白色文字+自适应宽度，卡片内占满剩余空间 */
.btn-read {
  background-color: #3498db;
  color: white;
  flex: 1;
}
/* 查看按钮hover：背景色加深，强化交互反馈 */
.btn-read:hover {
  background-color: #2980b9;
}
/* 重新加载/返回按钮：主蓝色背景+白色文字+上间距，与其他元素区分 */
.btn-reload, .btn-back {
  background: #4299e1;
  color: white;
  margin-top: 1rem;
}
/* 重新加载/返回按钮hover：背景色加深 */
.btn-reload:hover, .btn-back:hover {
  background: #3182ce;
}

/* 空状态提示：跨列居中+内边距+浅背景+虚线边框，友好提示无文章状态 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem 1rem;
  color: #718096;
  background-color: #f7fafc;
  border-radius: 10px;
  border: 1px dashed #e2e8f0;
}
/* 加载状态：居中+内边距+灰色文字，弱化等待感知 */
.loading {
  color: #666;
  padding: 3rem;
  text-align: center;
}
/* 错误提示：红色系（文字/边框/背景）+圆角+间距，突出错误状态 */
.error-message {
  color: #e74c3c;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid #fadbd8;
  border-radius: 8px;
  background-color: #fff5f5;
  margin-bottom: 1rem;
}

/* 响应式适配：768px以下（平板/手机） */
@media (max-width: 768px) {
  .article-grid {
    grid-template-columns: 1fr; /* 文章网格改为单列 */
  }
  .section-title {
    font-size: 1.5rem; /* 区块标题字号缩小 */
  }
  .article-card__actions {
    flex-direction: column; /* 卡片操作区按钮垂直布局 */
  }
  .category-title {
    font-size: 1.5rem; /* 分类标题字号缩小 */
  }
}
</style>
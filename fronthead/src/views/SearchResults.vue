<template>
  <!-- 搜索结果页根容器：响应式内边距+最大宽度限制（避免宽屏拉伸），承载所有搜索结果内容 -->
  <div class="container">
    <!-- 动态标题：根据是否有结果显示不同文案，强化用户搜索感知 -->
    <h2>
      {{ hasResults ? 
        `搜索结果: "${searchQuery}"` : 
        `没有找到与"${searchQuery}"相关的内容` 
      }}
    </h2>
    
    <!-- 加载状态提示：请求过程中显示，居中浅灰文案，弱化视觉冲击 -->
    <div class="loading" v-if="isLoading">加载中...</div>
    <!-- 错误提示：请求失败且非加载状态时显示，红色系警示样式，清晰反馈错误 -->
    <div class="error-message" v-if="error && !isLoading">{{ error }}</div>
    
    <!-- 核心结果展示区：非加载/非错误状态下渲染，区分作者/文章的单条/列表展示 -->
    <div v-if="!isLoading && !error">
      <!-- 作者结果展示区：区分列表（名称搜索）和单条（ID/邮箱搜索）两种形态 -->
      <!-- 作者列表（名称搜索结果）：多作者展示，循环渲染每个作者卡片 -->
      <div v-if="authorList.length > 0" class="results-list">
        <div v-for="author in authorList" :key="author.id" class="author-card">
          <h3>作者信息</h3>
          <p><strong>用户名：</strong>{{ author.username }}</p>
          <p><strong>邮箱：</strong>{{ author.email }}</p>
          <p><strong>账号状态：</strong>{{ author.is_active ? '已激活' : '未激活' }}</p>
          <p><strong>激活时间：</strong>{{ formatDate(author.activate_at) }}</p>

          <!-- 作者发布的文章列表：显示数量统计，无数据时提示"暂无文章" -->
          <div class="author-articles">
            <h4>发布的文章 ({{ author.articles?.length || 0 }})</h4>
            <div v-if="author.articles && author.articles.length">
              <div class="article-item" v-for="article in author.articles" :key="article.id">
                <a :href="`/app/articles/${article.id}`" target="_blank">{{ article.title }}</a>
                <div class="article-meta">
                  发布时间：{{ formatDate(article.created_at) }}
                </div>
              </div>
            </div>
            <div v-else>该作者暂无文章</div>
          </div>

          <!-- 作者发表的评论列表：显示数量统计，无数据时提示"暂无评论" -->
          <div class="author-comments">
            <h4>发表的评论 ({{ author.comments?.length || 0 }})</h4>
            <div v-if="author.comments && author.comments.length">
              <div class="comment-item" v-for="comment in author.comments" :key="comment.id">
                <div class="comment-content">{{ comment.content }}</div>
                <!-- 【优化点1】文章ID改为可点击链接，跳转对应文章详情页，提升交互连贯性 -->
                <div class="comment-meta">
                  文章ID：<a :href="`/app/articles/${comment.article_id}`" target="_blank" class="article-id-link">{{ comment.article_id }}</a> | 发布时间：{{ formatDate(comment.created_at) }}
                </div>
              </div>
            </div>
            <div v-else>该作者暂无评论</div>
          </div>
        </div>
      </div>

      <!-- 作者单条结果（ID/邮箱搜索）：单作者详情展示，结构与列表项一致保证视觉统一 -->
      <div v-if="authorSingle" class="author-card">
        <h3>作者信息</h3>
        <p><strong>用户名：</strong>{{ authorSingle.username }}</p>
        <p><strong>邮箱：</strong>{{ authorSingle.email }}</p>
        <p><strong>账号状态：</strong>{{ authorSingle.is_active ? '已激活' : '未激活' }}</p>
        <p><strong>激活时间：</strong>{{ formatDate(authorSingle.activate_at) }}</p>

        <div class="author-articles">
          <h4>发布的文章 ({{ authorSingle.articles?.length || 0 }})</h4>
          <div v-if="authorSingle.articles && authorSingle.articles.length">
            <div class="article-item" v-for="article in authorSingle.articles" :key="article.id">
              <a :href="`/app/articles/${article.id}`" target="_blank">{{ article.title }}</a>
              <div class="article-meta">
                发布时间：{{ formatDate(article.created_at) }}
              </div>
            </div>
          </div>
          <div v-else>该作者暂无文章</div>
        </div>

        <div class="author-comments">
          <h4>发表的评论 ({{ authorSingle.comments?.length || 0 }})</h4>
          <div v-if="authorSingle.comments && authorSingle.comments.length">
            <div class="comment-item" v-for="comment in authorSingle.comments" :key="comment.id">
              <div class="comment-content">{{ comment.content }}</div>
              <!-- 【优化点2】单条作者结果的评论文章ID也改为可点击链接，和列表版保持交互统一 -->
              <div class="comment-meta">
                文章ID：<a :href="`/app/articles/${comment.article_id}`" target="_blank" class="article-id-link">{{ comment.article_id }}</a> | 发布时间：{{ formatDate(comment.created_at) }}
              </div>
            </div>
          </div>
          <div v-else>该作者暂无评论</div>
        </div>
      </div>

      <!-- 文章结果展示区：区分列表（作者/标题/内容搜索）和单条（ID搜索）两种形态 -->
      <!-- 文章列表（作者/标题/内容搜索）：多文章展示，循环渲染每个文章卡片 -->
      <div v-if="articleList.length > 0" class="results-list">
        <div v-for="article in articleList" :key="article.id" class="article-card">
          <h3>{{ article.title }}</h3>
          <div class="article-meta">
            作者：{{ article.owner_name }} | 发布时间：{{ formatDate(article.created_at) }}
          </div>
          <!-- 渲染文章Markdown内容，适配代码高亮、排版等格式 -->
          <div class="article-body" v-html="renderArticleContent(article)"></div>

          <!-- 文章关联的评论列表：显示数量统计，无数据时提示"暂无评论" -->
          <div class="article-comments">
            <h4>评论 ({{ article.comments?.length || 0 }})</h4>
            <div v-if="article.comments && article.comments.length">
              <div class="comment-item" v-for="comment in article.comments" :key="comment.id">
                <div class="comment-author">{{ comment.user_name }}</div>
                <div class="comment-content">{{ comment.content }}</div>
                <!-- 【可选优化】文章下的评论增加「关联文章ID跳转」，强化内容关联 -->
                <div class="comment-meta">
                  发布时间：{{ formatDate(comment.created_at) }} | 
                  关联文章：<a :href="`/app/articles/${article.id}`" target="_blank" class="article-id-link">{{ article.id }}</a>
                </div>
              </div>
            </div>
            <div v-else>该文章暂无评论</div>
          </div>
        </div>
      </div>

      <!-- 文章单条结果（ID搜索）：单文章详情展示，结构与列表项一致保证视觉统一 -->
      <div v-if="articleSingle" class="article-card">
        <h3>{{ articleSingle.title }}</h3>
        <div class="article-meta">
          作者：{{ articleSingle.owner_name }} | 发布时间：{{ formatDate(articleSingle.created_at) }}
        </div>
        <div class="article-body" v-html="renderArticleContent(articleSingle)"></div>

        <div class="article-comments">
          <h4>评论 ({{ articleSingle.comments?.length || 0 }})</h4>
          <div v-if="articleSingle.comments && articleSingle.comments.length">
            <div class="comment-item" v-for="comment in articleSingle.comments" :key="comment.id">
              <div class="comment-author">{{ comment.user_name }}</div>
              <div class="comment-content">{{ comment.content }}</div>
              <!-- 【可选优化】单篇文章下的评论增加关联文章跳转，保持交互一致性 -->
              <div class="comment-meta">
                发布时间：{{ formatDate(comment.created_at) }} | 
                关联文章：<a :href="`/app/articles/${articleSingle.id}`" target="_blank" class="article-id-link">{{ articleSingle.id }}</a>
              </div>
            </div>
          </div>
          <div v-else>该文章暂无评论</div>
        </div>
      </div>

      <!-- 无结果提示：无任何作者/文章结果时显示，引导用户更换关键词/搜索类型 -->
      <div v-if="!hasResults" class="no-results">
        没有找到相关结果，请尝试其他关键词或搜索类型。
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 搜索结果页组件
 * @description 系统核心搜索结果展示页面，支持多维度搜索（作者ID/邮箱/名称、文章ID/作者/标题/内容），区分单条/列表结果展示，适配Markdown文章渲染（含代码高亮），提供加载/错误/无结果状态反馈，支持移动端响应式适配
 * @feature 1. 多策略搜索结果适配（作者/文章的单条/列表区分） 2. Markdown文章渲染（代码高亮、GFM语法支持） 3. 日期格式化处理（兼容异常日期） 4. 交互优化（文章ID可跳转、hover反馈） 5. 状态管理（加载/错误/无结果） 6. 路由监听（URL参数变化自动重新搜索） 7. 响应式布局（适配移动端/PC端） 8. 视觉统一（单条/列表结果样式一致）
 * @dependencies 
 *  - vue-router: 监听路由参数（搜索关键词/策略）、生成文章跳转链接
 *  - request工具：发送搜索接口请求
 *  - marked: 解析Markdown文章内容
 *  - highlight.js: 实现代码高亮渲染
 */
// 导入Vue核心API：响应式数据(ref)、计算属性(computed)、路由监听(watch)
import { ref, computed, watch } from 'vue'
// 导入Vue Router：监听路由参数（搜索关键词q、搜索策略s）
import { useRoute } from 'vue-router'
// 导入请求工具：发送搜索接口请求
import request from '@/utils/request'
// 导入Markdown解析库：渲染文章内容
import { marked } from 'marked'
// 导入代码高亮库：实现Markdown代码块高亮
import hljs from 'highlight.js'
// 导入代码高亮样式：保证高亮视觉效果
import 'highlight.js/styles/default.css'

// 初始化路由实例：监听URL中的搜索参数
const route = useRoute()

/**
 * 响应式数据定义（区分单条/列表，适配不同搜索策略）
 * @type {Ref<object | null>} authorSingle - 单条作者结果（ID/邮箱搜索），初始null
 * @type {Ref<Array>} authorList - 作者列表结果（名称搜索），初始空数组
 * @type {Ref<object | null>} articleSingle - 单条文章结果（ID搜索），初始null
 * @type {Ref<Array>} articleList - 文章列表结果（作者/标题/内容搜索），初始空数组
 * @type {Ref<string>} searchQuery - 搜索关键词，同步URL中的q参数
 * @type {Ref<object | null>} searchStrategy - 搜索策略对象，同步URL中的s参数（解码后）
 * @type {Ref<boolean>} isLoading - 搜索请求加载状态，控制加载提示显示
 * @type {Ref<string>} error - 搜索错误提示文案，请求失败时赋值
 */
const authorSingle = ref(null)
const authorList = ref([])
const articleSingle = ref(null)
const articleList = ref([])
const searchQuery = ref('')
const searchStrategy = ref(null)
const isLoading = ref(false)
const error = ref('')

/**
 * Markdown配置：启用代码高亮、GFM语法、换行支持等，保证文章渲染效果
 * 核心配置：代码高亮使用highlight.js，支持多语言，未知语言默认plaintext
 */
marked.setOptions({
  // 代码高亮处理函数
  highlight: function (code, lang) {
    // 校验语言合法性，未知语言使用plaintext
    const validLang = hljs.getLanguage(lang) ? lang : 'plaintext'
    // 调用highlight.js高亮代码
    return hljs.highlight(code, { language: validLang }).value
  },
  gfm: true, // 启用GitHub风格的Markdown
  breaks: true, // 支持换行符转换为<br>
  headerIds: false, // 禁用标题自动生成ID
  mangle: false // 禁用链接标签混淆
})

/**
 * 计算属性：判断是否有搜索结果（作者/文章的单条/列表任一有值即判定有结果）
 * @returns {boolean} 有结果返回true，无结果返回false
 */
const hasResults = computed(() => {
  return authorSingle.value !== null 
    || authorList.value.length > 0 
    || articleSingle.value !== null 
    || articleList.value.length > 0
})

/**
 * 渲染文章Markdown内容（适配单条/列表文章项）
 * @param {object} article - 文章对象（含content字段）
 * @returns {string} 解析后的HTML字符串，无内容时返回"暂无文章内容"提示
 */
const renderArticleContent = (article) => {
  if (!article || !article.content) {
    return '<p class="no-content">暂无文章内容</p>'
  }
  // 解析Markdown为HTML并返回
  return marked.parse(article.content)
}

/**
 * 日期格式化工具函数（兼容异常日期字符串）
 * @param {string} dateString - 原始日期字符串
 * @returns {string} 格式化后的本地日期字符串，异常时返回"未知时间"
 */
const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  try {
    // 转换为本地日期格式
    return new Date(dateString).toLocaleString()
  } catch (e) {
    // 捕获日期解析异常，返回兜底文案
    return '未知时间'
  }
}

/**
 * 判断是否为列表型搜索策略（区分列表/单条结果展示）
 * @param {string} strategyValue - 搜索策略值（如authors/name、articles/id）
 * @returns {boolean} 列表型策略返回true，单条型返回false
 */
const isListStrategy = (strategyValue) => {
  // 定义列表型策略集合（名称/作者/标题/内容搜索返回列表）
  const listStrategies = [
    'authors/name',    // 作者名称搜索 → 列表
    'articles/author', // 文章作者搜索 → 列表
    'articles/title',  // 文章标题搜索 → 列表
    'articles/content' // 文章内容搜索 → 列表
  ]
  return listStrategies.includes(strategyValue)
}

/**
 * 核心搜索逻辑：从路由参数获取关键词/策略，发送请求并分配结果（单条/列表）
 * @async 异步方法（发送HTTP请求）
 * @description 1. 重置前置状态（结果/错误/加载） 2. 校验路由参数（q/s） 3. 解码搜索策略并校验 4. 发送搜索请求（超时10s） 5. 根据策略分配结果（作者/文章的单条/列表） 6. 异常处理（区分404/网络/未知错误） 7. 最终结束加载状态
 * @returns {Promise<void>}
 */
const fetchResultsFromRoute = async () => {
  // 从路由参数获取搜索关键词(q)和策略(s)
  const { q, s } = route.query

  // 重置所有状态（避免旧结果干扰）
  authorSingle.value = null
  authorList.value = []
  articleSingle.value = null
  articleList.value = []
  error.value = ''
  isLoading.value = true

  // 无关键词/策略时，直接结束加载
  if (!q || !s) {
    isLoading.value = false
    return
  }

  try {
    // 解码搜索策略（URL编码后的JSON字符串）
    const strategy = JSON.parse(decodeURIComponent(s))
    // 校验策略有效性
    if (!strategy?.value) {
      error.value = '无效的搜索类型'
      isLoading.value = false
      return
    }

    // 编码搜索关键词（避免特殊字符导致请求异常）
    const keyword = encodeURIComponent(q.trim())
    // 拼接请求URL（搜索策略+关键词）
    const url = `/search/${strategy.value}/${keyword}`
    console.log('搜索请求URL:', url)

    // 发送搜索请求（超时10秒）
    const response = await request.get(url, { timeout: 10000 })
    // 兼容不同响应格式（直接返回data或整个response）
    const data = response.data || response

    // 根据搜索策略分配结果（作者/文章，单条/列表）
    if (strategy.value.startsWith('authors/')) {
      if (isListStrategy(strategy.value)) {
        // 作者名称搜索 → 列表（确保是数组，兼容后端返回单条的情况）
        authorList.value = Array.isArray(data) ? data : [data]
      } else {
        // 作者ID/邮箱搜索 → 单条
        authorSingle.value = data
      }
    } else if (strategy.value.startsWith('articles/')) {
      if (isListStrategy(strategy.value)) {
        // 文章作者/标题/内容搜索 → 列表（确保是数组）
        articleList.value = Array.isArray(data) ? data : [data]
      } else {
        // 文章ID搜索 → 单条
        articleSingle.value = data
      }
    }

    // 同步搜索关键词和策略到响应式数据
    searchQuery.value = q
    searchStrategy.value = strategy

  } catch (err) {
    // 异常处理：区分不同错误类型显示提示
    console.error('搜索请求失败:', err)
    // 404错误清空提示（无结果由hasResults判定），其他错误显示对应文案
    error.value = err.response?.status === 404 ? '' : `加载失败: ${err.message || '未知错误'}`
  } finally {
    // 无论成功/失败，结束加载状态
    isLoading.value = false
  }
}

/**
 * 路由参数监听：URL中q/s参数变化时，自动重新执行搜索逻辑
 * 配置：immediate=true（组件初始化时立即执行一次）
 */
watch(() => route.query, fetchResultsFromRoute, { immediate: true })
</script>

<style scoped>
/* 
 * 搜索结果页样式总说明：
 * 1. 设计原则：视觉统一（单条/列表结果样式一致）+ 交互友好（hover反馈、链接跳转）+ 响应式适配（移动端/PC端）+ 状态清晰（加载/错误/无结果区分）
 * 2. 视觉风格：白色卡片+浅灰背景+蓝色链接+红色错误提示，符合内容展示类页面的简洁调性
 * 3. 交互体验：卡片hover上浮、链接hover下划线、代码高亮、Markdown排版优化
 * 4. 兼容性：Markdown深度样式适配、移动端触控友好（简化布局、增大点击热区）
 * 5. 层级关系：标题>卡片标题>内容>元信息，通过字号/颜色/间距区分，元信息弱化显示
 */

/* 列表结果容器：垂直布局+项间距，保证多结果项之间的呼吸感 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-top: 1rem;
}

/* 根容器：响应式内边距（适配不同屏幕）+ 最大宽度限制（避免宽屏拉伸） */
.container {
  padding: 2rem clamp(1rem, 5vw, 3rem); /* 响应式内边距，5vw适配大屏 */
  max-width: 2000px; /* 限制最大宽度，避免内容过宽影响阅读 */
  margin: 0 0;
}

/* 通用卡片样式：白色背景+圆角+柔和阴影+内边距，统一作者/文章卡片视觉风格 */
.author-card, .article-card {
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  margin: 2rem 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05); /* 轻微阴影提升层次感 */
}

/* 卡片标题样式：底部边框+间距+主色调，强化标题层级，区分内容模块 */
.author-card h3, .author-articles h4, .author-comments h4,
.article-card h3, .article-comments h4 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b; /* 深灰色主色调，保证可读性 */
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f1f5f9; /* 浅灰分隔线，弱化视觉分割 */
}

/* 作者文章/评论、文章评论区域：间距+顶部虚线分隔，区分内容模块，提升可读性 */
.author-articles, .author-comments, .article-comments {
  margin: 2.5rem 0;
  padding-top: 1.5rem;
  border-top: 1px dashed #e2e8f0; /* 虚线分隔，柔和不突兀 */
}

/* 文章项：浅灰背景+圆角+内边距+hover交互，提升点击意愿，区分不同文章 */
.article-item {
  padding: 1rem 1.2rem;
  border-radius: 8px;
  background: #f8fafc; /* 浅灰背景，区分卡片主体 */
  margin-bottom: 1rem;
  transition: background-color 0.2s; /* 过渡动画，hover流畅 */
}
/* 文章项hover：加深背景色，强化交互反馈 */
.article-item:hover {
  background: #f1f5f9;
}

/* 文章标题链接：蓝色主色调+hover下划线，符合用户对链接的视觉认知 */
.article-item a {
  color: #3b82f6; /* 蓝色主题，统一链接颜色 */
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
}
.article-item a:hover {
  text-decoration: underline; /* hover下划线，强化可点击 */
}

/* 元信息（发布时间/关联ID等）：浅灰+小号字体，弱化显示，不抢占内容焦点 */
.article-meta, .comment-meta {
  color: #64748b; /* 浅灰色，次要信息色调 */
  font-size: 0.9rem;
  margin: 0.8rem 0 0 0;
}

/* 评论项：浅灰背景+圆角+内边距+行高，提升评论可读性，区分不同评论 */
.comment-item {
  padding: 1.2rem;
  background: #f8fafc;
  border-radius: 8px;
  margin: 1rem 0;
  line-height: 1.6; /* 优化行高，提升阅读体验 */
}

/* 评论作者：加粗+主色调，突出评论归属，区分作者和内容 */
.comment-author {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

/* 【优化点3】文章ID链接样式：与其他链接视觉统一，保证交互一致性 */
.article-id-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}
.article-id-link:hover {
  text-decoration: underline;
  color: #2563eb; /* 深色蓝，强化hover反馈 */
}

/* 文章正文样式：与详情页保持一致，优化Markdown渲染的阅读体验 */
.article-body {
  line-height: 1.8; /* 宽松行高，提升长文本阅读体验 */
  color: #333;
  font-size: 16px;
  margin: 1.5rem 0;
  background: #f9f9f9; /* 浅灰背景，区分正文和卡片 */
  padding: 20px;
  border-radius: 8px;
  word-wrap: break-word; /* 兼容长单词换行 */
  overflow-wrap: break-word;
  word-break: break-all; /* 兼容长URL换行 */
}

/* 无结果提示：居中+内边距+浅灰背景+圆角，弱化无结果的负面体验，引导用户操作 */
.no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: #64748b;
  font-size: 1.1rem;
  background: #f8fafc;
  border-radius: 12px;
  margin: 2rem 0;
}

/* 加载提示：居中+浅灰+内边距，弱化加载状态的视觉冲击，提示用户等待 */
.loading {
  color: #64748b;
  padding: 2rem;
  text-align: center;
  font-size: 1rem;
}

/* 错误提示：红色系+浅红背景+边框，强化错误警示，清晰反馈异常 */
.error-message {
  color: #dc2626; /* 红色警示色 */
  padding: 1.2rem;
  border: 1px solid #fee2e2; /* 浅红边框 */
  border-radius: 8px;
  background: #fef2f2; /* 浅红背景 */
  margin: 1rem 0;
  font-size: 0.95rem;
}

/* Markdown渲染样式（深度作用域）：保证与文章详情页渲染效果一致，提升阅读体验 */
:deep(.article-body h1) {
  font-size: 24px;
  margin: 28px 0 16px;
  font-weight: 700;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}
:deep(.article-body h2) {
  font-size: 22px;
  margin: 24px 0 14px;
  font-weight: 600;
}
:deep(.article-body h3) {
  font-size: 20px;
  margin: 20px 0 12px;
  font-weight: 600;
}
:deep(.article-body p) {
  margin-bottom: 16px;
  word-wrap: break-word;
  word-break: break-all;
}
:deep(.article-body pre) {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  overflow-x: auto; /* 代码块横向滚动 */
  margin: 16px 0;
}
:deep(.article-body code) {
  padding: 2px 4px;
  background: #f5f5f5;
  border-radius: 4px;
  font-family: Consolas, Monaco, 'Courier New', monospace; /* 等宽字体，适配代码 */
  font-size: 14px;
}
:deep(.article-body pre code) {
  padding: 0;
  background: transparent; /* 代码块内的code取消背景，避免重复 */
}
:deep(.article-body blockquote) {
  border-left: 4px solid #4299e1; /* 蓝色左侧边框，区分引用块 */
  padding: 8px 16px;
  background: #f0f8ff;
  color: #666;
  margin: 16px 0;
}
:deep(.article-body ul), 
:deep(.article-body ol) {
  padding-left: 24px;
  margin-bottom: 16px;
}
:deep(.article-body li) {
  margin-bottom: 8px;
  word-wrap: break-word;
  word-break: break-all;
}
:deep(.article-body a) {
  color: #4299e1;
  text-decoration: none;
}
:deep(.article-body a:hover) {
  text-decoration: underline;
}
:deep(.article-body img) {
  max-width: 100%; /* 图片自适应宽度 */
  border-radius: 8px;
  margin: 16px 0;
}
:deep(.no-content) {
  color: #999;
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

/* 移动端适配（768px以下）：简化布局+减少内边距，提升触控体验和屏幕利用率 */
@media (max-width: 768px) {
  /* 简化文章/评论项内边距，节省屏幕空间 */
  .article-item, .comment-item {
    padding: 0.8rem;
  }
  /* 减少根容器内边距，适配小屏 */
  .container {
    padding: 1rem;
  }
  /* 移动端文章正文适配：减少内边距+缩小字号，提升阅读体验 */
  .article-body {
    padding: 15px;
    font-size: 14px;
  }
}
</style>
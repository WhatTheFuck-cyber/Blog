<template>
  <!-- 文章详情页根容器：整合加载/错误状态、文章内容、互动操作、评论区、发表评论等模块，支持登录态判断和评论/回复功能 -->
  <div class="article-detail-container">
    <!-- 加载状态提示：文章数据加载中显示，提升用户等待体验 -->
    <div class="loading" v-if="articleStore.isLoading">正在加载文章详情...</div>
    
    <!-- 错误提示 + 重新加载按钮：加载失败时显示错误信息，支持重新触发加载 -->
    <div class="error-message" v-if="articleStore.error && !articleStore.isLoading">
      {{ articleStore.error }}
      <button class="btn btn-reload" @click="fetchArticleData">重新加载</button>
    </div>

    <!-- 文章内容区：加载成功且无错误、存在文章数据时显示，包含标题/元信息/正文/互动操作/评论区 -->
    <div v-if="!articleStore.isLoading && !articleStore.error && articleStore.currentArticle" class="article-content">
      <!-- 文章头部：展示标题 + 元信息（作者/发布时间/点赞数/收藏数/分类），信息分层展示 -->
      <div class="article-header">
        <h1 class="article-title">{{ articleStore.currentArticle.title }}</h1>
        <div class="article-meta">
          <span class="meta-item">作者：{{ articleStore.currentArticle.owner_name || '未知' }}</span>
          <span class="meta-divider">|</span>
          <span class="meta-item">{{ formatDate(articleStore.currentArticle.created_at) }}</span>
          <span class="meta-divider">|</span>
          <span class="meta-item like-count">
            <i class="like-icon">❤</i> {{ articleStore.currentArticle.like_count || 0 }}
          </span>
          <span class="meta-divider">|</span>
          <span class="meta-item collect-count">
            <i class="collect-icon">⭐</i> {{ articleStore.currentArticle.collect_count || 0 }}
          </span>
          <span class="meta-divider">|</span>
          <span class="meta-item">
            分类：{{ articleStore.currentArticle.category?.name || '未分类' }}
          </span>
        </div>
      </div>

      <!-- 文章正文：将Markdown内容渲染为HTML，支持代码高亮 -->
      <div class="article-body" v-html="renderArticleContent"></div>

      <!-- 文章操作区：点赞/收藏（状态切换）+ 返回首页按钮，支持登录态校验 -->
      <div class="article-actions">
        <button 
          class="btn btn-like" 
          @click="handleLike"
          :class="{ 'active': articleStore.isArticleLiked(articleStore.currentArticle.id) }"
        >
          <i class="like-icon">❤</i> 
          {{ articleStore.isArticleLiked(articleStore.currentArticle.id) ? '已点赞' : '点赞' }}
        </button>
        <button 
          class="btn btn-collect" 
          @click="handleCollect"
          :class="{ 'active': articleStore.isArticleCollected(articleStore.currentArticle.id) }"
        >
          <i class="collect-icon">⭐</i> 
          {{ articleStore.isArticleCollected(articleStore.currentArticle.id) ? '已收藏' : '收藏' }}
        </button>
        <router-link class="btn btn-back" to="/app/home">返回首页</router-link>
      </div>

      <!-- 评论区：区分登录/未登录状态，展示主评论+子评论列表，支持回复/删除操作 -->
      <div class="comment-section">
        <h3 class="comment-title">评论区</h3>
        
        <!-- 未登录提示：引导用户登录后查看/发表评论 -->
        <div v-if="!userStore.isLoggedIn" class="login-prompt">
          <p>需要登录才能查看和发表评论哦~</p>
          <button class="btn-login" @click="gotoLogin">立即登录</button>
        </div>
        
        <!-- 已登录显示评论列表：包含空评论提示、主评论+子评论、回复输入框 -->
        <div v-else>
          <!-- 评论列表为空提示：引导用户发表第一条评论 -->
          <div v-if="!articleStore.currentArticle.comments.length" class="no-comment">
            暂无评论，快来发表第一条评论吧！
          </div>
          
          <!-- 主评论列表：循环渲染，包含作者/内容/时间/操作按钮，支持子评论和回复输入 -->
          <div v-for="mainComment in articleStore.currentArticle.comments" :key="mainComment.id" class="comment-item main-comment">
            <div class="comment-header">
              <div class="comment-author">{{ mainComment.user_name }}</div>
              <div class="comment-actions">
                <button 
                  v-if="mainComment.user_id === userStore.userId" 
                  class="btn-delete" 
                  @click="handleDeleteComment(mainComment.id)"
                >
                  删除
                </button>
                <button 
                  v-else 
                  class="btn-reply" 
                  @click="handleReplyComment(mainComment.id)"
                >
                  回复
                </button>
              </div>
            </div>
            <div class="comment-content">{{ mainComment.content }}</div>
            <div class="comment-time">{{ formatDate(mainComment.created_at) }}</div>

            <!-- 子评论列表：嵌套渲染主评论的回复，样式区分主/子评论 -->
            <div v-if="mainComment.children.length" class="comment-children">
              <div v-for="childComment in mainComment.children" :key="childComment.id" class="comment-item child-comment">
                <div class="comment-header child-comment-header">
                  <div class="comment-author">{{ childComment.user_name }}</div>
                  <div class="comment-actions child-comment-actions">
                    <button 
                      v-if="childComment.user_id === userStore.userId" 
                      class="btn-delete btn-delete-sm" 
                      @click="handleDeleteComment(childComment.id)"
                    >
                      删除
                    </button>
                  </div>
                </div>
                <div class="comment-content">{{ childComment.content }}</div>
                <div class="comment-time">{{ formatDate(childComment.created_at) }}</div>
              </div>
            </div>

            <!-- 回复输入框：点击回复后显示，绑定回复内容，支持提交/取消操作 -->
            <div v-if="replyTargetId === mainComment.id" class="reply-input-wrap" :data-comment-id="mainComment.id">
              <textarea 
                class="comment-input reply-input" 
                placeholder="请输入回复内容..." 
                v-model="replyContent"
              ></textarea>
              <div class="reply-btn-group">
                <button 
                  class="submit-btn btn-reply-submit" 
                  :disabled="!replyContent.trim() || isSubmitting"
                  @click="handleSubmitReply(mainComment.id)"
                >
                  <span v-if="isSubmitting">提交中...</span>
                  <span v-else>提交回复</span>
                </button>
                <button class="cancel-btn" @click="cancelReply">取消</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 发表评论区域：区分登录/未登录状态，支持主评论发布，包含提交状态禁用 -->
      <div class="post-comment-section">
        <h3 class="comment-title">发表评论</h3>
        
        <!-- 未登录提示：引导用户登录后发表评论 -->
        <div v-if="!userStore.isLoggedIn" class="login-prompt">
          <p>登录后即可发表您的精彩评论~</p>
          <button class="btn-login" @click="gotoLogin">立即登录</button>
        </div>
        
        <!-- 已登录显示评论输入框：绑定评论内容，提交按钮禁用逻辑（空内容/提交中） -->
        <div v-else>
          <textarea 
            class="comment-input" 
            placeholder="请输入您的评论内容..." 
            v-model="commentContent"
            :disabled="isSubmitting"
          ></textarea>
          <button 
            class="submit-btn" 
            :disabled="isBtnDisabled"
            @click="handleSubmitComment"
          >
            <span v-if="isSubmitting">提交中...</span>
            <span v-else>发表评论</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 文章详情页组件
 * @description 展示文章完整信息（标题/元信息/正文），支持点赞/收藏互动，集成评论/回复功能（登录态控制），包含加载/错误状态处理
 * @feature 1. 文章Markdown内容渲染（支持代码高亮） 2. 点赞/收藏状态切换（未登录跳转登录） 3. 评论/回复发布/删除（登录态校验） 4. 加载/错误状态提示 5. 路由参数监听（ID变化重新加载） 6. 时间格式化 7. 提交状态防重复提交
 * @dependencies 
 *  - marked + highlight.js: Markdown渲染+代码高亮
 *  - pinia (articleStore/userStore): 文章/用户状态管理
 *  - vue-router: 路由跳转/参数监听
 *  - element-plus (ElMessage): 操作结果提示
 */
// 导入Vue核心API：生命周期/响应式/计算属性/异步DOM更新
import { onMounted, watch, computed, ref, nextTick, onUnmounted } from 'vue'
// 导入Vue Router：路由参数/跳转
import { useRoute, useRouter } from 'vue-router'
// 导入Pinia状态管理：文章/用户数据与操作
import { useArticleStore } from '@/store/article'
import { useUserStore } from '@/store/user'
// 导入Element Plus：操作结果提示
import { ElMessage } from 'element-plus'
// 导入Markdown解析+代码高亮依赖
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/default.css'

// 初始化核心实例
const route = useRoute() // 当前路由实例（获取文章ID参数）
const router = useRouter() // 路由跳转实例（登录/返回首页）
const articleStore = useArticleStore() // 文章状态管理（加载详情/点赞/评论等）
const userStore = useUserStore() // 用户状态管理（登录态/用户ID）

// 响应式数据定义
/** @type {Ref<string>} 主评论输入框内容，双向绑定文本域 */
const commentContent = ref('')
/** @type {Ref<boolean>} 评论/回复提交状态，防止重复提交 */
const isSubmitting = ref(false)
/** @type {Ref<string>} 回复目标评论ID，控制回复输入框显示 */
const replyTargetId = ref('')
/** @type {Ref<string>} 回复输入框内容，双向绑定文本域 */
const replyContent = ref('')

/**
 * 时间格式化函数
 * @description 将ISO时间字符串转为中文本地化格式（年/月/日 时/分），处理空值边界
 * @param {string} dateStr - 原始时间字符串（如ISO格式）
 * @returns {string} 格式化后的时间字符串（空值返回"未知时间"）
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '未知时间'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 配置marked解析器
 * @description 开启代码高亮（基于highlight.js）、GitHub风格Markdown、自动换行等特性，关闭header ID避免冲突
 */
marked.setOptions({
  highlight: function (code, lang) {
    // 代码高亮：校验语言类型，未知语言使用纯文本
    const validLang = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language: validLang }).value
  },
  gfm: true, // 开启GitHub Flavored Markdown
  breaks: true, // 换行符转为<br>
  headerIds: false, // 关闭标题自动生成ID
  mangle: false // 关闭链接标签混淆
})

/**
 * 计算属性：渲染文章Markdown内容
 * @description 解析文章Markdown内容为HTML，处理空内容边界（显示"暂无文章内容"）
 * @returns {string} 渲染后的HTML字符串
 */
const renderArticleContent = computed(() => {
  if (!articleStore.currentArticle || !articleStore.currentArticle.content) {
    return '<p class="no-content">暂无文章内容</p>'
  }
  return marked.parse(articleStore.currentArticle.content)
})

/**
 * 获取文章详情数据
 * @description 从路由参数提取文章ID，校验有效性后调用store加载详情，处理ID无效边界
 * @returns {Promise<void>} 异步操作Promise
 */
const fetchArticleData = async () => {
  const articleId = route.params.id
  // 边界处理：文章ID无效时设置错误状态
  if (!articleId) {
    articleStore.error = '无效的文章ID'
    articleStore.isLoading = false
    return
  }
  // 调用store方法加载文章详情
  await articleStore.fetchArticleDetail(articleId)
}

/**
 * 处理文章点赞/取消点赞
 * @description 调用store切换点赞状态，提示操作结果；未登录时引导登录（跳转登录页）
 * @returns {Promise<void>} 异步操作Promise
 */
const handleLike = async () => {
  const articleId = articleStore.currentArticle.id
  try {
    const result = await articleStore.toggleLike(articleId)
    // 操作成功提示（区分点赞/取消点赞）
    showMsg('success', result.isLiked ? '点赞成功' : '取消点赞成功')
  } catch (err) {
    // 未登录处理：提示并跳转登录页
    if (err.message.includes('请先登录')) {
      showMsg('warning', '记得登录哦~')
      router.push({ name: 'Login' })
    } else {
      // 其他错误提示
      showMsg('error', '出错了，请稍后再试~')
    }
  }
}

/**
 * 处理文章收藏/取消收藏
 * @description 逻辑同点赞操作，仅切换收藏状态
 * @returns {Promise<void>} 异步操作Promise
 */
const handleCollect = async () => {
  const articleId = articleStore.currentArticle.id
  try {
    const result = await articleStore.toggleCollect(articleId)
    // 操作成功提示（区分收藏/取消收藏）
    showMsg('success', result.isCollected ? '收藏成功' : '取消收藏成功',)
  } catch (err) {
    // 未登录处理：提示并跳转登录页
    if (err.message.includes('请先登录')) {
      showMsg('warning', '记得登录哦~')
      router.push({ name: 'Login' })
    } else {
      // 其他错误提示
      showMsg('error', '出错了，请稍后再试~')
    }
  }
}

/**
 * 生命周期：组件挂载
 * @description 页面首次加载时获取文章详情数据
 */
onMounted(() => {
  fetchArticleData()
})

/**
 * 监听路由参数变化
 * @description 文章ID变化时重新加载详情（如从列表页跳转不同文章）
 */
watch(() => route.params.id, () => {
  fetchArticleData()
})

/**
 * 计算属性：评论提交按钮禁用状态
 * @description 内容为空 或 正在提交时禁用，防止无效/重复提交
 * @returns {boolean} 禁用状态（true=禁用，false=可用）
 */
const isBtnDisabled = computed(() => {
  const isEmpty = commentContent.value.trim() === ''
  return isEmpty || isSubmitting.value
})

/**
 * 提交主评论
 * @description 校验状态→调用store发布评论→提示结果→清空输入框，处理文章ID/登录态边界
 * @returns {Promise<void>} 异步操作Promise
 */
const handleSubmitComment = async () => {
  // 边界处理：按钮禁用时直接返回
  if (isBtnDisabled.value) return
  const articleId = articleStore.currentArticle?.id
  // 边界处理：文章ID无效提示
  if (!articleId) {
    showMsg('error', '文章ID无效哦~')
    return
  }
  // 边界处理：未登录提示
  if (!userStore.isLoggedIn) {
    showMsg('warning', '请先登录哦~')
    return
  }

  try {
    isSubmitting.value = true // 标记提交中
    await articleStore.submitComment(articleId, commentContent.value) // 调用store发布评论
    showMsg('success', '评论发布成功！') // 成功提示
    commentContent.value = '' // 清空输入框
  } catch (err) {
    showMsg('error', '出错了，请稍后再试~') // 错误提示
  } finally {
    isSubmitting.value = false // 重置提交状态
  }
}

/**
 * 触发回复评论
 * @description 标记回复目标ID，清空回复内容，自动聚焦回复输入框（异步DOM更新）
 * @param {string} commentId - 被回复的主评论ID
 * @returns {void}
 */
const handleReplyComment = (commentId) => {
  replyTargetId.value = commentId // 标记回复目标
  replyContent.value = '' // 清空回复内容
  // 异步DOM更新后聚焦输入框
  nextTick(() => {
    const replyInput = document.querySelector(`.reply-input-wrap[data-comment-id="${commentId}"] textarea`)
    replyInput?.focus() // 存在则聚焦
  })
}

/**
 * 取消回复评论
 * @description 清空回复目标ID和回复内容，隐藏回复输入框
 * @returns {void}
 */
const cancelReply = () => {
  replyTargetId.value = ''
  replyContent.value = ''
}

/**
 * 提交回复评论
 * @description 校验状态→调用store发布回复→提示结果→清空回复状态，处理文章ID边界
 * @param {string} parentCommentId - 父评论ID（被回复的主评论）
 * @returns {Promise<void>} 异步操作Promise
 */
const handleSubmitReply = async (parentCommentId) => {
  // 边界处理：内容为空或提交中直接返回
  if (!replyContent.value.trim() || isSubmitting.value) return
  const articleId = articleStore.currentArticle?.id
  // 边界处理：文章ID无效提示
  if (!articleId) {
    showMsg('error', '文章ID无效哦~')
    return
  }

  try {
    isSubmitting.value = true // 标记提交中
    await articleStore.replyComment(articleId, parentCommentId, replyContent.value) // 调用store发布回复
    showMsg('success', '回复发布成功！') // 成功提示
    cancelReply() // 清空回复状态
  } catch (err) {
    showMsg('error', '出错了，请稍后再试~') // 错误提示
  } finally {
    isSubmitting.value = false // 重置提交状态
  }
}

/**
 * 删除评论/回复
 * @description 二次确认→调用store删除→提示结果，处理文章ID边界
 * @param {string} commentId - 要删除的评论/回复ID
 * @returns {Promise<void>} 异步操作Promise
 */
const handleDeleteComment = async (commentId) => {
  // 二次确认：防止误删
  if (!confirm('确定要删除这条评论吗？')) return
  const articleId = articleStore.currentArticle?.id
  // 边界处理：文章ID无效提示
  if (!articleId) {
    showMsg('error', '文章ID无效哦~')
    return
  }

  try {
    await articleStore.deleteComment(articleId, commentId) // 调用store删除评论
    showMsg('success', '评论删除成功！') // 成功提示
  } catch (err) {
    showMsg('error', '出错了，请稍后再试~') // 错误提示
  }
}

/**
 * 跳转登录页
 * @description 携带当前页面路径作为跳转参数，登录后可返回当前文章详情页
 * @returns {void}
 */
const gotoLogin = () => {
  router.push({ 
    name: 'Login',
    query: { redirect: route.fullPath } // 携带当前路径，登录后返回
  })
}

// 封装ElMessage，确保每次调用前关闭所有旧提示
const showMsg = (type, message) => {
  // 先关闭所有已存在的ElMessage
  ElMessage.closeAll()
  // 再显示新提示
  ElMessage[type]({
    message,
    duration: 2000,
    showClose: false // 保持原有样式，不显示关闭按钮
  })
}

// 组件卸载时强制清理所有提示（核心：防止页面跳转后提示滞留）
onUnmounted(() => {
  ElMessage.closeAll()
})
</script>

<style scoped>
/* 根容器：最大宽度+居中+内边距 */
.article-detail-container {
  max-width: 2000px;
  margin: 0 auto;
  padding: 20px;
}

/* 加载/错误提示：居中+内边距+文字颜色 */
.loading, .error-message {
  text-align: center;
  padding: 40px 0;
  color: #666;
}
.error-message {
  color: #e53e3e;
}

/* 重新加载按钮样式 */
.btn-reload {
  margin-top: 10px;
  padding: 8px 16px;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 文章头部：底部分隔线+间距 */
.article-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

/* 文章标题：字号+颜色+间距 */
.article-title {
  font-size: 28px;
  color: #333;
  margin: 0 0 16px;
}

/* 文章元信息：flex布局+换行+间距+字号 */
.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 14px;
  color: #666;
}

/* 元信息分隔符：颜色 */
.meta-divider {
  color: #ddd;
}

/* 点赞/收藏图标：颜色+右间距 */
.like-icon {
  color: #e53e3e;
  margin-right: 4px;
}
.collect-icon {
  color: #ed8936;
  margin-right: 4px;
}

/* 文章内容容器：最大宽度 */
.article-content {
  max-width: 2000px;
}

/* 文章正文：行高+背景+内边距+长文本换行处理 */
.article-body {
  line-height: 1.8;
  color: #333;
  font-size: 16px;
  margin-bottom: 40px;
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-all;
}

/* Markdown渲染样式（深度作用域） */
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
  overflow-x: auto;
  margin: 16px 0;
}
:deep(.article-body code) {
  padding: 2px 4px;
  background: #f5f5f5;
  border-radius: 4px;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 14px;
}
:deep(.article-body pre code) {
  padding: 0;
  background: transparent;
}
:deep(.article-body blockquote) {
  border-left: 4px solid #4299e1;
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
  max-width: 100%;
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

/* 文章操作区：flex布局+间距 */
.article-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 40px;
}

/* 点赞按钮：基础样式+激活态 */
.btn-like {
  padding: 8px 20px;
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-like.active {
  background: #fef2f2;
  color: #e53e3e;
  border-color: #fecaca;
}
.btn-like:hover {
  background-color: #edf2f7;
  color: #2d3748;
}

/* 收藏按钮：基础样式+激活态 */
.btn-collect {
  padding: 8px 20px;
  background: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-collect.active {
  background: #fffaf0;
  color: #ed8936;
  border-color: #fcd34d;
}
.btn-collect:hover {
  background-color: #edf2f7;
  color: #2d3748;
}

/* 返回首页按钮 */
.btn-back {
  padding: 8px 20px;
  background: #4299e1;
  color: white;
  border-radius: 4px;
  text-decoration: none;
}
.btn-back:hover {
  background-color: #2980b9;
}

/* 评论区标题 */
.comment-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
}

/* 评论项：基础样式 */
.comment-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
}

/* 主评论：背景+间距 */
.main-comment {
  margin-bottom: 20px;
  background: #fff;
}

/* 评论作者：加粗+颜色+间距 */
.comment-author {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

/* 评论内容：颜色+行高+间距 */
.comment-content {
  color: #4a5568;
  margin-bottom: 8px;
  line-height: 1.6;
}

/* 评论时间：字号+颜色 */
.comment-time {
  font-size: 12px;
  color: #999;
}

/* 子评论头部：布局调整 */
.child-comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
</style>

<!-- 全局样式：评论/回复/提示框相关（非scoped） -->
<style>
/* ElementUI提示框：瘦长扁平样式 */
.el-message {
  position: fixed;
  top: 15%;
  left: 50%;
  transform: translate(-50%, 0);
  margin: 0 !important;
  z-index: 9999;
  background: #fff !important;
  opacity: 1 !important;
  border: 1px solid #e6f7ed !important;
  border-radius: 4px;
  max-width: 280px;
  padding: 8px 16px !important;
  display: flex;
  align-items: center;
  gap: 8px;
}
.el-message--success .el-message__icon {
  width: 20px !important;
  height: 20px !important;
  color: #52c41a !important;
  font-size: 20px !important;
}
.el-message .el-message__content {
  color: #52c41a !important;
  font-size: 14px;
  padding: 0 !important;
  line-height: 1.4;
}
.el-message__closeBtn {
  display: none;
}

/* 评论/回复输入框：基础样式 */
.comment-input {
  width: 100%;
  height: 120px;
  padding: 15px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  resize: vertical;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  transition: border-color 0.3s ease;
  margin-bottom: 15px;
}
.comment-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}
.comment-input::placeholder {
  color: #999;
}

/* 回复输入框：高度调整 */
.reply-input {
  height: 80px !important;
  margin-bottom: 10px !important;
}

/* 提交按钮：基础样式+hover/禁用态 */
.submit-btn {
  padding: 10px 24px;
  background-color: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.submit-btn:hover {
  background-color: #66b1ff;
}
.submit-btn:active {
  background-color: #3399ff;
}
.submit-btn:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

/* 评论头部：作者+操作按钮布局 */
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

/* 评论操作按钮组：flex布局+间距 */
.comment-actions {
  display: flex;
  gap: 8px;
}

/* 删除按钮：基础+小号样式 */
.btn-delete {
  padding: 4px 8px;
  background: #fef2f2;
  color: #e53e3e;
  border: 1px solid #fecaca;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.btn-delete:hover {
  background: #fee2e2;
}
.btn-delete-sm {
  padding: 2px 6px;
  font-size: 11px;
  border-radius: 3px;
}

/* 回复按钮：基础样式 */
.btn-reply {
  padding: 4px 8px;
  background: #f0fdf4;
  color: #10b981;
  border: 1px solid #bbf7d0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.btn-reply:hover {
  background: #dcfce7;
}

/* 回复输入框容器：背景+内边距+间距 */
.reply-input-wrap {
  margin-top: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

/* 回复按钮组：右对齐+间距 */
.reply-btn-group {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 回复提交按钮：尺寸调整 */
.btn-reply-submit {
  padding: 6px 16px !important;
  font-size: 12px !important;
}

/* 取消按钮：基础样式 */
.cancel-btn {
  padding: 6px 16px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #eee;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}
.cancel-btn:hover {
  background: #eee;
}

/* 子评论容器：缩进+左侧边框 */
.comment-children {
  margin-top: 12px;
  margin-left: 30px;
  padding-left: 10px;
  border-left: 2px solid #eee;
}

/* 子评论：样式区分 */
.child-comment {
  padding: 10px 12px;
  border: 1px solid #f5f5f5;
  border-radius: 6px;
  background: #fafafa;
  margin-bottom: 8px;
  font-size: 14px;
}
.child-comment:last-child {
  margin-bottom: 0;
}

/* 未登录提示：居中+背景+间距 */
.login-prompt {
  padding: 20px;
  text-align: center;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin: 10px 0;
}

/* 登录按钮：基础样式+hover */
.btn-login {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}
.btn-login:hover {
  background-color: #66b1ff;
}

/* 无评论提示：居中+背景+颜色 */
.no-comment {
  padding: 20px;
  text-align: center;
  color: #999;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 10px 0;
}

/* 评论区/发表评论区：上间距 */
.comment-section, .post-comment-section {
  margin-top: 30px;
}

/* 响应式适配：小屏幕 */
@media (max-width: 768px) {
  .submit-btn {
    width: 100%;
    padding: 12px 0;
  }
  .comment-title {
    font-size: 16px;
  }
}
</style>
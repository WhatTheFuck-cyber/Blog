// @store/userInfo.js (If you see this message, that means this file has been checked and can be put into production environment)

import { defineStore } from 'pinia'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'

/**
 * 用户详情信息管理 Store
 * @description 基于 Pinia 实现用户基础信息、文章/评论、点赞/收藏等互动数据的管理
 * @exports useUserInfoStore - 用户详情信息操作钩子
 */
export const useUserInfoStore = defineStore('userInfo', {
  /**
   * Store 状态定义
   * @property {number} id - 用户ID
   * @property {string} email - 用户邮箱
   * @property {string} username - 用户名
   * @property {boolean} is_activate - 用户是否激活
   * @property {string} activate_at - 用户激活时间
   * @property {Array<Object>} articles - 用户发布的文章列表
   * @property {Array<Object>} comments - 用户发布的评论列表
   * @property {Array<number>} my_likes - 点赞文章ID列表（轻量化，用于状态判断）
   * @property {Array<number>} my_collects - 收藏文章ID列表（轻量化，用于状态判断）
   * @property {Array<Object>} likeArticles - 点赞文章基础展示信息（标题/作者/时间）
   * @property {Array<Object>} collectArticles - 收藏文章基础展示信息（标题/作者/时间）
   * @property {boolean} isLoading - 数据加载状态
   * @property {string} error - 错误信息提示
   */
  state: () => ({
    // 原有用户基础信息（完全保留）
    id: 0,
    email: '',
    username: '',
    is_activate: false,
    activate_at: '',
    articles: [],
    comments: [],

    // 仅存储文章ID（核心：轻量化，用于状态判断）
    my_likes: [], // 点赞文章ID列表
    my_collects: [], // 收藏文章ID列表

    // 新增：存储点赞/收藏的基础展示信息（仅用于UserTrack列表展示）
    likeArticles: [], // 点赞文章基础信息（标题/作者/时间）
    collectArticles: [], // 收藏文章基础信息

    // 通用状态（保留）
    isLoading: false,
    error: ''
  }),

  /**
   * Store 方法（Actions）
   * @description 处理用户详情信息的获取、清空、状态管理等逻辑
   */
  actions: {
    /**
     * 清空用户详情信息
     * @returns {void}
     * @description 退出登录时调用，重置所有用户信息状态为初始值
     */
    clearUserInfo() {
      this.id = 0
      this.email = ''
      this.username = ''
      this.is_activate = false
      this.activate_at = ''
      this.articles = []
      this.comments = []
      this.my_likes = []
      this.my_collects = []
      this.likeArticles = [] // 新增清空
      this.collectArticles = [] // 新增清空
      this.error = ''
    },

    /**
     * 设置加载状态
     * @param {boolean} flag - 加载状态标识（true=加载中，false=加载完成）
     * @returns {void}
     * @description 控制数据请求过程中的加载状态展示
     */
    setLoading(flag) {
      this.isLoading = flag
    },

    /**
     * 清空错误信息
     * @returns {void}
     * @description 重置错误提示状态，用于新请求前的状态清理
     */
    clearError() {
      this.error = ''
    },

    /**
     * 获取用户基本信息
     * @param {number|string} [userId] - 目标用户ID（可选，默认取当前登录用户ID）
     * @returns {Promise<void>}
     * @description 从后端获取用户基础信息（账号、文章、评论），格式化数据类型并存储
     */
    async fetchUserBasicInfo(userId) {
      const userStore = useUserStore()
      const targetUserId = userId || userStore.userId
      if (!targetUserId || isNaN(Number(targetUserId))) {
        this.error = '无效的用户ID'
        return
      }
      const numericUserId = Number(targetUserId)

      this.setLoading(true)
      this.clearError()

      try {
        const res = await request.get('/users', {
          params: { user_id: numericUserId }
        })

        this.id = Number(res.id) || 0
        this.email = res.email || ''
        this.username = res.username || ''
        this.is_activate = res.is_active || false
        this.activate_at = res.activate_at || ''
        
        this.articles = (res.articles || []).map(article => ({
          ...article,
          id: Number(article.id),
          owner_id: Number(article.owner_id),
          like_count: article.like_count || 0,
          collect_count: article.collect_count || 0
        }))

        this.comments = (res.comments || []).map(comment => ({
          ...comment,
          id: Number(comment.id),
          user_id: Number(comment.user_id),
          article_id: Number(comment.article_id),
          parent_id: Number(comment.parent_id)
        }))

      } catch (err) {
        console.error('获取用户基本信息失败: ', err)
        this.error = err.response?.data?.message || '获取个人信息失败，请稍后重试'
      } finally {
        this.setLoading(false)
      }
    },

    /**
     * 获取用户互动数据（点赞/收藏）
     * @returns {Promise<void>}
     * @description 分离存储互动数据：ID列表（用于状态判断）+ 基础展示信息（用于列表渲染），过滤无效数据
     */
    async fetchMyInteractions() {
      this.clearError()
      try {
        // 1. 处理点赞数据
        const likesRes = await request.get('/interactions/my/likes')
        this.likeArticles = likesRes.map(item => ({ // 存储基础展示信息
          id: Number(item.id),
          title: item.title || '无标题',
          owner_name: item.owner_name || '未知作者',
          created_at: item.created_at || ''
        })).filter(art => art.id) // 过滤无效数据
        this.my_likes = this.likeArticles.map(art => art.id) // 仅存ID

        // 2. 处理收藏数据
        const collectsRes = await request.get('/interactions/my/collects')
        this.collectArticles = collectsRes.map(item => ({
          id: Number(item.id),
          title: item.title || '无标题',
          owner_name: item.owner_name || '未知作者',
          created_at: item.created_at || ''
        })).filter(art => art.id)
        this.my_collects = this.collectArticles.map(art => art.id) // 仅存ID

      } catch (err) {
        console.error('获取用户点赞/收藏数据失败: ', err)
        this.error = err.response?.data?.message || '获取互动数据失败，请稍后重试'
      }
    },

    /**
     * 一键获取所有用户信息
     * @param {number|string} [userId] - 目标用户ID（可选，默认取当前登录用户ID）
     * @returns {Promise<void>}
     * @description 先获取基础信息，成功后再获取互动数据，实现用户信息一站式加载
     */
    async fetchAllUserInfo(userId) {
      await this.fetchUserBasicInfo(userId)
      if (!this.error && this.id > 0) {
        await this.fetchMyInteractions()
      }
    }
  },

  /**
   * Store 计算属性（Getters）
   * @description 基于State动态计算的响应式只读属性，用于快速获取状态/统计数据
   */
  getters: {
    /**
     * 判断文章是否被点赞
     * @param {number} articleId - 文章ID
     * @returns {boolean} 点赞状态（true=已点赞，false=未点赞）
     * @description 通过文章ID匹配my_likes列表，判断点赞状态
     */
    isArticleLiked: (state) => (articleId) => {
      return state.my_likes.includes(Number(articleId))
    },
    /**
     * 判断文章是否被收藏
     * @param {number} articleId - 文章ID
     * @returns {boolean} 收藏状态（true=已收藏，false=未收藏）
     * @description 通过文章ID匹配my_collects列表，判断收藏状态
     */
    isArticleCollected: (state) => (articleId) => {
      return state.my_collects.includes(Number(articleId))
    },
    /**
     * 获取用户发布文章数量
     * @returns {number} 文章数量
     * @description 统计articles数组长度，返回用户发布文章总数
     */
    articleCount: (state) => state.articles.length,
    /**
     * 获取用户发布评论数量
     * @returns {number} 评论数量
     * @description 统计comments数组长度，返回用户发布评论总数
     */
    commentCount: (state) => state.comments.length,
    /**
     * 获取用户点赞文章数量
     * @returns {number} 点赞数量
     * @description 统计my_likes数组长度，返回用户点赞文章总数
     */
    likeCount: (state) => state.my_likes.length,
    /**
     * 获取用户收藏文章数量
     * @returns {number} 收藏数量
     * @description 统计my_collects数组长度，返回用户收藏文章总数
     */
    collectCount: (state) => state.my_collects.length
  }
})
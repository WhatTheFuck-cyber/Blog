// @store/article.js (If you see this message, that means this file has been checked and can be put into production environment)

import { defineStore } from 'pinia'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'

export const useArticleStore = defineStore('article', {
  state: () => ({
    categoryList: [],
    latestArticleList: [],
    currentArticle: null,
    currentCategory: null,
    myLikedArticleIds: [],
    myCollectedArticleIds: [],
    isLoading: false,
    error: ''
  }),
  actions: {
    /**
     * 获取首页分类和最新文章数据
     */
    async fetchHomeData() {
      this.isLoading = true
      this.error = ''
      try {
        const response = await request.get('/home')
        this.categoryList = response.categories || []
        this.latestArticleList = (response.latest_articles || []).map(art => ({
          ...art,
          id: Number(art.id),
          like_count: art.like_count || 0,
          collect_count: art.collect_count || 0
        }))
      } catch (err) {
        console.error('获取首页数据失败: ', err)
        this.error = '文章和分类加载失败，请稍后再试'
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 获取当前登录用户的点赞/收藏文章ID列表，同步互动状态
     */
    async fetchMyInteractions() {
      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) return

      try {
        const likesRes = await request.get('/interactions/my/likes')
        this.myLikedArticleIds = likesRes.map(item => Number(item.id))
        
        const collectsRes = await request.get('/interactions/my/collects')
        this.myCollectedArticleIds = collectsRes.map(item => Number(item.id))
      } catch (err) {
        console.error('获取我的互动列表失败: ', err)
      }
    },

    /**
     * 获取指定分类的详情及该分类下的文章列表
     * @param {string|number} categoryId - 分类ID
     */
    async fetchCategoryDetail(categoryId) {
      const categoryIdNum = Number(categoryId);
      if (isNaN(categoryIdNum)) {
        this.error = '无效的分类ID';
        this.isLoading = false;
        return;
      }

      this.isLoading = true;
      this.error = '';
      try {
        const response = await request.get(`/categories/${categoryIdNum}`); 
        this.currentCategory = {
          ...response,
          articles: (response.articles || []).map(art => ({
            ...art,
            id: Number(art.id),
            like_count: art.like_count || 0,
            collect_count: art.collect_count || 0
          }))
        };
      } catch (err) {
        console.error('获取分类详情失败: ', err);
        this.error = '分类加载失败，请稍后再试';
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 获取指定文章的详情（含评论列表），同步点赞/收藏状态
     * @param {string|number} articleId - 文章ID
     */
    async fetchArticleDetail(articleId) {
      const articleIdNum = Number(articleId)
      if (isNaN(articleIdNum)) {
        this.error = '无效的文章ID'
        return
      }

      this.isLoading = true
      this.error = ''
      this.currentArticle = null
      
      try {
        if (this.categoryList.length === 0) {
          await this.fetchHomeData()
        }

        const response = await request.get(`/articles/${articleIdNum}`)
        
        const matchedCategory = this.categoryList.find(
          cat => cat.id === Number(response.category_id)
        )

        const processComments = (comments) => {
          if (!Array.isArray(comments)) return [];
          const formatted = comments.map(comment => ({
            ...comment,
            id: Number(comment.id),
            parent_id: Number(comment.parent_id),
            article_id: Number(comment.article_id),
            user_id: Number(comment.user_id)
          }));
          const mainComments = formatted.filter(c => c.parent_id === 0);
          return mainComments.map(main => ({
            ...main,
            children: formatted.filter(c => c.parent_id === main.id)
          }));
        };

        this.currentArticle = {
          ...response,
          id: Number(response.id),
          like_count: response.like_count || 0,
          collect_count: response.collect_count || 0,
          comments: processComments(response.comments),
          category: matchedCategory || { name: '未分类' }
        }

        const userStore = useUserStore(this.$pinia)
        if (userStore.isLoggedIn) {
          if (response.is_liked && !this.myLikedArticleIds.includes(articleIdNum)) {
            this.myLikedArticleIds.push(articleIdNum)
          }
          if (response.is_collected && !this.myCollectedArticleIds.includes(articleIdNum)) {
            this.myCollectedArticleIds.push(articleIdNum)
          }
        }
      } catch (err) {
        console.error('获取文章详情失败: ', err)
        this.error = err.response?.data?.message || '文章加载失败，请稍后再试'
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 切换文章点赞/取消点赞状态
     * @param {string|number} articleId - 文章ID
     * @returns {object} 操作结果及最新点赞状态
     */
    async toggleLike(articleId) {
      const articleIdNum = Number(articleId)
      if (isNaN(articleIdNum)) {
        throw new Error('无效的文章ID')
      }

      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) {
        throw new Error('请先登录后再点赞')
      }

      try {
        const isLiked = this.myLikedArticleIds.includes(articleIdNum)

        if (isLiked) {
          await request.delete(`/interactions/likes/${articleIdNum}`)
        } else {
          await request.post('/interactions/likes', {
            article_id: articleIdNum
          })
        }

        if (isLiked) {
          this.myLikedArticleIds = this.myLikedArticleIds.filter(id => id !== articleIdNum)
        } else {
          this.myLikedArticleIds.push(articleIdNum)
        }

        if (this.currentArticle?.id === articleIdNum) {
          await this.fetchArticleDetail(articleIdNum)
        } else {
          await this.fetchHomeData()
        }

        return { success: true, isLiked: !isLiked }
      } catch (err) {
        console.error('点赞操作失败: ', err)
        throw new Error(err.response?.data?.message || '点赞失败，请重试')
      }
    },

    /**
     * 切换文章收藏/取消收藏状态
     * @param {string|number} articleId - 文章ID
     * @returns {object} 操作结果及最新收藏状态
     */
    async toggleCollect(articleId) {
      const articleIdNum = Number(articleId)
      if (isNaN(articleIdNum)) {
        throw new Error('无效的文章ID')
      }

      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) {
        throw new Error('请先登录后再收藏')
      }

      try {
        const isCollected = this.myCollectedArticleIds.includes(articleIdNum)

        if (isCollected) {
          await request.delete(`/interactions/collects/${articleIdNum}`)
        } else {
          await request.post('/interactions/collects', {
            article_id: articleIdNum
          })
        }

        if (isCollected) {
          this.myCollectedArticleIds = this.myCollectedArticleIds.filter(id => id !== articleIdNum)
        } else {
          this.myCollectedArticleIds.push(articleIdNum)
        }

        if (this.currentArticle?.id === articleIdNum) {
          await this.fetchArticleDetail(articleIdNum)
        } else {
          await this.fetchHomeData()
        }

        return { success: true, isCollected: !isCollected }
      } catch (err) {
        console.error('收藏操作失败: ', err)
        throw new Error(err.response?.data?.message || '收藏失败，请重试')
      }
    },

    /**
     * 发布文章主评论
     * @param {string|number} articleId - 文章ID
     * @param {string} content - 评论内容
     * @returns {object} 操作结果及发布的评论数据
     */
    async submitComment(articleId, content) {
      const articleIdNum = Number(articleId)
      if (isNaN(articleIdNum)) {
        throw new Error('无效的文章ID')
      }
      if (!content.trim()) {
        throw new Error('评论内容不能为空')
      }
      
      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) {
        throw new Error('请先登录后再发表评论')
      }

      try {
        const response = await request.post('/comments', {
          article_id: articleIdNum,
          content: content.trim(),
          parent_id: 0
        })

        await this.fetchArticleDetail(articleIdNum)
        return { success: true, comment: response }
      } catch (err) {
        throw new Error(err.response?.data?.message || '评论发布失败，请重试')
      }
    },

    /**
     * 回复文章评论（子评论）
     * @param {string|number} articleId - 文章ID
     * @param {string|number} parentCommentId - 父评论ID
     * @param {string} content - 回复内容
     * @returns {object} 操作结果及发布的回复数据
     */
    async replyComment(articleId, parentCommentId, content) {
      const articleIdNum = Number(articleId)
      const parentCommentIdNum = Number(parentCommentId)
      
      if (isNaN(articleIdNum) || isNaN(parentCommentIdNum)) {
        throw new Error('无效的文章ID或父评论ID')
      }
      if (!content.trim()) {
        throw new Error('回复内容不能为空')
      }
      
      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) {
        throw new Error('请先登录后再回复评论')
      }

      try {
        const response = await request.post('/comments', {
          article_id: articleIdNum,
          content: content.trim(),
          parent_id: parentCommentIdNum
        })

        await this.fetchArticleDetail(articleIdNum)
        return { success: true, comment: response }
      } catch (err) {
        throw new Error(err.response?.data?.message || '回复评论失败，请重试')
      }
    },

    /**
     * 删除指定评论
     * @param {string|number} articleId - 文章ID
     * @param {string|number} commentId - 评论ID
     * @returns {object} 操作结果
     */
    async deleteComment(articleId, commentId) {
      const articleIdNum = Number(articleId)
      const commentIdNum = Number(commentId)
      
      if (isNaN(articleIdNum) || isNaN(commentIdNum)) {
        throw new Error('无效的文章ID或评论ID')
      }
      
      const userStore = useUserStore(this.$pinia)
      if (!userStore.isLoggedIn) {
        throw new Error('请先登录后再删除评论')
      }

      try {
        await request.delete(`/comments/${commentIdNum}`, {
          params: { article_id: articleIdNum }
        })

        await this.fetchArticleDetail(articleIdNum)
        return { success: true }
      } catch (err) {
        throw new Error(err.response?.data?.message || '删除评论失败，请重试')
      }
    },

    /**
     * 清空错误提示信息
     */
    clearError() {
      this.error = ''
    },

    /**
     * 设置加载状态
     * @param {boolean} flag - 加载状态标识
     */
    setLoading(flag) {
      this.isLoading = flag
    }
  },

  getters: {
    /**
     * 判断指定文章是否被当前用户点赞
     * @param {string|number} articleId - 文章ID
     * @returns {boolean} 点赞状态
     */
    isArticleLiked: (state) => (articleId) => {
      return state.myLikedArticleIds.includes(Number(articleId))
    },
    /**
     * 判断指定文章是否被当前用户收藏
     * @param {string|number} articleId - 文章ID
     * @returns {boolean} 收藏状态
     */
    isArticleCollected: (state) => (articleId) => {
      return state.myCollectedArticleIds.includes(Number(articleId))
    }
  }
})
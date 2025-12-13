// @store/user.js (If you see this message, that means this file has been checked and can be put into production environment)

import { defineStore } from 'pinia'
import request from '@/utils/request'
import router from '@/router'

/**
 * 用户状态管理 Store
 * @description 基于 Pinia 实现用户登录态、Token 管理、权限控制等核心逻辑
 * @exports useUserStore - 用户状态操作钩子
 */
export const useUserStore = defineStore('user', {
  /**
   * Store 状态定义
   * @property {boolean} isLoggedIn - 用户是否登录
   * @property {string} username - 用户名
   * @property {number|null} userId - 用户唯一标识ID
   * @property {string} token - 访问令牌 access_token
   * @property {string} tokenType - Token 类型（默认 Bearer）
   * @property {number} expiresIn - Token 总有效期（单位：秒）
   * @property {number|null} refreshTimer - Token 自动刷新定时器ID
   * @property {boolean} isRefreshing - Token 刷新并发锁
   * @property {number} loginTime - 登录/刷新Token的时间戳（毫秒）
   * @property {Function|null} visibilityChangeListener - 标签页可见性监听函数引用
   */
  state: () => ({
    isLoggedIn: false, // 标识用户是否处于已登录状态
    username: '', // 存储用户名
    userId: null, // 后端返回的用户唯一标识 ID
    token: '', // access_token
    tokenType: 'Bearer',
    expiresIn: 0, // Token 的总有效期（单位：秒）
    refreshTimer: null, // 自动刷新 Token 定时器 ID
    isRefreshing: false, // Token 刷新的并发锁
    loginTime: 0, // 登录 / 刷新 Token 的时间戳（毫秒），和 expiresIn 配合计算 Token 剩余有效期
    visibilityChangeListener: null // 标签页可见性监听的函数引用，用于移除监听事件（比如切回标签页时检查 Token 有效期）
  }),

  /**
   * Store 计算属性（Getters）
   * @description 基于 State 动态计算的响应式只读属性
   */
  getters: {
    /**
     * 计算 Token 剩余有效时间
     * @returns {number} Token 剩余有效时间（单位：毫秒），0 表示无有效 Token
     * @description 结合登录时间和 Token 总有效期，精准计算剩余有效时长
     */
    remainTokenTime() {
      // 如果没有登录或没有 Token 总有效期，直接返回0（表示无有效Token）
      if (!this.loginTime || !this.expiresIn) return 0
      // 计算Token的过期时间戳（毫秒）
      const expireTime = this.loginTime + this.expiresIn * 1000
      // 计算剩余有效时间
      return expireTime - Date.now()
    }
  },

  /**
   * Store 方法（Actions）
   * @description 处理异步操作和状态修改，包含登录、登出、Token 刷新等核心逻辑
   */
  actions: {

    /**
     * 登录态初始化
     * @description 解决页面刷新后登录态丢失问题，从 localStorage 恢复登录信息并初始化定时器
     * @returns {void}
     */
    init() {
      try {
        // localStorage 是浏览器提供的本地持久化存储 API（属于 Web Storage 规范）
        // 数据存在浏览器里，除非手动删除（代码删 / 用户清浏览器缓存），否则即使关闭页面、重启浏览器，数据也不会丢 
        //     —— 这也是代码里用它存登录信息的核心原因（刷新页面后还能恢复登录态）
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          if (user.token && user.tokenType) {
            this.isLoggedIn = true
            this.username = user.username || ''
            this.userId = user.userId || null
            this.token = user.token
            this.tokenType = user.tokenType
            this.expiresIn = user.expiresIn || 0
            this.loginTime = user.loginTime || Date.now()
            this.setAuthHeader()
            this.setupRefreshTimer()
          } else {
            this.resetState()
            localStorage.removeItem('user')
          }
        } else {
          this.resetState()
        }
      } catch (error) {
        console.error('用户状态初始化失败：', error)
        this.resetState()
        localStorage.removeItem('user')
      }
    },

    /**
     * 用户登录
     * @param {string} email - 用户登录邮箱
     * @param {string} password - 用户登录密码
     * @returns {Promise<boolean>} 登录成功返回 true，失败抛出异常
     * @description 完成登录核心流程，存储登录信息到 localStorage 和 Store，初始化 Token 刷新定时器
     */
    async login(email, password) {
      try {
        const response = await request.post('/users/login', { email, password })
        const loginData = response

        if (!loginData.access_token || !loginData.token_type) {
          throw new Error('登录失败：未获取到有效 Token')
        }

        const now = Date.now()
        const userData = {
          userId: loginData.user_id || null,
          token: loginData.access_token,
          tokenType: loginData.token_type,
          expiresIn: loginData.expires_in || 0,
          username: email.split('@')[0],
          loginTime: now
        }

        localStorage.setItem('user', JSON.stringify(userData))
        this.$patch(userData)
        this.isLoggedIn = true
        this.setAuthHeader()
        this.setupRefreshTimer()

        return true
      } catch (error) {
        this.resetState()
        localStorage.removeItem('user')
        throw error
      }
    },

    /**
     * 刷新 Token
     * @returns {Promise<string>} 刷新后的新 Token
     * @description 实现 Token 自动续命，处理并发刷新场景，失败则强制登出
     */
    async refreshToken() {
      if (this.isRefreshing) {
        return new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            clearInterval(check)
            reject(new Error('Token刷新超时'))
          }, 10000)

          const check = setInterval(() => {
            if (!this.isRefreshing) {
              clearTimeout(timeout)
              clearInterval(check)
              this.token ? resolve(this.token) : reject(new Error('刷新后无有效Token'))
            }
          }, 100)
        })
      }

      try {
        this.isRefreshing = true

        const response = await request.post('/users/refresh', {
          token: this.token
        })

        const newToken = response.new_token || response.access_token
        if (!newToken) {
          throw new Error('刷新Token失败：未返回有效token')
        }

        const newTokenType = response.token_type || this.tokenType

        this.token = newToken
        this.tokenType = newTokenType
        this.loginTime = Date.now()

        const userData = JSON.parse(localStorage.getItem('user')) || {}
        userData.token = newToken
        userData.tokenType = newTokenType
        userData.loginTime = this.loginTime
        localStorage.setItem('user', JSON.stringify(userData))

        this.setAuthHeader()
        this.setupRefreshTimer()

        console.log('Token刷新成功')
        return newToken
      } catch (error) {
        console.error('Token刷新失败，强制登出：', error)
        this.logout()
        throw error
      } finally {
        this.isRefreshing = false
      }
    },

    /**
     * 设置 Token 刷新定时器
     * @returns {void}
     * @description 精准控制 Token 刷新时机（剩余90秒时刷新），处理标签页切换的边界问题
     */
    setupRefreshTimer() {
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer)
        this.refreshTimer = null
      }

      if (this.visibilityChangeListener) {
        document.removeEventListener('visibilitychange', this.visibilityChangeListener)
        this.visibilityChangeListener = null
      }

      const targetRefreshRemain = 90 * 1000
      const currentRemain = this.remainTokenTime

      let delayMs = currentRemain - targetRefreshRemain

      if (delayMs > 0) {
        this.refreshTimer = setTimeout(async () => {
          console.log(`Token剩余90秒过期，触发自动刷新`)
          await this.refreshToken()
        }, delayMs)
        console.log(`Token将在${Math.round(delayMs/1000)}秒后刷新（剩余90秒过期时）`)
      } else {
        console.warn('Token剩余时间≤90秒，立即刷新')
        this.refreshToken().catch(err => console.error('立即刷新失败：', err))
      }

      this.visibilityChangeListener = async () => {
        if (document.visibilityState === 'visible' && this.isLoggedIn) {
          const remain = this.remainTokenTime
          if (remain < targetRefreshRemain) {
            console.log('切回页面，Token剩余时间<90秒，立即刷新')
            await this.refreshToken()
          }
        }
      }
      document.addEventListener('visibilitychange', this.visibilityChangeListener)
    },

    /**
     * 设置请求鉴权头
     * @returns {void}
     * @description 给 axios 实例添加全局 Authorization 头，作为冗余确保鉴权可用（request 拦截器已实现）
     */
    setAuthHeader() {
      request.defaults.headers.common['Authorization'] = `${this.tokenType} ${this.token}`
    },

    /**
     * 用户登出
     * @returns {Promise<void>}
     * @description 清除定时器、监听事件，调用后端登出接口，重置状态并跳转登录页
     */
    async logout() {
      if (this.refreshTimer) {
        clearTimeout(this.refreshTimer)
        this.refreshTimer = null
      }

      if (this.visibilityChangeListener) {
        document.removeEventListener('visibilitychange', this.visibilityChangeListener)
        this.visibilityChangeListener = null
      }

      if (this.token) {
        try {
          await request.post('/users/logout', { token: this.token })
          console.log('后端登出成功')
        } catch (error) {
          console.error('后端登出失败：', error)
        }
      }

      this.resetState()
      localStorage.removeItem('user')
      request.defaults.headers.common['Authorization'] = ''
      router.push('/app/login').catch(err => {})
    },

    /**
     * 重置用户状态
     * @returns {void}
     * @description 清空 Store 中所有用户相关状态，恢复初始值
     */
    resetState() {
      this.isLoggedIn = false
      this.username = ''
      this.userId = null
      this.token = ''
      this.tokenType = 'Bearer'
      this.expiresIn = 0
      this.refreshTimer = null
      this.isRefreshing = false
      this.loginTime = 0
      this.visibilityChangeListener = null
    }
  }
})
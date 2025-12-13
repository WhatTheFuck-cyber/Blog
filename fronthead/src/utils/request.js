// @utils/request.js (If you see this message, that means this file has been checked and can be put into production environment)

import axios from 'axios'
import pinia from '@/store'
import { useUserStore } from '@/store/user'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  timeout: 5000 // 5秒超时
})

// 存储等待刷新 Token 的请求队列（解决并发请求重试问题）
let refreshRequestQueue = []

/**
 * 刷新 Token 成功后处理请求队列
 * @param {string} token - 刷新后的新 Token
 * @description 遍历队列，给每个请求更新新 Token 并重新发起请求，最后清空队列
 */
const resolveQueue = (token) => {
  refreshRequestQueue.forEach(cb => cb(token))
  refreshRequestQueue = []
}

// 请求拦截器：给请求自动加 Token。精简 Token 检查逻辑，对齐前端保底的 90 秒刷新规则
request.interceptors.request.use(
  /**
   * 请求发送前的拦截处理逻辑
   * @param {Object} config - axios 请求配置对象（包含URL、请求头、参数等）
   * @returns {Object} 处理后的请求配置（自动添加Authorization头）
   */
  (config) => {
    // 1. 拿到全局的用户状态（是否登录、Token 是啥）
    const userStore = useUserStore(pinia)
    console.log('axios 请求拦截器 userStore：', userStore)

    // 2. 如果用户已登录、有 Token → 自动给请求头加 Token
    if (userStore.isLoggedIn && userStore.token) {
      // Authorization 是后端约定的“身份凭证字段”，格式一般是「Token类型 + Token值」
      config.headers.Authorization = `${userStore.tokenType} ${userStore.token}`
    }

    // 把加好 Token 的请求配置返回，请求才能正常发出去
    return config
  },
  /**
   * 请求发送失败的拦截处理逻辑
   * @param {Error} error - 请求发送失败的错误对象
   * @returns {Promise<never>} 拒绝状态的 Promise，抛出自定义错误
   */
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  /**
   * 响应成功的拦截处理逻辑
   * @param {Object} response - axios 完整响应对象（包含data、status、headers等）
   * @returns {Object} 后端返回的业务数据（直接返回response.data，简化业务层调用）
   */
  (response) => response.data,

  /**
   * 响应失败的拦截处理逻辑（适配双Token机制）
   * @param {Error} error - 响应失败的错误对象（包含config、response等属性）
   * @returns {Promise<any>} 重试后的请求Promise / 拒绝状态的Promise
   * @description 核心处理401 Token过期场景：自动刷新Token并重试请求；刷新失败则自动登出并记录跳转路径
   */
  async (error) => {
    // 1. 先拿到用户状态 + 报错请求的配置
    const userStore = useUserStore(pinia)
    console.log('axios 响应拦截器 userStore：', userStore)

    // 处理 config 为 undefined 的情况
    const originalRequest = error.config || {}
    
    // 2. 定义几个“判断开关”，避免写一堆嵌套 if
    const isRefreshApi = originalRequest.url?.includes('/users/refresh') // 是不是刷 Token 的接口
    const is401 = error.response?.status === 401 // 是不是 Token 过期报错
    const isLoggedIn = userStore.isLoggedIn // 用户是不是登录了
    const hasRetried = originalRequest._retry // 是不是已经重试过

    // 3. 核心场景：Token 过期了，但用户还登录着、没重试过、不是刷 Token 接口本身报错 → 重试
    if (is401 && isLoggedIn && !hasRetried && !isRefreshApi) {
      originalRequest._retry = true // 标记“已经重试过了”，防止死循环

      try {
        // 子场景1：正在刷 Token（比如同时发了3个请求，第一个已经在刷 Token 了）
        if (userStore.isRefreshing) {
          // 返回一个“承诺”：等 Token 刷好后，再重试这个请求
          return new Promise(resolve => {
            // 把“重试这个请求的操作”加到队列里
            refreshRequestQueue.push((newToken) => {
              // newToken 是刷好的新 Token → 给这个请求更新 Token
              originalRequest.headers.Authorization = `${userStore.tokenType} ${newToken}`
              // 重新发起这个请求，完成“承诺”
              resolve(request(originalRequest))
            })
          })
        }

        // 子场景2：没在刷 Token → 主动去刷 Token
        const newToken = await userStore.refreshToken()
        // 刷成功后，把队列里的所有请求都重试一遍
        resolveQueue(newToken)
        originalRequest.headers.Authorization = `${userStore.tokenType} ${newToken}`
        return request(originalRequest)
      } catch (refreshErr) {
        // 刷 Token 失败了（比如 RefreshToken 也过期了）→ 兜底处理
        refreshRequestQueue = [] // 清空待办清单
        userStore.logout() // 自动登出
        const currentPath = window.location.pathname // 拿到当前页面路径
        if (currentPath !== '/login') {
          // 记住当前页面，登录后跳回来（比如用户在/article/1页登出，登录后直接回这个页）
          localStorage.setItem('redirectAfterLogin', currentPath)
        }
        return Promise.reject(refreshErr) // 告诉业务层“刷 Token 失败了”
      }
    }

    // 4. 其他 401 情况（比如没登录就访问需要权限的接口、刷 Token 接口本身报错）→ 兜底处理
    if (is401) {
      userStore.logout() // 直接登出
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && !isRefreshApi) {
        localStorage.setItem('redirectAfterLogin', currentPath)
      }
    }

    // 5. 非 401 错误（比如 500 服务器挂了、404 接口不存在）→ 直接抛错给业务层
    return Promise.reject(error)
  }
)

// 导出 axios 实例
export default request


/**
Promise：「异步操作的 “承诺书”」，用来处理 “不是立刻能拿到结果” 的操作（比如发接口请求、刷 Token）
Promise 的核心特性
  三种状态：
    pending（进行中）：操作还没完成；
    fulfilled（已成功）：操作完成，拿到结果；
    rejected（已失败）：操作出错，拿到错误。
    状态一旦确定就不能改：比如从 pending 变成 fulfilled 后，就永远是成功状态；
  核心方法：
    new Promise((resolve, reject) => { ... })：创建承诺书，resolve 是 “操作成功时调用”，reject 是 “操作失败时调用”；
    await：等待承诺书完成（只能用在 async 函数里）；
    Promise.reject(error)：返回一个 “失败的承诺书”，告诉调用者 “操作失败了”。


响应失败（重点讲 401 场景的调用逻辑）：

场景前提：
  用户已登录，但 Token 过期；
  同时调用 request.get('/articles') 和 request.get('/categories')；
  两个请求都返回 401 → 进入响应拦截器的失败回调。

第一个请求（查文章）进入失败回调：async (error)...
  userStore.refreshToken() 是异步操作（比如调用 /users/refresh 接口），返回 Promise → await 会等它完成；
  在刷 Token 的过程中，userStore.isRefreshing 会被设为 true（store 里的逻辑）→ 第二个请求进来时，会触发 “排队逻辑”。

第二步：第二个请求（查分类）进入失败回调（此时正在刷 Token）：async (error)...
关键调用点：
  第二个请求不会重复刷 Token，而是返回一个 “待完成的 Promise”；
  refreshRequestQueue 此时变成：[ (newToken) => { 重试/分类请求 } ]；
  这个 Promise 会 “挂起”，直到 resolve 被调用（也就是刷 Token 成功后）。

第三步：第一个请求的刷 Token 完成，触发队列执行：resolveQueue(newToken)
resolveQueue 的调用逻辑：
  const resolveQueue = (token) => {
    // 遍历队列里的cb函数，逐个执行
    refreshRequestQueue.forEach(cb => cb(token)) 
    refreshRequestQueue = [] // 清空队列
  }
cb(token) 就是执行队列里的「重试 / 分类请求」函数；
执行 cb(newToken) 时，会给 /categories 请求更新新 Token，重新发起请求，并调用 resolve → 第二个请求的 Promise 完成；
第一个请求也会重新发起 /articles 请求，拿到数据。

在基于 axios 封装的请求层中，依托双 Token（Access Token/Refresh Token）机制实现了 Token 过期后的无感刷新：
  Access Token 作为业务请求的身份凭证（短有效期、高业务权限），会在请求拦截器中自动附加到请求头；
  当业务请求因 Access Token 过期返回 401 错误时，响应拦截器会先判断是否为首次重试、是否处于登录状态且非刷新接口本身报错，
    若满足则由第一个过期请求触发 Refresh Token 刷新逻辑 —— 向后端发起刷新请求时，携带有效期更长、仅用于刷新操作的有效 Refresh Token，
    后端校验该 Refresh Token 有效后返回新的 Access Token；
  在此期间，其他并发的 401 请求会进入队列并返回挂起的 Promise 等待，
    待新 Access Token 获取成功后，遍历队列执行所有待重试请求（更新请求头为新 Access Token 并重新发起），
  全程用户无感知；
    若 Refresh Token 失效等导致刷新失败，则清空请求队列、自动登出用户并记录当前页面路径，以便用户重新登录后跳转回原页面；
    双 Token 机制从根本上解决了单 Token 模式下 “Token 过期后刷新接口因无有效凭证无法调用” 的问题，是实现无感刷新的核心保障。
*/
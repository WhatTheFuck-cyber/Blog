// @router/index.js (If you see this message, that means this file has been checked and can be put into production environment)

import { createRouter, createWebHistory } from 'vue-router'
import pinia from '@/store'
import { useUserStore } from '@/store/user'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'StartPage',
    component: () => import('@/views/Start.vue'), // 「开始」页面组件
    meta: { requiresAuth: false }
  },
  {
    path: '/app',
    component: () => import('@/components/Layout.vue'), // 通用布局
    children: [
      { 
        path: '', 
        redirect: 'app/home' // 根路径重定向到主页
      },
      { 
        path: 'home', 
        name: 'Home', 
        component: () => import('@/views/Home.vue'), 
        meta: { requiresAuth: false } // 无需登录即可访问
      },
      { 
        path: 'about', 
        name: 'About', 
        component: () => import('@/views/About.vue'),
        meta: { requiresAuth: false } 
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { requiresAuth: false, hiddenWhenLogin: true } // 登录后隐藏该路由
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/Register.vue'),
        meta: { requiresAuth: false, hiddenWhenLogin: true }
      },
      {
        path: 'articles/:id',
        name: 'article-detail',
        component: () => import('@/views/ArticleDetail.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: 'categories/:id',
        name: 'category',
        component: () => import('@/views/Category.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: 'search',
        name: 'search-results',
        component: () => import('@/views/SearchResults.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/userpage',
    component: () => import('@/components/UserPage'), // 通用布局
    children:[
      { 
        path: '', 
        redirect: 'userpage/userhome' // 根路径重定向到用户主页
      },
      {
        path: 'userhome',
        name: 'UserPage',
        component: () => import('@/views/UserHome.vue'),
        meta: { requiresAuth: true } // 需要登录才能访问
      },
      {
        path: 'userpublish',
        name: 'UserPublish',
        component: () => import('@/views/UserPublish.vue'),
        meta: { requiresAuth: true } // 需要登录才能访问
      },
      {
        path: 'usertrack',
        name: 'UserTrack',
        component: () => import('@/views/UserTrack.vue'),
        meta: { requiresAuth: true } // 需要登录才能访问
      },
    ]
  },
  {
    path: '/article',
    component: () => import('@components/ArticleWriteBase.vue'),
    children:[
      {
        path: '',
        redirect: '/:pathMatch(.*)*',
      },
      {
        path: 'create',
        name: 'CreateArticle',
        component: () => import('@/views/ArticleCreate.vue'),
        meta: { requiresAuth: true } // 需要登录才能访问
      },
      {
        path: 'revise/:articleId', // 动态路由参数，可由route.params.articleId获取
        name: 'ReviseArticle',
        component: () => import('@/views/ArticleRevise.vue'),
        meta: { requiresAuth: true } // 需要登录才能访问
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'), // 「404 Not Found」页面组件
    meta: { requiresAuth: false }
  }
]

/**
 * 创建路由实例
 * @description 基于HTML5 History模式创建Vue Router实例，绑定路由配置
 * @returns {Router} Vue Router实例对象
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 优化：处理重复跳转警告
const originalPush = router.push

/**
 * 重写路由push方法
 * @param {string|Location} location - 跳转的目标路由地址（字符串/路由对象）
 * @returns {Promise} 路由跳转的Promise对象
 * @description 解决重复跳转同一路由时的NavigationDuplicated警告，仅忽略该类型警告，其他错误正常抛出
 */
router.push = function push(location) {
  return originalPush.call(this, location).catch(err => {
    // 只忽略“重复跳转同一路由”的警告，其他错误正常抛出
    if (err.name !== 'NavigationDuplicated') {
      throw err
    }
  })
}

/**
 * 全局路由前置守卫
 * @param {RouteLocationNormalized} to - 即将进入的目标路由对象
 * @param {RouteLocationNormalized} from - 当前正要离开的路由对象
 * @param {Function} next - 路由守卫的放行/跳转函数
 * @description 落地路由meta字段的权限控制逻辑：
 * 1. 已登录用户禁止访问登录/注册页，自动跳转到主页
 * 2. 未登录用户禁止访问需要权限的页面，自动跳转到登录页
 * 3. 其他情况正常放行
 */
router.beforeEach((to, from, next) => {
  const userStore = useUserStore(pinia) // 获取用户登录状态
  userStore.init()
  console.log('路由守卫 userStore：', userStore) // 调试userStore地址一致性

  // 规则1：拦截“已登录用户访问登录/注册页”
  // 这个实际上不怎么起作用，因为处于登录状态是无法显示”登录“和”注册“按钮的，也就避免了访问这两个页面
  if (to.meta.hiddenWhenLogin && userStore.isLoggedIn) {
    next({ name: 'Home' }) // 跳转到主页
    return
  }

  // 规则2：拦截“未登录用户访问需要登录的页面”
  // 目前没有什么作用，后续添加页面的时候可能会用到
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login' }) // 跳转到登录页
    return
  }

  // 正常情况：放行
  next()
})

// 导出路由实例
export default router
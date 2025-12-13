<template>
  <!-- 登录页根容器：全屏弹性布局居中，浅灰背景营造简洁登录氛围，适配不同屏幕高度 -->
  <div class="auth-container">
    <!-- 登录卡片：核心交互容器，绑定震动动画（登录失败触发），hover上浮强化交互质感 -->
    <div class="auth-card" ref="cardRef" :class="{ 'card-shake': isShake }">
      <h2 class="auth-title">登录</h2>
      <!-- 标题分隔线：渐变蓝色主题线，居中展示，强化视觉层级 -->
      <div class="auth-divider" style="background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);"></div>
      
      <!-- 邮箱输入项：绑定邮箱响应式数据，输入时清除卡片震动状态，空值兜底提示 -->
      <div class="form-item">
        <label class="form-label">电子邮箱</label>
        <input 
          type="text" 
          class="form-input" 
          v-model="email"  
          placeholder="请输入你的邮箱"
          @input="clearShake"
        >
      </div>

      <!-- 密码输入项：含密码显隐切换功能，输入时清除卡片震动状态 -->
      <div class="form-item">
        <label class="form-label">密码</label>
        <!-- 密码框包裹容器：相对定位，作为密码显隐图标的定位参考容器 -->
        <div class="input-wrapper">
          <input 
            :type="showPassword ? 'text' : 'password'"
            class="form-input" 
            v-model="password" 
            placeholder="请输入你的密码"
            @input="clearShake"
          >
          <!-- 密码显示/隐藏切换图标：点击切换显隐状态，hover主题色反馈 -->
          <div 
            class="password-toggle-icon" 
            @click="showPassword = !showPassword"
          >
            <i class="fa-solid" :class="!showPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
          </div>
        </div>
      </div>

      <!-- 登录错误提示：登录失败时显示，红色系视觉提示，左边框强化警示 -->
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

      <!-- 登录按钮：禁用逻辑（加载中/邮箱/密码为空），点击触发登录请求，加载中显示状态文案 -->
      <button 
        type="button" 
        class="auth-btn" 
        :disabled="isBtnDisabled"
        @click="handleLogin"
        style="background: linear-gradient(90deg, #3498db 0%, #2980b9 100%);"
      >
        {{ isLoading ? '登录中...' : '确认登录' }}
      </button>

      <!-- 注册链接：引导无账号用户跳转注册页，hover下划线+主题色反馈 -->
      <p class="auth-link">
        还没有账号？ <router-link to="/app/register">点击这里注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页组件
 * @description 系统登录核心页面，包含邮箱/密码表单验证、密码显隐切换、登录状态反馈（加载/错误/震动动画）、登录成功跳转首页、未注册引导跳转注册页
 * @feature 1. 表单实时验证（邮箱/密码非空），按钮禁用逻辑 2. 密码显隐切换（自定义图标，兼容各浏览器） 3. 登录请求状态管理（加载中禁用按钮） 4. 登录失败反馈（错误提示+卡片震动动画） 5. 登录成功跳转首页并回到顶部 6. 输入交互（输入时清除错误/震动状态） 7. 响应式适配移动端 8. 统一蓝色主题视觉风格
 * @dependencies 
 *  - vue-router: 编程式导航（登录成功跳转首页、注册链接路由跳转）
 *  - pinia (useUserStore): 用户状态管理（调用登录接口、存储登录状态）
 *  - font-awesome: 密码显隐切换图标
 */
// 导入Vue核心API：响应式数据(ref)、计算属性(computed)
import { ref, computed } from 'vue'
// 导入Vue Router实例：实现编程式路由跳转（首页/注册页）
import { useRouter } from 'vue-router'
// 导入Pinia用户状态管理：调用登录接口、管理用户登录状态
import { useUserStore } from '@/store/user'

// 初始化核心实例
const userStore = useUserStore() // 用户状态管理实例（登录接口调用、登录状态存储）

/** @type {import('vue-router').Router} 路由 */
const router = useRouter()
/** @type {Ref<string>} 邮箱输入框绑定值，初始为空字符串 */
const email = ref('')
/** @type {Ref<string>} 密码输入框绑定值，初始为空字符串 */
const password = ref('')
/** @type {Ref<string>} 登录错误提示文案，登录失败时赋值，初始为空 */
const errorMessage = ref('')
/** @type {Ref<boolean>} 登录请求加载状态，控制按钮禁用/文案切换 */
const isLoading = ref(false)
/** @type {Ref<boolean>} 卡片震动动画触发状态，登录失败时置为true */
const isShake = ref(false)
/** @type {Ref<boolean>} 密码显示/隐藏切换状态，false为隐藏（默认），true为显示 */
const showPassword = ref(false)

/**
 * 计算属性：登录按钮禁用逻辑
 * @returns {boolean} 禁用状态（加载中/邮箱为空/密码为空时返回true）
 */
const isBtnDisabled = computed(() => {
  return isLoading.value || !email.value.trim() || !password.value.trim()
})

/**
 * 清除卡片震动状态
 * @description 输入框输入时触发，重置震动动画状态，提升输入体验
 * @returns {void}
 */
const clearShake = () => {
  isShake.value = false
}

/**
 * 登录处理核心方法
 * @description 1. 置为加载状态，清空错误提示和震动状态 2. 调用用户store的登录接口 3. 成功则跳转首页并回到顶部 4. 失败则显示错误提示+触发卡片震动（300ms后重置） 5. 最终结束加载状态
 * @async 异步方法（调用登录接口）
 * @returns {Promise<void>}
 */
const handleLogin = async () => {
  // 初始化请求状态
  isLoading.value = true
  errorMessage.value = ''
  isShake.value = false
  
  try {
    // 调用登录接口（传入去空格后的邮箱/密码）
    await userStore.login(email.value.trim(), password.value.trim())
    // 登录成功：跳转首页并回到页面顶部
    router.push('/app/home').then(() => {
      window.scrollTo(0, 0)
    })
  } catch (error) {
    // 登录失败：显示错误提示+触发震动动画
    errorMessage.value = '登录失败，请检查账号密码'
    isShake.value = true
    // 300ms后重置震动状态（匹配动画时长，避免持续震动）
    setTimeout(() => {
      isShake.value = false
    }, 300)
  } finally {
    // 无论成功/失败，结束加载状态
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 
 * 登录页样式总说明：
 * 1. 设计原则：简洁易用+视觉统一（蓝色主题）+ 交互反馈（hover/震动/焦点）+ 响应式适配
 * 2. 视觉风格：浅灰背景+白色卡片+蓝色渐变，符合现代登录页设计趋势
 * 3. 交互体验：卡片hover上浮、输入框focus高亮、密码图标hover变色、登录失败震动
 * 4. 兼容性：隐藏浏览器原生密码图标、适配移动端/PC端
 * 5. 层级关系：标题>表单>按钮>辅助链接，通过字号/颜色/间距区分
 */

/* 登录页根容器：最小高度100vh（占满屏幕）+ 弹性布局居中 + 浅灰背景 + 内边距适配小屏 */
.auth-container {
  min-height: 100vh;
  padding: 2rem 1rem;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; /* 多字体兼容，保证跨系统显示一致 */
}

/* 登录卡片：最大宽度限制+白色背景+圆角+阴影+hover上浮动画，核心交互容器 */
.auth-card {
  width: 100%;
  max-width: 450px; /* 限制最大宽度，避免大屏过宽 */
  background: #ffffff;
  border-radius: 16px; /* 大圆角提升现代感 */
  box-shadow: 0 8px 24px rgba(129, 140, 153, 0.1); /* 轻微阴影提升层次感 */
  padding: 3rem 2.5rem;
  transition: all 0.3s ease; /* 过渡动画，保证hover/震动流畅 */
}
/* 卡片hover效果：轻微上浮+阴影加深，强化可交互感知 */
.auth-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(129, 140, 153, 0.18);
}

/* 卡片震动动画：登录失败触发，左右小幅度晃动，增强错误反馈 */
.card-shake {
  animation: card-shake 0.5s ease;
}
/* 震动动画关键帧：0/100%初始位置，20/60%左移，40/80%右移，模拟震动效果 */
@keyframes card-shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-3px); }
  40%, 80% { transform: translateX(3px); }
}

/* 登录标题：居中+大号字体+深灰色+字重，突出核心标题 */
.auth-title {
  font-size: 2rem;
  color: #2d3748; /* 深灰色，保证可读性 */
  margin: 0 0 1.2rem 0;
  font-weight: 600;
  text-align: center;
}

/* 标题分隔线：居中+窄宽度+渐变背景，视觉分割标题与表单 */
.auth-divider {
  height: 2px;
  width: 70px; /* 短横线，避免视觉占比过大 */
  border-radius: 1px;
  margin: 0 auto 2.5rem; /* 水平居中，底部间距分隔表单 */
}

/* 表单项：底部固定间距，保证表单元素垂直分布均匀 */
.form-item {
  margin-bottom: 1.8rem;
}

/* 表单标签：块级显示+深灰色+字重+底部间距，清晰标注输入项 */
.form-label {
  display: block; /* 独占一行，避免与输入框同行 */
  color: #2d3748;
  font-weight: 600;
  margin-bottom: 0.7rem;
  font-size: 1.05rem; /* 微放大，提升可读性 */
}

/* 表单输入框：宽度100%+内边距+浅灰背景+圆角+focus高亮，提升输入体验 */
.form-input {
  width: 100%;
  padding: 1rem 1.2rem;
  border: 1px solid #e2e8f0; /* 浅灰边框，弱化边框视觉 */
  border-radius: 8px;
  font-size: 1.05rem;
  color: #2d3748;
  background-color: #f5f7fa; /* 浅灰背景，区分输入区域 */
  transition: all 0.3s ease; /* 过渡动画，focus状态切换流畅 */
}
/* 占位符样式：浅灰色，弱化显示，避免干扰输入 */
.form-input::placeholder {
  color: #94a3b8;
  opacity: 1; /* 修复部分浏览器占位符透明度问题 */
}
/* 输入框focus状态：清除默认轮廓+主题色边框+轻微阴影，强化焦点 */
.form-input:focus {
  outline: none;
  border-color: #3498db; /* 主题蓝色，统一视觉 */
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1); /* 外发光，不突兀 */
  background-color: #ffffff; /* 聚焦时白色背景，提升输入清晰度 */
}

/* 登录按钮：宽度100%+大内边距+圆角+渐变背景+hover/禁用态，突出核心操作 */
.auth-btn {
  width: 100%; /* 占满卡片宽度，提升点击热区 */
  padding: 1.1rem;
  border: none; /* 清除默认边框 */
  border-radius: 8px;
  color: #ffffff;
  font-size: 1.05rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s ease;
  margin-top: 0.8rem;
}
/* 按钮hover（非禁用）：透明度降低，强化交互反馈 */
.auth-btn:hover:not(:disabled) {
  opacity: 0.9;
}
/* 按钮禁用态：灰色背景+禁止光标+低透明度，明确不可点击状态 */
.auth-btn:disabled {
  background: #95a5a6; /* 灰色，区分可点击状态 */
  cursor: not-allowed;
  opacity: 0.8;
}

/* 注册链接：居中+浅灰色+底部间距，作为辅助操作引导 */
.auth-link {
  text-align: center;
  margin-top: 1.8rem;
  color: #7f8c8d; /* 浅灰色，弱化辅助文字 */
  font-size: 1rem;
}
/* 注册链接跳转样式：主题蓝色+无下划线+hover变色/下划线，引导点击 */
.auth-link router-link,
.auth-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}
.auth-link router-link:hover,
.auth-link a:hover {
  color: #2980b9; /* 深色主题蓝，强化hover */
  text-decoration: underline;
}

/* 错误提示：左红边框+浅红背景+居中+内边距，突出错误提示，不刺眼 */
.error-message {
  color: #e74c3c; /* 红色警示色 */
  font-size: 0.95rem;
  text-align: center;
  margin-top: 1.2rem;
  padding: 0.8rem;
  background: rgba(231, 76, 60, 0.05); /* 浅红背景，弱化视觉冲击 */
  border-radius: 4px;
  border-left: 3px solid #e74c3c; /* 左侧红条，强化警示 */
}

/* 密码框包裹容器：相对定位，为密码显隐图标提供绝对定位参考 */
.input-wrapper {
  position: relative;
  width: 100%;
}
/* 密码输入框：右侧预留空间（48px），避免文字被图标遮挡 */
.input-wrapper .form-input {
  padding-right: 48px;
}
/* 密码显示/隐藏图标：绝对定位右侧+垂直居中+hover主题色，交互友好 */
.password-toggle-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%); /* 垂直居中 */
  color: #94a3b8; /* 浅灰色，弱化默认状态 */
  font-size: 18px;
  cursor: pointer;
  z-index: 10; /* 保证在输入框上层 */
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
/* 密码图标hover：主题蓝色，强化交互反馈 */
.password-toggle-icon:hover {
  color: #3498db;
}
/* 隐藏浏览器原生密码图标：兼容IE/Chrome/Firefox，保证自定义图标唯一显示 */
.form-input::-ms-reveal,
.form-input::-webkit-credentials-auto-fill-button {
  display: none !important;
  visibility: hidden;
}

/* 移动端适配（480px以下，手机端）：调整卡片尺寸/内边距，保证小屏适配 */
@media (max-width: 480px) {
  .auth-card {
    max-width: 90%; /* 占屏幕90%宽度，避免边缘挤压 */
    padding: 2.5rem 1.8rem; /* 减少内边距，适配小屏高度 */
  }
  .form-input {
    padding: 0.9rem 1rem; /* 减少输入框内边距，节省空间 */
  }
  .input-wrapper .form-input {
    padding-right: 48px; /* 保留右侧空间，避免图标遮挡密码 */
  }
}
</style>
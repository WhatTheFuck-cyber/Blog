<template>
  <!-- 注册页根容器：全屏弹性垂直居中布局，浅灰背景营造简洁注册氛围，适配不同屏幕高度 -->
  <div class="auth-container">
    <!-- 注册卡片：核心交互容器，绑定震动动画（注册失败/表单校验失败触发），hover上浮强化交互质感 -->
    <div class="auth-card" ref="cardRef" :class="{ 'card-shake': isShake }">
      <h2 class="auth-title">注册</h2>
      <!-- 标题分隔线：渐变绿色主题线，居中展示，强化视觉层级（匹配注册页绿色主色调） -->
      <div class="auth-divider" style="background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);"></div>
      
      <!-- 用户名输入项：绑定用户名响应式数据，输入时清除错误/震动/倒计时状态，提示文本引导格式规范 -->
      <div class="form-item">
        <label class="form-label">用户名</label>
        <input 
          type="text" 
          class="form-input" 
          v-model="username"
          placeholder="请输入你的用户名"
          @input="clearShakeAndCountdown"
        >
        <p class="form-hint">仅支持数字和字母，3-20个字符.</p>
      </div>

      <!-- 邮箱输入项：绑定邮箱响应式数据，输入时清除错误/震动/倒计时状态，type="email"基础格式校验 -->
      <div class="form-item">
        <label class="form-label">电子邮箱</label>
        <input 
          type="email" 
          class="form-input" 
          v-model="email"
          placeholder="请输入你的电子邮箱"
          @input="clearShakeAndCountdown"
        >
      </div>

      <!-- 密码输入项：含密码显隐切换功能，输入时清除错误/震动/倒计时状态，提示文本引导密码格式 -->
      <div class="form-item password-item">
        <label class="form-label">密码</label>
        <!-- 密码框包裹容器：相对定位，作为密码显隐图标的定位参考容器 -->
        <div class="input-wrapper">
          <input 
            :type="showPassword ? 'text' : 'password'"
            class="form-input" 
            v-model="password"
            placeholder="请输入你的密码"
            @input="clearShakeAndCountdown"
          >
          <!-- 密码显示/隐藏切换图标：点击切换显隐状态，hover主题色反馈 -->
          <div 
            class="password-toggle-icon" 
            @click="showPassword = !showPassword"
          >
            <i class="fa-solid" :class="!showPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
          </div>
        </div>
        <p class="form-hint">至少6个字符，只能包含数字、字母和!@#$%*.</p>
      </div>

      <!-- 确认密码输入项：同密码框结构，用于校验两次密码一致性，输入时清除错误/震动/倒计时状态 -->
      <div class="form-item password-item">
        <label class="form-label">确认密码</label>
        <div class="input-wrapper">
          <input 
            :type="showConfirmPassword ? 'text' : 'password'" 
            class="form-input" 
            v-model="confirmPassword"
            placeholder="请再次输入你的密码"
            @input="clearShakeAndCountdown"
          >
          <!-- 确认密码显示/隐藏切换图标：独立显隐控制，避免与密码框联动 -->
          <div 
            class="password-toggle-icon" 
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <i class="fa-solid" :class="!showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'"></i>
          </div>
        </div>
      </div>

      <!-- 注册错误提示：表单校验/接口请求失败时显示，红色系视觉提示，左边框强化警示 -->
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
      <!-- 注册成功提示：注册成功后显示，含5秒自动跳转倒计时，绿色系视觉反馈 -->
      <div v-if="successMessage" class="success-message">{{ successMessage }}（剩余 {{ countdown }} 秒）</div>

      <!-- 注册按钮：禁用逻辑（字段为空/加载中），点击触发注册流程，加载中显示状态文案，绿色渐变主题 -->
      <button 
        class="auth-btn" 
        :disabled="isBtnDisabled"
        @click="handleRegister"
        style="background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);"
      >
        {{ isLoading ? '注册中...' : '确认注册' }}
      </button>

      <!-- 登录链接：引导已有账号用户跳转登录页，hover下划线+主题色反馈 -->
      <p class="auth-link">
        已经有账号？ <router-link to="/app/login">点击这里登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * 注册页组件
 * @description 系统注册核心页面，包含用户名/邮箱/密码/确认密码表单校验、密码显隐切换、注册状态反馈（加载/错误/震动动画）、注册成功自动跳转登录页、已有账号引导登录
 * @feature 1. 多维度表单校验（格式/长度/一致性），分无提示/带提示两种校验模式 2. 密码/确认密码独立显隐切换（兼容各浏览器） 3. 注册请求状态管理（加载中禁用按钮） 4. 注册失败反馈（错误提示+卡片震动动画） 5. 注册成功自动倒计时跳转（5秒），支持手动清除倒计时 6. 内存泄漏防护（组件卸载清除定时器、输入时重置状态） 7. 响应式适配移动端 8. 统一绿色主题视觉风格
 * @dependencies 
 *  - vue-router: 编程式导航（注册成功跳转登录页、登录链接路由跳转）
 *  - pinia (useUserStore): 用户状态管理（注册状态存储）
 *  - request工具：发送注册接口请求
 *  - font-awesome: 密码显隐切换图标
 */
// 导入Vue核心API：响应式数据(ref)、计算属性(computed)、DOM更新(nextTick)、组件生命周期(onUnmounted)
import { ref, computed, nextTick, onUnmounted } from 'vue'
// 导入Pinia用户状态管理：管理用户注册状态
import { useUserStore } from '@/store/user'
// 导入请求工具：发送注册接口请求
import request from '@/utils/request'
// 导入Vue Router：实现编程式路由跳转（登录页）
import { useRouter } from 'vue-router'

/** 
 * Vue Router路由跳转实例（编程式导航）
 * @type {import('vue-router').Router} 
 * 用途：实现注册成功跳转登录页、引导用户跳转登录页
 */
const router = useRouter()

/**
 * 响应式数据定义
 * @type {Ref<string>} username - 用户名输入框绑定值，初始为空字符串
 * @type {Ref<string>} email - 邮箱输入框绑定值，初始为空字符串
 * @type {Ref<string>} password - 密码输入框绑定值，初始为空字符串
 * @type {Ref<string>} confirmPassword - 确认密码输入框绑定值，初始为空字符串
 * @type {Ref<string>} errorMessage - 注册错误提示文案，校验/请求失败时赋值，初始为空
 * @type {Ref<string>} successMessage - 注册成功提示文案，注册成功后赋值，初始为空
 * @type {Ref<boolean>} isLoading - 注册请求加载状态，控制按钮禁用/文案切换
 * @type {Ref<boolean>} isShake - 卡片震动动画触发状态，校验/请求失败时置为true
 * @type {Ref<HTMLElement | null>} cardRef - 注册卡片DOM引用，用于动画触发（预留扩展）
 * @type {Ref<boolean>} showPassword - 密码显示/隐藏切换状态，false为隐藏（默认），true为显示
 * @type {Ref<boolean>} showConfirmPassword - 确认密码显示/隐藏切换状态，独立控制，避免与密码框联动
 * @type {Ref<number>} countdown - 注册成功自动跳转倒计时，初始5秒
 */
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)
const isShake = ref(false)
const cardRef = ref(null)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const countdown = ref(5)

/** @type {NodeJS.Timeout | null} 倒计时定时器实例，用于清除定时器防止内存泄漏 */
let countdownTimer = null

// 初始化用户状态管理实例
const userStore = useUserStore()

/**
 * 计算属性：注册按钮禁用逻辑
 * @description 字段为空（用户名/邮箱/密码/确认密码）或请求加载中时，禁用注册按钮
 * @returns {boolean} 禁用状态（true=禁用，false=可用）
 */
const isBtnDisabled = computed(() => {
  // 校验字段是否为空（去空格后）
  const isEmpty = !username.value.trim() || 
                  !email.value.trim() || 
                  !password.value.trim() || 
                  !confirmPassword.value.trim();
  // 空字段或加载中均禁用按钮
  return isEmpty || isLoading.value
})

/**
 * 清除震动状态、提示文案和倒计时定时器（防止内存泄漏）
 * @description 输入框输入时触发，重置错误/成功提示、震动状态，清除旧定时器并重置倒计时，提升输入体验
 * @returns {void}
 */
const clearShakeAndCountdown = () => {
  isShake.value = false
  errorMessage.value = ''
  successMessage.value = ''
  // 清除倒计时定时器（防止多个定时器同时运行）
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdown.value = 5 // 重置倒计时为初始值
}

/**
 * 触发卡片震动动画（注册/校验失败时调用）
 * @description 震动动画时长500ms，匹配CSS动画时长，500ms后自动重置状态，避免持续震动
 * @returns {void}
 */
const triggerCardShake = () => {
  isShake.value = true
  setTimeout(() => {
    isShake.value = false
  }, 500)
}

/**
 * 无提示版表单校验（仅返回布尔值）
 * @description 用于静默校验（如实时输入校验，预留扩展），不显示错误提示，仅返回是否校验失败
 * @returns {boolean} 校验结果（true=校验失败，false=校验通过）
 */
const validateFormWithoutTip = () => {
  // 用户名：3-20位数字/字母
  if (!/^[a-zA-Z0-9]{3,20}$/.test(username.value.trim())) return true;
  // 邮箱：基础邮箱格式
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) return true;
  // 密码：至少6位，包含数字/字母/!@#$%*.
  const pwdReg = /^[a-zA-Z0-9!@#$%*.]{6,}$/;
  const passwordVal = password.value.trim();
  if (passwordVal && !pwdReg.test(passwordVal)) return true;
  // 两次密码一致性
  if (passwordVal !== confirmPassword.value.trim()) return true;
  return false;
}

/**
 * 带提示版表单校验（返回布尔值+错误提示）
 * @description 注册按钮点击时触发，校验失败显示对应错误提示，返回校验结果
 * @returns {boolean} 校验结果（true=校验通过，false=校验失败）
 */
const validateForm = () => {
  // 用户名格式校验
  if (!/^[a-zA-Z0-9]{3,20}$/.test(username.value.trim())) {
    errorMessage.value = '用户名必须是3-20位数字或字母'
    return false
  }
  // 邮箱格式校验
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
    errorMessage.value = '请输入合法的电子邮箱'
    return false
  }
  // 密码格式校验
  const pwdReg = /^[a-zA-Z0-9!@#$%*.]{6,}$/; 
  const passwordVal = password.value.trim();
  if (passwordVal && !pwdReg.test(passwordVal)) {
    errorMessage.value = '密码只能包含数字、字母和!@#$%*.，且至少6位';
    return false;
  }
  // 两次密码一致性校验
  if (passwordVal !== confirmPassword.value.trim()) {
    errorMessage.value = '两次密码输入不一致，请重新输入'
    return false
  }
  return true
}

/**
 * 启动注册成功自动跳转倒计时
 * @description 注册成功后调用，5秒倒计时结束自动跳转登录页，支持清除旧定时器防止内存泄漏
 * @returns {void}
 */
const startCountdown = () => {
  countdown.value = 5 // 重置倒计时为5秒
  if (countdownTimer) clearInterval(countdownTimer) // 清除旧定时器，避免叠加
  // 每秒递减倒计时，<=0时清除定时器并跳转登录页
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
      countdownTimer = null
      router.push('/app/login') // 跳转登录页
    }
  }, 1000)
}

/**
 * 处理注册核心逻辑（表单校验→接口请求→结果反馈）
 * @async 异步方法（调用注册接口）
 * @description 1. 清空前置状态（错误/成功提示、震动、倒计时） 2. 前端表单校验，失败则触发震动 3. 校验通过发送注册请求 4. 成功则显示提示+启动倒计时 5. 失败则区分错误类型显示提示+触发震动 6. 最终结束加载状态
 * @returns {Promise<void>}
 */
const handleRegister = async () => {
  // 清空前置状态（错误提示、震动、倒计时）
  clearShakeAndCountdown()
  
  // 前端表单校验失败：触发震动动画并返回
  if (!validateForm()) {
    triggerCardShake()
    return
  }

  // 置为加载状态，禁用按钮
  isLoading.value = true
  try {
    // 发送注册接口请求（传递去空格后的表单数据）
    const userInfo = await request.post('/users/register', {
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value.trim()
    })
    console.log('注册成功，后端返回用户信息：', userInfo)
    // 注册成功：显示提示文案+启动自动跳转倒计时
    successMessage.value = '注册成功！将自动跳转到登录界面'
    startCountdown()

  } catch (error) {
    console.error('注册失败：', error)
    // 区分错误类型显示对应提示
    if (error.response) {
      // 后端返回错误（如用户名/邮箱已存在）
      errorMessage.value = '注册失败，请确保邮箱或用户名未被使用'
    } else if (error.request) {
      // 网络异常（无响应）
      errorMessage.value = '网络异常，请检查你的网络连接'
    } else {
      // 其他未知错误
      errorMessage.value = '注册过程中发生未知错误，请重试'
    }
    // 等待DOM更新后触发震动动画（保证动画生效）
    await nextTick()
    triggerCardShake()
  } finally {
    // 无论成功/失败，结束加载状态，启用按钮
    isLoading.value = false
  }
}

/**
 * 组件卸载生命周期：清除定时器防止内存泄漏
 * @description 组件销毁时清除倒计时定时器，避免定时器持续运行导致内存泄漏
 * @returns {void}
 */
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
/* 
 * 注册页样式总说明：
 * 1. 设计原则：简洁易用+视觉统一（绿色主题）+ 交互反馈（hover/震动/焦点）+ 响应式适配 + 内存泄漏防护
 * 2. 视觉风格：浅灰背景+白色卡片+绿色渐变，符合注册页友好、安全的设计调性
 * 3. 交互体验：卡片hover上浮、输入框focus高亮、密码图标hover变色、注册失败震动、按钮hover/active反馈
 * 4. 兼容性：隐藏浏览器原生密码图标、适配移动端/PC端、多字体兼容保证跨系统显示
 * 5. 层级关系：标题>表单>按钮>辅助链接，通过字号/颜色/间距区分，提示文本弱化显示
 */

/* 注册页根容器：最小高度100vh（占满屏幕）+ 弹性布局居中 + 浅灰背景 + 内边距适配小屏 + 多字体兼容 */
.auth-container {
  min-height: 100vh;
  padding: 2rem 1rem;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; /* 跨系统字体兼容 */
}

/* 注册卡片：最大宽度限制+白色背景+圆角+阴影+hover上浮动画，核心交互容器 */
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

/* 卡片震动动画：注册/校验失败触发，左右小幅度晃动，增强错误反馈（时长500ms匹配JS定时器） */
.card-shake {
  animation: card-shake 0.5s ease;
}
/* 震动动画关键帧：0/100%初始位置，20/60%左移，40/80%右移，模拟震动效果 */
@keyframes card-shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-3px); }
  40%, 80% { transform: translateX(3px); }
}

/* 注册标题：居中+大号字体+深灰色+字重，突出核心标题 */
.auth-title {
  font-size: 2rem;
  color: #2d3748; /* 深灰色，保证可读性 */
  margin: 0 0 1.2rem 0;
  font-weight: 600;
  text-align: center;
}

/* 标题分隔线：居中+窄宽度+绿色渐变背景，视觉分割标题与表单，匹配注册页主题色 */
.auth-divider {
  height: 2px;
  width: 70px; /* 短横线，避免视觉占比过大 */
  border-radius: 1px;
  margin: 0 auto 2.5rem; /* 水平居中，底部间距分隔表单 */
}

/* 密码框包裹容器：相对定位，为密码显隐图标提供绝对定位参考 */
.input-wrapper {
  position: relative;
  width: 100%;
}

/* 密码项专属样式：统一底部间距，区分普通表单项 */
.password-item {
  margin-bottom: 1.8rem;
}

/* 密码显示/隐藏图标：绝对定位右侧+垂直居中+hover主题色，交互友好，匹配绿色主题 */
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
/* 密码图标hover：绿色主题色，强化交互反馈 */
.password-toggle-icon:hover {
  color: #2ecc71;
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

/* 表单输入框：宽度100%+内边距+右侧留图标空间+focus高亮，提升输入体验 */
.form-input {
  width: 100%;
  padding: 1rem 1.2rem;
  padding-right: 48px; /* 右侧预留48px空间，避免文字被密码图标遮挡 */
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
/* 输入框focus状态：清除默认轮廓+绿色主题边框+轻微阴影，强化焦点，匹配注册页主题 */
.form-input:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1); /* 外发光，不突兀 */
  background-color: #ffffff; /* 聚焦时白色背景，提升输入清晰度 */
}

/* 表单提示文本：小号+浅灰色，弱化显示，引导用户符合输入格式 */
.form-hint {
  margin-top: 0.3rem;
  font-size: 0.85rem;
  color: #718096;
  margin-bottom: 0;
}

/* 注册按钮：宽度100%+大内边距+圆角+绿色渐变背景+hover/禁用态，突出核心操作 */
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

/* 登录链接：居中+浅灰色+底部间距，作为辅助操作引导 */
.auth-link {
  text-align: center;
  margin-top: 1.8rem;
  color: #7f8c8d; /* 浅灰色，弱化辅助文字 */
  font-size: 1rem;
}
/* 登录链接跳转样式：蓝色+无下划线+hover变色/下划线，引导点击（复用登录页主题色，保持统一） */
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

/* 成功提示：左绿边框+浅绿背景+居中+内边距，突出成功反馈，匹配注册主题色 */
.success-message {
  color: #27ae60 !important; /* 绿色成功色，强制覆盖继承样式 */
  font-size: 0.95rem;
  text-align: center;
  margin-top: 1.2rem;
  padding: 0.8rem;
  background: rgba(39, 174, 96, 0.05) !important; /* 浅绿背景，弱化视觉冲击 */
  border-radius: 4px;
  border-left: 3px solid #27ae60 !important; /* 左侧绿条，强化成功反馈 */
  font-weight: 500; /* 字重提升，突出成功提示 */
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
    padding: 2.5rem 1rem; /* 减少内边距，适配小屏高度 */
  }
  .form-input {
    padding: 0.9rem 1rem; /* 减少输入框内边距，节省空间 */
    padding-right: 48px; /* 保留右侧空间，避免图标遮挡密码 */
  }
}
</style>
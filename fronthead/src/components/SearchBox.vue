<template>
  <!-- 搜索组件核心容器：承载输入区、策略下拉面板、状态提示，支持自定义样式类 -->
  <div class="search-container" :class="customClass">
    <!-- 搜索输入组合区：输入框 + 策略切换按钮 + 搜索按钮，支持回车触发搜索 -->
    <div class="search-input-group">
      <input 
        type="text" 
        v-model="searchQuery"
        :placeholder="placeholder"
        @keyup.enter="handleSearch"
        class="search-input"
      >
      <!-- 搜索策略切换按钮：控制下拉面板显隐，展示当前选中策略 -->
      <button 
        @click="toggleStrategyDropdown" 
        class="strategy-btn"
        :class="{ 'active': showStrategyDropdown }"
      >
        <span>{{ selectedStrategy.label }}</span>
        <span class="triangle" :class="{ 'rotated': showStrategyDropdown }">▼</span>
      </button>
      <!-- 搜索按钮：支持插槽自定义内容，点击触发搜索逻辑 -->
      <button @click="handleSearch" class="search-btn">
        <slot name="search-btn">搜索</slot>
      </button>
    </div>

    <!-- 搜索策略下拉面板：按作者/文章维度分类展示策略，带过渡动画 -->
    <transition name="dropdown">
      <div class="strategy-dropdown" v-if="showStrategyDropdown">
        <!-- 作者维度搜索策略组：可通过props控制是否显示 -->
        <template v-if="showAuthorStrategies">
          <div class="strategy-group">
            <h4>搜索作者</h4>
            <div class="strategy-options">
              <div 
                class="strategy-option"
                v-for="strategy in authorStrategies" 
                :key="strategy.value"
                @click="selectStrategy(strategy)"
              >
                {{ strategy.label }}
              </div>
            </div>
          </div>
        </template>
        
        <!-- 文章维度搜索策略组：可通过props控制是否显示 -->
        <template v-if="showArticleStrategies">
          <div class="strategy-group">
            <h4>搜索文章</h4>
            <div class="strategy-options">
              <div 
                class="strategy-option"
                v-for="strategy in articleStrategies" 
                :key="strategy.value"
                @click="selectStrategy(strategy)"
              >
                {{ strategy.label }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </transition>

    <!-- 状态提示区：加载中/错误提示，分别配置过渡动画 -->
    <div class="loading" v-if="isLoading">搜索中...</div>
    <transition name="fade">
      <div class="search-error" v-if="errorMessage">{{ errorMessage }}</div>
    </transition>
  </div>
</template>

<script setup>
/**
 * 多功能搜索组件
 * @description 支持多维度（作者/文章）搜索策略选择，带参数校验、状态提示、过渡动画的通用搜索组件
 * @feature 1. 支持作者/文章双维度搜索策略 2. 参数校验（关键词/策略） 3. 加载/错误状态提示 4. 过渡动画提升体验 5. 自定义样式/占位符/初始值
 * @props {string} placeholder - 输入框占位符，默认"请输入搜索关键词..."
 * @props {boolean} showAuthorStrategies - 是否显示作者维度策略，默认true
 * @props {boolean} showArticleStrategies - 是否显示文章维度策略，默认true
 * @props {string} customClass - 容器自定义样式类名，默认空
 * @props {string} initialQuery - 初始搜索关键词，默认空
 * @props {Object} initialStrategy - 初始选中的搜索策略，默认空对象
 * @slot search-btn - 搜索按钮自定义内容，默认显示"搜索"
 * @dependencies vue-router - 用于跳转搜索结果页
 */
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

// 组件Props定义：配置组件可定制化参数
const props = defineProps({
  placeholder: { type: String, default: '请输入搜索关键词...' },
  showAuthorStrategies: { type: Boolean, default: true }, // 是否显示作者维度策略
  showArticleStrategies: { type: Boolean, default: true }, // 是否显示文章维度策略
  customClass: { type: String, default: '' }, // 自定义容器类名
  initialQuery: { type: String, default: '' }, // 初始搜索关键词
  initialStrategy: { type: Object } // 初始选中的搜索策略
})

/** @type {import('vue-router').Router} 路由 */
const router = useRouter()
/** @type {Ref<string>} 搜索关键词，默认取initialQuery */
const searchQuery = ref(props.initialQuery)
/** @type {Ref<boolean>} 策略下拉面板显隐状态，默认false */
const showStrategyDropdown = ref(false)
/** @type {Ref<boolean>} 搜索加载状态，默认false */
const isLoading = ref(false)
/** @type {Ref<string>} 错误提示文本，默认空 */
const errorMessage = ref('')
/** @type {Ref<Object>} 选中的搜索策略，默认"选择搜索类型" */
const selectedStrategy = ref(props.initialStrategy || { label: '选择搜索类型', value: '' })

/** @type {Ref<Array<Object>>} 作者维度搜索策略列表 */
const authorStrategies = ref([
  { label: '作者ID', value: 'authors/id' },
  { label: '作者邮箱', value: 'authors/email' },
  { label: '作者名称', value: 'authors/name' }
])

/** @type {Ref<Array<Object>>} 文章维度搜索策略列表 */
const articleStrategies = ref([
  { label: '文章ID', value: 'articles/id' },
  { label: '文章作者', value: 'articles/author' },
  { label: '文章标题', value: 'articles/title' },
  { label: '文章内容', value: 'articles/content' }
])

/**
 * 切换搜索策略下拉面板显隐状态
 * @description 点击策略按钮时触发，切换面板显示/隐藏
 * @returns {void}
 */
const toggleStrategyDropdown = () => {
  showStrategyDropdown.value = !showStrategyDropdown.value
}

/**
 * 选中搜索策略并关闭下拉面板
 * @param {Object} strategy - 选中的策略对象 {label: string, value: string}
 * @description 保存选中策略，关闭下拉面板，清空错误提示
 * @returns {void}
 */
const selectStrategy = (strategy) => {
  selectedStrategy.value = strategy
  showStrategyDropdown.value = false
  errorMessage.value = ''
}

/**
 * 处理搜索核心逻辑
 * @description 校验关键词/策略 → 跳转搜索结果页 → 处理加载/错误状态
 * @returns {void}
 */
const handleSearch = () => {
  errorMessage.value = ''

  // 关键词校验：非空检查
  if (!searchQuery.value.trim()) {
    errorMessage.value = '请输入搜索关键词'
    return
  }
  // 策略校验：必须选择有效策略
  if (!selectedStrategy.value.value) {
    errorMessage.value = '请选择搜索类型'
    return
  }

  isLoading.value = true
  // 跳转搜索结果页，携带关键词和策略参数
  router.push({
    name: 'search-results',
    query: {
      q: searchQuery.value.trim(),
      s: JSON.stringify(selectedStrategy.value)
    }
  }).then(() => {
    isLoading.value = false
    errorMessage.value = ''
  }).catch(() => {
    isLoading.value = false
  })
}

/**
 * 监听初始查询参数变化
 * @description 同步initialQuery到搜索框，立即执行一次
 */
watch(() => props.initialQuery, (newVal) => {
  searchQuery.value = newVal
}, { immediate: true })

/**
 * 监听初始策略参数变化
 * @description 同步initialStrategy到选中状态，立即执行一次
 */
watch(() => props.initialStrategy, (newVal) => {
  if (newVal) selectedStrategy.value = newVal
}, { immediate: true })

/**
 * 监听搜索关键词变化
 * @description 清除空关键词对应的错误提示，提升用户体验
 */
watch(searchQuery, (newVal) => {
  if (newVal.trim() && errorMessage.value === '请输入搜索关键词') {
    errorMessage.value = '';
  }
});

/**
 * 监听选中策略变化
 * @description 清除未选策略对应的错误提示，提升用户体验
 */
watch(selectedStrategy, (newVal) => {
  if (newVal.value && errorMessage.value === '请选择搜索类型') {
    errorMessage.value = '';
  }
});
</script>

<style scoped>
/* 
 * 搜索组件样式总说明：
 * 1. 采用Flex布局实现输入区元素自适应排列，支持响应式
 * 2. 下拉面板/错误提示添加过渡动画，提升交互体验
 * 3. 交互元素（按钮/策略选项）添加hover/active反馈
 * 4. 核心优先级：交互体验 > 视觉样式 > 细节适配
 */

/* 搜索组件容器：相对定位，宽度铺满父容器，作为下拉面板定位基准 */
.search-container {
  position: relative; /* 相对定位，作为子元素绝对定位的基准 */
  width: 100%; /* 宽度铺满父容器 */
}

/* 搜索输入组：Flex布局，元素间距4px，实现输入框自适应宽度 */
.search-input-group {
  display: flex; /* Flex布局排列输入框/按钮 */
  gap: 4px; /* 子元素间距，避免挤压 */
}

/* 搜索输入框：自适应宽度，焦点高亮边框，优化输入体验 */
.search-input {
  flex: 1; /* 占满剩余宽度 */
  padding: 8px 12px; /* 内边距，提升输入舒适度 */
  border: 1px solid #e2e8f0; /* 浅边框，统一视觉风格 */
  border-radius: 4px; /* 圆角，弱化直角 */
  font-size: 14px; /* 字体大小适配 */
  transition: border-color 0.2s; /* 边框颜色过渡动画 */
}

.search-input:focus {
  outline: none; /* 清除默认焦点轮廓 */
  border-color: #3498db; /* 焦点时边框变主题色，强化反馈 */
}

/* 策略选择按钮：hover/active状态样式，Flex布局对齐文字和三角 */
.strategy-btn {
  padding: 0 12px; /* 水平内边距 */
  background-color: #f7fafc; /* 浅灰背景，区分按钮 */
  border: 1px solid #e2e8f0; /* 统一边框风格 */
  border-radius: 4px; /* 圆角 */
  cursor: pointer; /* 鼠标手型，提示可点击 */
  white-space: nowrap; /* 禁止文字换行，防止按钮变形 */
  display: inline-flex; /* Flex布局对齐文字和三角图标 */
  align-items: center; /* 垂直居中 */
  gap: 6px; /* 文字和三角间距 */
  transition: all 0.2s ease; /* 所有属性过渡动画 */
}

.strategy-btn:hover {
  background-color: #edf2f7; /* hover背景色加深，强化反馈 */
  border-color: #cbd5e1; /* hover边框色加深 */
}

.strategy-btn.active {
  background-color: #e2e8f0; /* 激活态背景色，区分面板展开状态 */
}

/* 下拉三角图标：旋转过渡动画，提示面板展开/收起状态 */
.triangle {
  display: inline-block; /* 行内块，支持旋转动画 */
  transition: transform 0.3s ease; /* 旋转过渡动画 */
}

.triangle.rotated {
  transform: rotate(180deg); /* 旋转180度，标识面板展开 */
}

/* 搜索按钮：主题色背景，hover/active交互反馈，提升点击体验 */
.search-btn {
  padding: 0 16px; /* 水平内边距，扩大点击热区 */
  background-color: #3498db; /* 主题色背景 */
  color: white; /* 白色文字，对比鲜明 */
  border: none; /* 清除默认边框 */
  border-radius: 4px; /* 圆角 */
  cursor: pointer; /* 鼠标手型 */
  transition: all 0.2s ease; /* 过渡动画 */
}

.search-btn:hover {
  background-color: #2563eb; /* hover背景色加深 */
  transform: translateY(-1px); /* 轻微上移，灵动效果 */
}

.search-btn:active {
  transform: translateY(0); /* 点击时回归原位，强化按压反馈 */
}

/* 下拉面板过渡动画：透明度+位移+高度，实现顺滑展开/收起 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease; /* 所有属性过渡动画 */
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0; /* 初始/结束透明度0 */
  transform: translateY(-10px); /* 初始/结束向上位移10px */
  max-height: 0; /* 初始/结束高度0 */
  overflow: hidden; /* 隐藏溢出内容 */
}

/* 策略下拉面板：绝对定位，悬浮层，阴影提升层级，宽度继承父容器 */
.strategy-dropdown {
  position: absolute; /* 绝对定位，基于容器定位 */
  top: 100%; /* 位于输入组下方 */
  left: 0; /* 靠左对齐 */
  right: 0; /* 靠右对齐，宽度继承 */
  margin-top: 4px; /* 与输入组间距4px */
  padding: 12px; /* 内边距 */
  background: white; /* 白色背景 */
  border-radius: 4px; /* 圆角 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.1); /* 阴影，提升层级 */
  z-index: 100; /* 高z-index，确保在最上层 */
}

/* 策略分组：底部间距，最后一组无间距，区分不同维度策略 */
.strategy-group {
  margin-bottom: 12px; /* 分组底部间距 */
}

.strategy-group:last-child {
  margin-bottom: 0; /* 最后一组清除间距 */
}

.strategy-group h4 {
  margin: 0 0 8px 0; /* 清除默认边距，仅保留底部间距 */
  font-size: 14px; /* 字体大小 */
  color: #4a5568; /* 文字颜色，区分标题和选项 */
}

/* 策略选项：弹性换行，hover/active交互反馈，适配多选项排列 */
.strategy-options {
  display: flex; /* Flex布局排列选项 */
  flex-wrap: wrap; /* 自动换行，适配多选项 */
  gap: 8px; /* 选项间距 */
}

.strategy-option {
  padding: 4px 12px; /* 内边距，扩大点击热区 */
  background-color: #f7fafc; /* 浅灰背景 */
  border-radius: 4px; /* 圆角 */
  cursor: pointer; /* 鼠标手型 */
  font-size: 13px; /* 字体大小适配 */
  transition: all 0.2s ease; /* 过渡动画 */
}

.strategy-option:hover {
  background-color: #3498db; /* hover背景色变主题色 */
  color: white; /* hover文字变白色 */
  transform: translateY(-1px); /* 轻微上移 */
}

.strategy-option:active {
  transform: translateY(0); /* 点击时回归原位 */
}

/* 加载提示样式：浅灰色文字，与输入组间距8px */
.loading {
  margin-top: 8px; /* 与输入组间距 */
  font-size: 13px; /* 字体大小 */
  color: #64748b; /* 浅灰色文字，弱化视觉权重 */
}

/* 错误提示过渡动画：仅透明度，实现顺滑显隐 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease; /* 透明度过渡动画 */
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* 初始/结束透明度0 */
}

/* 错误提示样式：红色文字，与输入组间距8px，强化错误提示 */
.search-error {
  margin-top: 8px; /* 与输入组间距 */
  font-size: 13px; /* 字体大小 */
  color: #e74c3c; /* 红色文字，强化错误提示 */
}
</style>
<template>
  <!-- 文章更新页面容器：集成侧边栏、标题编辑、Markdown编辑器、更新/保存/预览功能，移除导入功能，适配文章编辑场景 -->
  <div class="article-create">
    <SidebarDrawerUser />
    
    <!-- 头部容器：相对定位，包含返回个人主页按钮（右上角）和文章标题输入区，避免元素重叠 -->
    <div class="header-container">
      <!-- 返回个人主页按钮：绝对定位右上角，hover深色反馈，点击跳转个人主页 -->
      <button class="back-home-btn" @click="goToUserHome">返回个人主页</button>
      
      <!-- 标题输入区：顶部内边距避免与返回按钮重叠，绑定文章标题（最大长度50字） -->
      <div class="title-input-wrapper">
        <div class="title-with-category">
          <label class="title-label">文章标题</label>
          <span class="category-tag">| 分类：{{ categoryName || '未分类' }}</span>
        </div>
        <input
          v-model="title"
          type="text"
          class="title-input"
          placeholder="请输入文章标题（不超过50个字）"
          maxlength="50"
        />
      </div>
    </div>

    <!-- Markdown编辑器区域：自适应高度，仅编辑模式（隐藏预览工具栏），绑定文章内容 -->
    <div class="editor-container">
      <MdEditor
        v-model="content"
        class="markdown-editor"
        placeholder="请使用Markdown格式编写文章内容..."
        theme="light"
        :editorMode="editMode"
        :preview="false"
        :previewOnly="false"
        :previewTheme="null"
        :toolbarsExclude="['preview']"
        :showCodeRowNumber="false"
      />
    </div>

    <!-- 功能按钮区：Flex布局，移除导入按钮，保留更新/保存/预览功能，各按钮hover颜色加深反馈 -->
    <div class="btn-group">
      <button class="submit-btn" @click="updateArticle">更新文章</button>
      <button class="save-btn" @click="saveToLocal">保存为Markdown文件</button>
      <button class="preview-btn" @click="isPreviewShow = !isPreviewShow">
        {{ isPreviewShow ? '关闭预览' : '预览效果' }}
      </button>
      <button class="add-category-btn" @click="isCategoryDialogShow = true">
        添加分类
      </button>
    </div>

    <!-- 自定义悬浮预览框：双向绑定显示状态，传递编辑中的Markdown内容，支持自定义位置/尺寸 -->
    <PreviewModel
      v-model:visible="isPreviewShow"
      :content="content"
      :default-position="{ top: 100, left: 100 }"
      :default-size="{ width: 600, height: 500 }"
    />

        <!-- 新增：分类弹窗 -->
    <div class="category-dialog" v-if="isCategoryDialogShow">
      <div class="dialog-content">
        <h3>添加文章分类</h3>
        <div class="dialog-form">
          <label>分类ID：</label>
          <input v-model="categoryId" type="text" placeholder="输入分类ID（选填）" />
          <label>分类名称：</label>
          <input v-model="categoryName" type="text" placeholder="输入分类名称（选填）" />
          <p class="tip">提示：至少填写ID或名称其中一项</p>
        </div>
        <div class="dialog-btns">
          <button @click="isCategoryDialogShow = false">取消</button>
          <button @click="submitCategory">确定</button>
        </div>
      </div>
    </div>

    <!-- 新增：成功提示框（自动消失） -->
    <div class="success-toast" v-if="isSuccessToastShow">
      {{ successToastMsg }}
    </div>
  </div>
</template>

<script setup>
/**
 * 文章更新页面组件
 * @description 用于编辑已有文章的核心页面，支持加载原有文章数据、Markdown格式编辑、更新文章到后端、本地保存Markdown文件、预览编辑效果，移除导入功能适配更新场景
 * @feature 1. 从路由参数获取文章ID，加载原有文章标题/内容 2. Markdown编辑器（仅编辑模式） 3. 文章标题长度限制（50字） 4. PUT接口更新文章 5. 本地保存编辑后的Markdown文件 6. 悬浮预览框查看编辑效果 7. 移动端响应式适配 8. 完善的错误处理和边界校验
 * @dependencies 
 *  - md-editor-v3: Markdown编辑器核心组件
 *  - PreviewModel: 自定义悬浮预览组件
 *  - SidebarDrawerUser: 用户版侧边栏抽屉组件
 *  - vue-router: 路由参数获取/跳转（返回个人主页）
 *  - request: 后端接口请求（加载文章详情/更新文章）
 */
// 导入Vue核心API：响应式数据/生命周期
import { ref, onMounted } from 'vue'
// 导入Vue Router：获取路由参数/路由跳转
import { useRoute, useRouter } from 'vue-router'
// 导入后端请求工具：接口调用
import request from '@/utils/request'
// 导入Markdown编辑器组件及样式
import { MdEditor } from 'md-editor-v3'
// 导入自定义预览组件
import PreviewModel from '@/components/PreviewModel.vue'
// 导入用户侧边栏组件
import SidebarDrawerUser from '@/components/SidebarDrawerUser.vue'
import 'md-editor-v3/lib/style.css'

// 初始化路由实例
const route = useRoute() // 当前路由实例（获取文章ID参数）
const router = useRouter() // 路由跳转实例（返回个人主页/错误跳转）

// 响应式数据定义
/** @type {Ref<string>} 文章标题，双向绑定输入框，最大长度50字，初始化从接口加载 */
const title = ref('')
/** @type {Ref<string>} 文章内容，双向绑定Markdown编辑器，初始化从接口加载 */
const content = ref('')
/** @type {Ref<int>} 文章分类ID */
const categoryId = ref('')
/** @type {Ref<string>} 文章分类名字 */
const categoryName = ref('')
/** @type {Ref<string>} 文章分类描述 */
const categoryDescription = ref('')
/** @type {Ref<boolean>} 预览框显示/隐藏状态，双向绑定预览组件 */
const isPreviewShow = ref(false)
/** @type {Ref<string>} Markdown编辑器模式，固定为编辑模式 */
const editMode = ref('edit')
/** @type {Ref<boolean>} 分类弹窗显示/隐藏状态，双向绑定分类弹窗组件 */
const isCategoryDialogShow = ref(false)
/** @type {Ref<boolean>} 成功提示 */
const isSuccessToastShow = ref(false)
/** @type {Ref<string>} 存提示框的文本内容*/
const successToastMsg = ref('')




/**
 * 跳转至个人主页
 * @description 点击返回按钮触发，跳转至/userpage/userhome路由
 * @returns {void}
 */
const goToUserHome = () => {
  router.push('/userpage/userhome')
}

/**
 * 初始化文章数据
 * @description 从路由参数提取文章ID，校验有效性后调用GET接口加载原有文章标题/内容，处理ID无效/接口错误等边界情况
 * @returns {Promise<void>} 异步操作Promise
 */
const initArticleData = async () => {
  try {
    // 从路由参数获取文章ID（路由配置为 /article/revise/:articleId）
    const articleId = route.params.articleId
    
    // 边界处理：文章ID无效时提示并跳转个人主页
    if (!articleId) {
      alert('未找到文章ID，请检查链接！')
      router.push('/userpage/userhome')
      return
    }

    // 请求文章详情接口（GET /articles/{article_id}），获取原有标题和内容
    const res = await request.get(`/articles/${articleId}`)
    if (res) {
      title.value = res.title || '' // 初始化标题（空值处理）
      content.value = res.content || '' // 初始化内容（空值处理）
    }

    if (res.category_id) {
      const res_ = await request.get(`/categories/${res.category_id}`)
      if (res_) {
        categoryName.value = res_.name
        categoryDescription.value = res_.description
      }
    }
  } catch (error) {
    // 错误处理：打印日志+提示用户+跳转个人主页
    console.error('出错：', error)
    router.push('/userpage/userhome')
  }
}

/**
 * 更新文章到后端
 * @description 校验标题/内容非空、文章ID有效后，调用PUT接口更新文章，处理接口错误，更新成功后提示并返回个人主页
 * @returns {Promise<void>} 异步操作Promise
 */
const updateArticle = async () => {
  try {
    // 表单验证：标题非空校验
    if (!title.value.trim()) return alert('请输入文章标题')
    // 表单验证：内容非空校验
    if (!content.value.trim()) return alert('请输入文章内容')

    // 从路由参数获取文章ID（适配路由 /article/revise/:article_id）
    const articleId = route.params.articleId
    // 边界处理：文章ID无效时提示
    if (!articleId) {
      alert('未找到文章ID，无法更新！')
      return
    }

    // 发送PUT请求更新文章（接口：/articles/{article_id}）
    await request.put(`/articles/${articleId}`, {
      title: title.value.trim(), // 去除首尾空格
      content: content.value.trim() // 去除首尾空格
    })

    // 操作成功提示并跳转个人主页
    alert('文章更新成功！')
    router.push('/userpage/userhome')
  } catch (error) {
    // 错误处理：打印日志+提示用户
    console.error('更新文章失败：', error)
    alert('文章更新失败，请重试！')
  }
}

/**
 * 保存编辑后的文章为本地Markdown文件
 * @description 校验内容非空后，生成Blob对象，创建下载链接触发文件保存，支持自定义文件名（优先标题，无则为"未命名文章"）
 * @returns {void}
 */
const saveToLocal = () => {
  // 边界处理：标题和内容均为空时提示
  if (!title.value.trim() && !content.value.trim()) return alert('无内容可保存')
  // 确定文件名（优先标题，无则默认）
  const fileName = title.value.trim() || '未命名文章'
  // 生成Markdown格式Blob（标题为一级标题，内容换行分隔）
  const blob = new Blob([`# ${title.value}\n\n${content.value}`], { type: 'text/markdown' })
  // 创建下载链接
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${fileName}.md` // 设置下载文件名
  a.click() // 触发下载
  URL.revokeObjectURL(a.href) // 释放URL对象，避免内存泄漏
}

/**
 * 生命周期：组件挂载
 * @description 页面首次加载时初始化文章数据，加载原有文章标题和内容到编辑器
 */
onMounted(() => {
  initArticleData()
})

/**
 * 提交分类
 */
const submitCategory = async () => {
  try {
    const articleId = route.params.articleId
    // 校验：文章ID/分类信息是否存在
    if (!articleId) {
      alert('未找到文章ID，无法添加分类！')
      return
    }
    if (!categoryId.value.trim() && !categoryName.value.trim()) {
      alert('请填写分类ID或名称！')
      return
    }

    // 调用对应接口：优先用ID，其次用名称
    let apiUrl = ''
    let categoryTarget = ''
    if (categoryId.value.trim()) {
      apiUrl = `/articles/${articleId}/category/id/${categoryId.value.trim()}`
      categoryTarget = `ID: ${categoryId.value.trim()}`
    } else {
      apiUrl = `/articles/${articleId}/category/name/${categoryName.value.trim()}`
      categoryTarget = `名称: ${categoryName.value.trim()}`
    }

    // 调用PUT接口
    await request.put(apiUrl)
    
    // 成功处理：关闭弹窗+显示提示+重置表单
    isCategoryDialogShow.value = false
    successToastMsg.value = `成功将文章添加至分类${categoryTarget}`
    isSuccessToastShow.value = true
    // 自动隐藏提示（3秒后）
    setTimeout(() => {
      isSuccessToastShow.value = false
    }, 3000)
    // 重置分类表单
    categoryId.value = ''
    categoryName.value = ''
  } catch (error) {
    console.error('添加分类失败：', error)
    alert('添加分类失败，请重试！')
  }
}
</script>

<style scoped>
/* 
 * 文章更新页面样式总说明：
 * 1. 整体Flex垂直布局，自适应高度（最小80vh），统一间距和内边距，适配编辑场景
 * 2. 头部容器相对定位，返回按钮绝对定位右上角，标题输入区顶部内边距避免重叠
 * 3. Markdown编辑器自适应高度，浅边框美化，自定义主题色为蓝色
 * 4. 功能按钮区分不同主题色（更新-蓝/保存-青绿/预览-琥珀），hover颜色加深，支持换行适配小屏
 * 5. 移除导入按钮相关样式，简化功能区
 * 6. 移动端适配：编辑器高度降低、按钮尺寸缩小，保证小屏操作体验
 * 7. 核心优先级：功能可用性 > 交互体验 > 视觉美观 > 响应式兼容
 */

/* 根容器：全屏宽度，最小高度80vh，Flex垂直布局，统一间距/内边距，盒模型包含内边距 */
.article-create {
  width: 100%;
  min-height: 80vh; /* 最小高度80视口高度，保证编辑区域充足 */
  display: flex; /* Flex布局 */
  flex-direction: column; /* 垂直排列子元素 */
  gap: 1.5rem; /* 子元素之间的间距 */
  padding: 1rem; /* 内边距，控制内容与边界的距离 */
  box-sizing: border-box; /* 内边距计入宽度，避免溢出 */
}

/* 头部容器：相对定位，作为返回按钮绝对定位的基准 */
.header-container {
  width: 100%;
  position: relative; /* 相对定位 */
}

/* 返回个人主页按钮：绝对定位右上角，浅灰背景，hover深色反馈，提升点击体验 */
.back-home-btn {
  position: absolute; /* 绝对定位 */
  top: 0; /* 顶部对齐 */
  right: 0; /* 右侧对齐 */
  padding: 0.6rem 1.2rem; /* 内边距，扩大点击热区 */
  background-color: #718096; /* 浅灰背景色 */
  color: white; /* 白色文字 */
  border: none; /* 清除默认边框 */
  border-radius: 8px; /* 圆角，弱化直角 */
  font-size: 0.9rem; /* 字体大小适配 */
  cursor: pointer; /* 鼠标手型，提示可点击 */
  transition: background-color 0.2s ease; /* 背景色过渡动画，交互更丝滑 */
}
.back-home-btn:hover {
  background-color: #4a5568; /* hover时背景色加深，强化反馈 */
}

/* 标题输入区：顶部内边距避免与返回按钮重叠，宽度100% */
.title-input-wrapper {
  width: 100%;
  padding-top: 1rem; /* 顶部内边距，避免与返回按钮重叠 */
}

/* 标题标签：块级显示，加粗，深灰色，底部间距，突出标签层级 */
.title-label {
  display: block; /* 块级显示，独占一行 */
  font-size: 1.1rem; /* 字体微放大，突出标签 */
  color: #2d3748; /* 深灰色，提升可读性 */
  font-weight: 600; /* 字体加粗，强化标签 */
  margin-bottom: 0.8rem; /* 底部间距，与输入框区分 */
}

/* 标题输入框：宽度100%，浅边框，圆角，focus时主题色边框+阴影，提升输入体验 */
.title-input {
  width: 100%; /* 宽度100% */
  padding: 0.8rem 1rem; /* 内边距，提升输入体验 */
  border: 1px solid #e2e8f0; /* 浅灰色边框，美化 */
  border-radius: 8px; /* 圆角，现代感 */
  font-size: 1rem; /* 字体大小适配 */
  box-sizing: border-box; /* 内边距计入宽度 */
  transition: border-color 0.2s ease; /* 边框色过渡动画 */
}
.title-input:focus {
  outline: none; /* 清除默认focus轮廓 */
  border-color: #4299e1; /* focus时主题色边框 */
  box-shadow: 0 0 0 2px rgba(66, 153, 225, 0.2); /* focus时轻微阴影，强化焦点 */
}

/* 编辑器容器：自适应高度，最小高度500px，浅边框，圆角，隐藏溢出，保证编辑器完整性 */
.editor-container {
  flex: 1; /* 占满剩余高度 */
  min-height: 500px; /* 最小高度，保证编辑器可用区域 */
  border: 1px solid #e2e8f0; /* 浅灰色边框，美化 */
  border-radius: 8px; /* 圆角，现代感 */
  overflow: hidden; /* 隐藏溢出，避免编辑器内容超出容器 */
}

/* Markdown编辑器：强制宽高100%，覆盖组件默认样式，自定义主题色为蓝色 */
.markdown-editor {
  width: 100% !important; /* 强制宽度100%，覆盖组件默认样式 */
  height: 100% !important; /* 强制高度100%，覆盖组件默认样式 */
  --md-color-primary: #4299e1; /* 自定义编辑器主题色为蓝色 */
}

/* 功能按钮区：Flex布局，支持换行，统一间距，适配不同屏幕宽度 */
.btn-group {
  display: flex; /* Flex布局 */
  gap: 1rem; /* 按钮之间的间距 */
  align-items: center; /* 垂直居中 */
  flex-wrap: wrap; /* 自动换行，适配小屏 */
}

/* 更新按钮：蓝色背景（主操作色），hover加深，突出更新核心功能 */
.submit-btn {
  padding: 0.8rem 1.5rem; /* 内边距，扩大点击热区 */
  background: #4299e1; /* 蓝色背景，主操作色 */
  color: white; /* 白色文字 */
  border: none; /* 清除默认边框 */
  border-radius: 8px; /* 圆角 */
  font-size: 1rem; /* 字体大小 */
  cursor: pointer; /* 鼠标手型 */
  transition: background 0.2s ease; /* 背景色过渡动画 */
}
.submit-btn:hover {
  background: #3182ce; /* hover时背景色加深 */
}
/* 添加分类按钮：固定右下角，浅灰背景，hover深色 */
.add-category-btn {
  position: fixed;
  right: 2rem;
  padding: 0.8rem 1.5rem;
  background: #718096;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
.add-category-btn:hover {
  background: #4a5568;
}

/* 保存按钮：青绿色背景（次要操作色），hover加深，区分保存功能 */
.save-btn {
  padding: 0.8rem 1.5rem; /* 内边距 */
  background: #38b2ac; /* 青绿色背景，次要操作色 */
  color: white; /* 白色文字 */
  border: none; /* 清除默认边框 */
  border-radius: 8px; /* 圆角 */
  font-size: 1rem; /* 字体大小 */
  cursor: pointer; /* 鼠标手型 */
  transition: background 0.2s ease; /* 背景色过渡动画 */
}
.save-btn:hover {
  background: #319795; /* hover时背景色加深 */
}

/* 预览按钮：琥珀色背景（次要操作色），hover加深，区分预览功能 */
.preview-btn {
  padding: 0.8rem 1.5rem; /* 内边距 */
  background: #f59e0b; /* 琥珀色背景，次要操作色 */
  color: white; /* 白色文字 */
  border: none; /* 清除默认边框 */
  border-radius: 8px; /* 圆角 */
  font-size: 1rem; /* 字体大小 */
  cursor: pointer; /* 鼠标手型 */
  transition: background 0.2s ease; /* 背景色过渡动画 */
}
.preview-btn:hover {
  background: #d97706; /* hover时背景色加深 */
}

/* 原生文件输入框：隐藏（已移除导入功能，保留样式避免冲突） */
.file-input {
  display: none; /* 隐藏原生输入框 */
}

/* 响应式适配：平板/手机端（≤768px） */
@media (max-width: 768px) {
  .editor-container {
    min-height: 400px; /* 编辑器最小高度降低，适配小屏 */
  }
  .back-home-btn {
    padding: 0.5rem 1rem; /* 返回按钮内边距缩小 */
    font-size: 0.8rem; /* 字体缩小 */
  }
}

/* 分类弹窗：遮罩层+居中内容 */
.category-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.dialog-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
}
.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
}
.dialog-form input {
  padding: 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}
.tip {
  color: #718096;
  font-size: 0.8rem;
  margin: 0;
}
.dialog-btns {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
.dialog-btns button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.dialog-btns button:first-child {
  background: #e2e8f0;
}
.dialog-btns button:last-child {
  background: #4299e1;
  color: white;
}

/* 成功提示框：固定底部，绿色背景，自动消失 */
.success-toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.8rem 1.5rem;
  background: #38b2ac;
  color: white;
  border-radius: 8px;
  z-index: 101;
}

/* 标题+分类组合容器：横向排列，对齐居中 */
.title-with-category {
  display: flex;
  align-items: center;
  gap: 0.8rem; /* 标题和分类之间的间距 */
  margin-bottom: 0.8rem; /* 保持和原label一致的底部间距 */
}

/* 分类标签样式：主题色，字体和标题标签匹配 */
.category-tag {
  font-size: 1rem;
  color: #0487f3; /* 和编辑器主题色一致，视觉统一 */
  font-weight: 500;
  margin-bottom: 0.8rem;
}
</style>
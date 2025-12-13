<template>
  <!-- 文章创建页面容器：集成侧边栏、标题输入、Markdown编辑器、功能按钮、预览组件，支持提交/导入/导出/预览功能 -->
  <div class="article-create">
    <SidebarDrawerUser />
    
    <!-- 头部容器：包含返回个人主页按钮 + 文章标题输入区，相对定位避免元素重叠 -->
    <div class="header-container">
      <!-- 返回个人主页按钮：绝对定位在右上角，hover深色反馈 -->
      <button class="back-home-btn" @click="goToUserHome">返回个人主页</button>
      
      <!-- 标题输入区：顶部内边距避免与返回按钮重叠 -->
      <div class="title-input-wrapper">
        <label class="title-label">文章标题</label>
        <input
          v-model="title"
          type="text"
          class="title-input"
          placeholder="请输入文章标题（不超过50个字）"
          maxlength="50"
        />
      </div>
    </div>

    <!-- Markdown编辑器区域：自适应高度，浅边框美化，隐藏预览功能仅保留编辑模式 -->
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

    <!-- 功能按钮区：Flex布局，支持提交、保存、导入、预览功能，hover颜色加深反馈 -->
    <div class="btn-group">
      <button class="submit-btn" @click="submitArticle">提交文章</button>
      <button class="save-btn" @click="saveToLocal">保存为Markdown文件</button>
      <label class="import-btn">
        导入Markdown文件
        <input
          type="file"
          accept=".md,.markdown"
          class="file-input"
          @change="importFromLocal"
        />
      </label>
      <button class="preview-btn" @click="isPreviewShow = !isPreviewShow">
        {{ isPreviewShow ? '关闭预览' : '预览效果' }}
      </button>
    </div>

    <!-- 自定义悬浮预览框：双向绑定显示状态，传递Markdown内容，支持自定义位置/尺寸 -->
    <PreviewModel
      v-model:visible="isPreviewShow"
      :content="content"
      :default-position="{ top: 100, left: 100 }"
      :default-size="{ width: 600, height: 500 }"
    />
  </div>
</template>

<script setup>
/**
 * 文章创建页面组件
 * @description 支持Markdown格式文章创建的核心页面，集成标题输入、编辑器、提交/导入/导出/预览功能，适配移动端响应式
 * @feature 1. Markdown编辑器（仅编辑模式，隐藏预览工具栏） 2. 文章标题长度限制（50字） 3. 提交文章到后端接口 4. 本地保存/导入Markdown文件 5. 悬浮预览框查看效果 6. 返回个人主页快捷按钮 7. 移动端适配（编辑器高度/按钮尺寸调整）
 * @dependencies 
 *  - md-editor-v3: Markdown编辑器核心组件
 *  - PreviewModel: 自定义悬浮预览组件
 *  - SidebarDrawerUser: 用户版侧边栏抽屉组件
 *  - vue-router: 路由跳转（返回个人主页）
 *  - request: 后端接口请求（提交文章）
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { MdEditor } from 'md-editor-v3'
import PreviewModel from '@/components/PreviewModel.vue'
import SidebarDrawerUser from '@/components/SidebarDrawerUser.vue'
import 'md-editor-v3/lib/style.css'

/** @type {import('vue-router').Router} 路由 */
const router = useRouter()
/** @type {Ref<string>} 文章标题，双向绑定输入框，最大长度50字 */
const title = ref('')
/** @type {Ref<string>} 文章内容，双向绑定Markdown编辑器 */
const content = ref('')
/** @type {Ref<boolean>} 预览框显示/隐藏状态，双向绑定预览组件 */
const isPreviewShow = ref(false)
/** @type {Ref<string>} Markdown编辑器模式，固定为编辑模式 */
const editMode = ref('edit')

/**
 * 跳转至个人主页
 * @description 点击返回按钮触发，跳转至/userpage/userhome路由
 * @returns {void}
 */
const goToUserHome = () => {
  router.push('/userpage/userhome')
}

/**
 * 提交文章到后端
 * @description 校验标题/内容非空后，调用/articles接口提交，提交成功后提示用户
 * @returns {void}
 */
const submitArticle = () => {
  // 标题非空校验
  if (!title.value.trim()) return alert('请输入文章标题')
  // 内容非空校验
  if (!content.value.trim()) return alert('请输入文章内容')
  // 调用后端提交接口
  request.post('/articles', { title: title.value, content: content.value })
  // 提交成功提示
  alert('文章提交成功！')
}

/**
 * 保存文章为本地Markdown文件
 * @description 校验内容非空后，生成Blob对象，创建下载链接触发文件保存，支持自定义文件名（优先标题，无则为"未命名文章"）
 * @returns {void}
 */
const saveToLocal = () => {
  // 内容非空校验
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
 * 从本地导入Markdown文件
 * @description 校验文件类型为.md/.markdown，读取文件内容后解析标题（一级标题行）和内容，双向绑定到编辑器，清空input支持重新选择同一文件
 * @param {Event} e - 文件选择框change事件对象
 * @returns {void}
 */
const importFromLocal = (e) => {
  // 获取选中的文件
  const file = e.target.files[0]
  if (!file) return
  
  // 校验文件类型（仅支持.md/.markdown）
  if (!['.md', '.markdown'].includes(file.name.slice(-3))) {
    return alert('请选择Markdown文件（.md/.markdown）')
  }

  // 创建文件读取器
  const reader = new FileReader()
  // 文件读取完成回调
  reader.onload = (event) => {
    // 按行分割文件内容
    const lines = event.target.result.split('\n')
    // 解析标题（第一行为一级标题时提取）
    if (lines[0].startsWith('# ')) {
      title.value = lines[0].slice(2).trim() // 提取#后的标题文本
      content.value = lines.slice(1).filter(line => line || true).join('\n') // 剩余行作为内容（保留空行）
    } else {
      // 无一级标题时标题置空，内容为完整文件内容
      title.value = ''
      content.value = event.target.result
    }
  }
  // 以UTF-8编码读取文件为文本
  reader.readAsText(file, 'utf-8')
  // 清空input值，支持重新选择同一文件
  e.target.value = ''
}
</script>

<style scoped>
/* 
 * 文章创建页面样式总说明：
 * 1. 整体Flex垂直布局，自适应高度，统一间距和内边距
 * 2. 头部容器相对定位，返回按钮绝对定位右上角，标题输入区顶部内边距避免重叠
 * 3. Markdown编辑器自适应高度，浅边框美化，自定义主题色
 * 4. 功能按钮区分不同主题色，hover颜色加深，支持换行适配小屏
 * 5. 导入按钮隐藏原生文件输入框，自定义样式统一视觉
 * 6. 移动端适配：编辑器高度降低、按钮尺寸缩小
 * 7. 核心优先级：功能可用性 > 交互体验 > 视觉美观 > 响应式兼容
 */

/* 根容器：全屏宽度，最小高度80vh，Flex垂直布局，统一间距/内边距 */
.article-create {
  width: 100%;
  min-height: 80vh; /* 最小高度80视口高度，保证页面完整性 */
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

/* 返回个人主页按钮：绝对定位右上角，浅灰背景，hover深色反馈 */
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

/* 标题标签：块级显示，加粗，深灰色，底部间距 */
.title-label {
  display: block; /* 块级显示，独占一行 */
  font-size: 1.1rem; /* 字体微放大，突出标签 */
  color: #2d3748; /* 深灰色，提升可读性 */
  font-weight: 600; /* 字体加粗，强化标签 */
  margin-bottom: 0.8rem; /* 底部间距，与输入框区分 */
}

/* 标题输入框：宽度100%，浅边框，圆角，focus时主题色边框+阴影 */
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

/* 编辑器容器：自适应高度，最小高度500px，浅边框，圆角，隐藏溢出 */
.editor-container {
  flex: 1; /* 占满剩余高度 */
  min-height: 500px; /* 最小高度，保证编辑器可用区域 */
  border: 1px solid #e2e8f0; /* 浅灰色边框，美化 */
  border-radius: 8px; /* 圆角，现代感 */
  overflow: hidden; /* 隐藏溢出，避免编辑器内容超出容器 */
}

/* Markdown编辑器：强制宽高100%，自定义主题色为蓝色 */
.markdown-editor {
  width: 100% !important; /* 强制宽度100%，覆盖组件默认样式 */
  height: 100% !important; /* 强制高度100%，覆盖组件默认样式 */
  --md-color-primary: #4299e1; /* 自定义编辑器主题色为蓝色 */
}

/* 功能按钮区：Flex布局，支持换行，统一间距 */
.btn-group {
  display: flex; /* Flex布局 */
  gap: 1rem; /* 按钮之间的间距 */
  align-items: center; /* 垂直居中 */
  flex-wrap: wrap; /* 自动换行，适配小屏 */
}

/* 提交按钮：蓝色背景，hover加深 */
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

/* 保存按钮：青绿色背景，hover加深 */
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

/* 导入按钮：紫色背景，hover加深，行内块级适配点击区域 */
.import-btn {
  padding: 0.8rem 1.5rem; /* 内边距 */
  background: #9f7aea; /* 紫色背景，次要操作色 */
  color: white; /* 白色文字 */
  border: none; /* 清除默认边框 */
  border-radius: 8px; /* 圆角 */
  font-size: 1rem; /* 字体大小 */
  cursor: pointer; /* 鼠标手型 */
  transition: background 0.2s ease; /* 背景色过渡动画 */
  display: inline-block; /* 行内块级，适配点击区域 */
}
.import-btn:hover {
  background: #805ad5; /* hover时背景色加深 */
}

/* 预览按钮：琥珀色背景，hover加深 */
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

/* 原生文件输入框：隐藏，仅通过导入按钮触发 */
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
</style>
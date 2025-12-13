<template>
  <div class="message-page">
    <!-- 核心：用 isShowDetail 控制显示“原界面”或“详情组件” -->
    <div v-if="!isShowDetail">
      <!-- 头部按钮区 -->
      <div class="tab-header">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'send' }"
          @click="switchTab('send')"
        >
          发送邮件
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'receive' }"
          @click="switchTab('receive')"
        >
          接收邮件
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'sent' }"
          @click="switchTab('sent')"
        >
          已发送邮件
        </button>
      </div>

      <!-- 提示信息（从Store读取） -->
      <div v-if="messageStore.message" class="message-tip" :class="messageStore.messageType">
        {{ messageStore.message }}
        <span class="close-tip" @click="messageStore.message = ''">×</span>
      </div>

      <!-- 内容区 -->
      <div class="tab-content">
        <!-- 发送邮件界面 -->
        <div v-if="activeTab === 'send'" class="send-panel">
          <div class="form-item">
            <label>收件人邮箱：</label>
            <input 
              type="email" 
              v-model="sendForm.receiver_email" 
              placeholder="请输入收件人邮箱（如admin@163.com）"
              class="form-input"
            >
          </div>
          <div class="form-item">
            <label>邮件内容：</label>
            <textarea 
              v-model="sendForm.content" 
              placeholder="请输入邮件内容"
              class="form-textarea"
              rows="6"
            ></textarea>
          </div>
          <button 
            class="submit-btn" 
            @click="handleSendEmail"
            :disabled="messageStore.loading"
          >
            <span v-if="messageStore.loading">发送中...</span>
            <span v-else>发送邮件</span>
          </button>
        </div>

        <!-- 接收邮件界面 -->
        <div v-if="activeTab === 'receive'" class="list-panel">
          <div class="loading" v-if="messageStore.loading">加载中...</div>
          <div class="empty" v-else-if="messageStore.receiveList.length === 0">
            暂无接收的邮件
          </div>
          <div v-else class="email-list-container">
            <div class="email-list">
              <div 
                class="email-item" 
                v-for="item in (messageStore.receiveExpand ? messageStore.receiveList : messageStore.receiveList.slice(0, 2))" 
                :key="item.id"
                @click="showDetail(item.id, 'receive')"
                style="cursor: pointer;"
              >
                <div class="email-info">
                  <p><span class="label">发件人：</span>{{ item.sender_email }}</p>
                  <p><span class="label">发送时间：</span>{{ formatTime(item.created_at) }}</p>
                  <p><span class="label">已读状态：</span>{{ item.is_read ? '已读' : '未读' }}</p>
                  <p><span class="label">邮件ID：</span>{{ item.id }}</p>
                </div>
              </div>
            </div>
            <button 
              v-if="messageStore.receiveList.length > 2"
              class="expand-btn"
              @click="messageStore.receiveExpand = !messageStore.receiveExpand"
            >
              {{ messageStore.receiveExpand ? '收起' : '展开更多' }}
            </button>
          </div>
        </div>

        <!-- 已发送邮件界面 -->
        <div v-if="activeTab === 'sent'" class="list-panel">
          <div class="loading" v-if="messageStore.loading">加载中...</div>
          <div class="empty" v-else-if="messageStore.sentList.length === 0">
            暂无已发送的邮件
          </div>
          <div v-else class="email-list-container">
            <div class="email-list">
              <div 
                class="email-item" 
                v-for="item in (messageStore.sentExpand ? messageStore.sentList : messageStore.sentList.slice(0, 2))" 
                :key="item.id"
                style="cursor: pointer;"
              >
                <div class="email-info" @click="showDetail(item.id, 'sent')">
                  <p><span class="label">发件人：</span>{{ item.sender_email }}</p>
                  <p><span class="label">发送时间：</span>{{ formatTime(item.created_at) }}</p>
                  <p><span class="label">对方已读：</span>{{ item.is_read ? '已读' : '未读' }}</p>
                  <p><span class="label">邮件ID：</span>{{ item.id }}</p>
                </div>
                <button 
                  class="withdraw-btn"
                  @click.stop="messageStore.withdrawMessage(item.id)"
                  :disabled="messageStore.withdrawLoading[item.id]"
                >
                  <span v-if="messageStore.withdrawLoading[item.id]">撤回中...</span>
                  <span v-else>撤回</span>
                </button>
              </div>
            </div>
            <button 
              v-if="messageStore.sentList.length > 2"
              class="expand-btn"
              @click="messageStore.sentExpand = !messageStore.sentExpand"
            >
              {{ messageStore.sentExpand ? '收起' : '展开更多' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情组件 -->
    <MessageDetailPage 
      v-else
      :messageId="currentMessageId"
      @close="isShowDetail = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/store/message'
import MessageDetailPage from '@/components/MessageDetailPage.vue'

// 引入Store
const messageStore = useMessageStore()

// 本地响应式数据
const activeTab = ref('send')
const isShowDetail = ref(false)
const currentMessageId = ref('')
const sendForm = ref({
  content: '',
  receiver_email: ''
})

// 切换Tab
const switchTab = (tab) => {
  activeTab.value = tab
  // 重置展开状态
  messageStore.receiveExpand = false
  messageStore.sentExpand = false
  // 加载对应列表
  if (tab === 'receive') {
    messageStore.getReceiveEmail()
  } else if (tab === 'sent') {
    messageStore.getSentEmail()
  }
}

// 显示详情 + 前端标记已读
const showDetail = (messageId, type) => {
  currentMessageId.value = messageId
  // 核心：前端立即标记为已读
  messageStore.markAsRead(messageId, type)
  isShowDetail.value = true
}

// 发送邮件
const handleSendEmail = async () => {
  const res = await messageStore.sendEmail(sendForm.value)
  if (res) {
    // 清空表单
    sendForm.value = { content: '', receiver_email: '' }
  }
}

// 格式化时间
const formatTime = (isoTime) => {
  if (!isoTime) return ''
  const date = new Date(isoTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 初始加载
onMounted(() => {
  switchTab('send')
})
</script>

<style scoped>
/* 样式部分完全保留，无需修改 */
.message-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

/* 头部tab按钮 */
.tab-header {
  display: flex;
  gap: 8px;
  padding: 0 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 8px;
}

.tab-btn {
  padding: 8px 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #333;
  font-size: 14px;
}

.tab-btn.active {
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tab-btn:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.4);
}

/* 提示信息 */
.message-tip {
  margin: 0 8px;
  padding: 10px 16px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  font-size: 14px;
}

.message-tip.success {
  background-color: rgba(72, 187, 120, 0.8);
}

.message-tip.error {
  background-color: rgba(220, 38, 38, 0.8);
}

.close-tip {
  cursor: pointer;
  margin-left: 10px;
  font-weight: bold;
}

/* 内容区通用 */
.tab-content {
  flex: 1;
  overflow: auto;
  padding: 0 8px;
}

/* 发送邮件面板 */
.send-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-input, .form-textarea {
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  font-size: 14px;
  color: #333;
}

.form-textarea {
  resize: none;
}

.submit-btn {
  padding: 12px;
  border: none;
  border-radius: 6px;
  background-color: rgba(59, 130, 246, 0.8);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-btn:disabled {
  background-color: rgba(59, 130, 246, 0.4);
  cursor: not-allowed;
}

.submit-btn:hover:not(:disabled) {
  background-color: rgba(59, 130, 246, 1);
}

/* 列表面板通用 */
.list-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading, .empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
  font-size: 14px;
}

.email-list-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.email-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 核心：优化邮件卡片交互效果 */
.email-item {
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 8px; /* 圆角更大更美观 */
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer; /* 明确可点击 */
  /* 过渡动画：所有变化丝滑 */
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  /* 初始轻微阴影 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

/* hover 效果：加深背景、增强阴影、轻微缩放 */
.email-item:hover {
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px); /* 轻微上浮 */
  border-color: rgba(59, 130, 246, 0.2); /* 边框微蓝 */
}

/* 点击按压效果 */
.email-item:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

/* 可选：添加hover时的渐变高光（增强视觉反馈） */
.email-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s ease;
}

.email-item:hover::before {
  left: 100%;
}

.email-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  flex: 1;
  /* 防止文字被按钮遮挡 */
  padding-right: 16px;
}

.label {
  color: #666;
  font-weight: 500;
}

/* 展开/收起按钮样式 */
.expand-btn {
  padding: 0.5rem 1rem;
  background-color: #e2e8f0; /* 浅灰背景，中性色调 */
  border: none;
  border-radius: 6px;
  color: #2d3748;
  cursor: pointer;
  transition: background-color 0.2s ease;
  align-self: flex-start; /* 左对齐，符合阅读习惯 */
  margin-top: 0.5rem;
}
.expand-btn:hover {
  background-color: #cbd5e1; /* 加深灰色，强化hover反馈 */
}

/* 撤回按钮样式：优化交互 */
.withdraw-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background-color: rgba(220, 38, 38, 0.7);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  margin-left: 10px;
  /* 按钮悬浮效果 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.withdraw-btn:disabled {
  background-color: rgba(220, 38, 38, 0.3);
  cursor: not-allowed;
  transform: none;
}

.withdraw-btn:hover:not(:disabled) {
  background-color: rgba(220, 38, 38, 0.9);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.withdraw-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}
</style>
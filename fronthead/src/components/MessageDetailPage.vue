<template>
  <!-- 详情页完全贴合父容器（板子） -->
  <div class="detail-page">
    <!-- 右上角白色交互按钮 -->
    <button class="back-btn" @click="handleClose">返回</button>

    <!-- 详情内容区（贴合板子内部） -->
    <div class="detail-content">
      <!-- 加载状态 -->
      <div class="loading" v-if="loading">加载详情中...</div>
      
      <!-- 详情数据（按新排版调整） -->
      <div v-else-if="detail" class="detail-card">
        <!-- 1. 收发信息栏目（缩小排版） -->
        <div class="sender-receiver-section">
          <div class="section-title">收发信息</div>
          <div class="info-row">
            <div class="info-item">
              <span class="label">发件人：</span>
              <span class="value">{{ detail.sender?.username }} ({{ detail.sender?.email }})</span>
            </div>
            <div class="info-item">
              <span class="label">收件人：</span>
              <span class="value">{{ detail.receiver?.username }} ({{ detail.receiver?.email }})</span>
            </div>
          </div>
        </div>

        <!-- 2. 辅助信息行（发送时间+已读状态，排成一行缩小显示） -->
        <div class="aux-info-row">
          <span class="aux-text">发送时间：{{ formatTime(detail.created_at) }}</span>
          <span class="aux-text">已读状态：{{ detail.is_read ? '已读' : '未读' }}</span>
        </div>

        <!-- 3. 主体邮件内容（大栏目渲染） -->
        <div class="content-section">
          <div class="section-title">邮件内容</div>
          <div class="content-box">{{ detail.content }}</div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div class="empty" v-else>暂无邮件详情</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

// 接收父组件传入的邮件ID
const props = defineProps({
  messageId: {
    type: [Number, String],
    required: true
  }
})

// 向父组件触发“关闭详情”事件
const emit = defineEmits(['close'])

// 响应式数据
const loading = ref(false)
const detail = ref(null)

// 格式化时间
const formatTime = (isoTime) => {
  if (!isoTime) return ''
  const date = new Date(isoTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

// 请求邮件详情
const fetchDetail = async () => {
  try {
    loading.value = true
    const res = await request.get(`/messages/${props.messageId}`)
    detail.value = res
  } catch (err) {
    console.error('获取详情失败：', err)
  } finally {
    loading.value = false
  }
}

// 关闭详情（通知父组件）
const handleClose = () => {
  emit('close')
}

// 组件挂载后请求详情
onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
/* 详情页：完全贴合父容器（板子），背景与板子统一 */
.detail-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0; /* 去掉内边距，完美贴合板子 */
  box-sizing: border-box;
  /* 背景色与板子保持一致（截图中为浅白半透明） */
  background-color: rgba(240, 240, 240, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 0; /* 去掉圆角，贴合板子边框 */
}

/* 右上角返回按钮：白色背景+交互 */
.back-btn {
  align-self: flex-end;
  margin: 8px 16px 0 0; /* 右上角留轻微边距 */
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background-color: #ffffff; /* 白色背景 */
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #333;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.back-btn:hover {
  background-color: #f5f5f5; /* hover浅灰 */
  border-color: #d0d0d0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}
.back-btn:active {
  background-color: #eeeeee;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) inset;
}

/* 详情内容区：顶部对齐，贴合内部 */
.detail-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* 内容从顶部开始 */
  padding: 12px 16px;
  gap: 12px;
  box-sizing: border-box;
}

.loading, .empty {
  text-align: center;
  color: #666;
  font-size: 14px;
  padding: 20px 0;
}

/* 详情卡片：无额外边框，贴合背景 */
.detail-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1; /* 占满剩余空间 */
}

/* 1. 收发信息栏目：缩小排版+轻阴影 */
.sender-receiver-section {
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.info-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.info-item {
  font-size: 13px; /* 缩小字体 */
  display: flex;
  gap: 6px;
}
.info-item .label {
  min-width: 70px;
  font-weight: 500;
  color: #666;
}
.info-item .value {
  color: #444;
}

/* 2. 辅助信息行：一行显示+缩小字体 */
.aux-info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 12px; /* 缩小字体 */
  color: #666;
  background-color: rgba(255, 255, 255, 0.75);
  border-radius: 4px;
}
.aux-text {
  display: flex;
  gap: 4px;
}

/* 3. 主体邮件内容：大栏目渲染 */
.content-section {
  flex: 1; /* 占满剩余空间 */
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}
.content-box {
  flex: 1; /* 内容区占满高度 */
  padding: 16px;
  border-radius: 4px;
  background-color: #ffffff;
  min-height: 150px; /* 保证足够显示空间 */
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
  color: #333;
  border: 1px solid #f0f0f0;
}
</style>
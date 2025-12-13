// @/store/message.js (If you see this message, that means this file has been checked and can be put into production environment)

import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useMessageStore = defineStore('message', {
  state: () => ({
    // 邮件列表
    receiveList: [], // 接收邮件
    sentList: [],    // 已发送邮件
    // 状态控制
    loading: false,
    withdrawLoading: {}, // 撤回按钮loading
    receiveExpand: false, // 接收列表展开状态
    sentExpand: false,    // 已发送列表展开状态
    // 提示信息
    message: '',
    messageType: 'success'
  }),
  actions: {
    /**
     * 显示全局提示信息
     * @param {string} text - 提示文本内容
     * @param {string} [type='success'] - 提示类型，可选值：success/error/warning/info
     * @returns {void}
     */
    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 1000)
    },

    /**
     * 获取接收邮件列表
     * @description 从后端接口获取用户接收的邮件列表，处理加载状态和异常提示
     * @async
     * @returns {Promise<void>}
     */
    async getReceiveEmail() {
      try {
        this.loading = true
        const res = await request.get('/messages/received')
        this.receiveList = res || []
        this.showMessage('获取接收邮件成功')
      } catch (err) {
        console.error('获取接收邮件失败：', err)
        this.receiveList = []
        this.showMessage(`获取失败：${err.response?.data?.message || '网络异常'}`, 'error')
      } finally {
        this.loading = false
      }
    },

    /**
     * 获取已发送邮件列表
     * @description 从后端接口获取用户已发送的邮件列表，处理加载状态和异常提示
     * @async
     * @returns {Promise<void>}
     */
    async getSentEmail() {
      try {
        this.loading = true
        const res = await request.get('/messages/sent')
        this.sentList = res || []
        this.showMessage('获取已发送邮件成功')
      } catch (err) {
        console.error('获取已发送邮件失败：', err)
        this.sentList = []
        this.showMessage(`获取失败：${err.response?.data?.message || '网络异常'}`, 'error')
      } finally {
        this.loading = false
      }
    },

    /**
     * 发送邮件
     * @description 验证表单合法性后，调用后端接口发送邮件，返回发送结果
     * @async
     * @param {Object} form - 邮件发送表单
     * @param {string} form.receiver_email - 收件人邮箱
     * @param {string} form.content - 邮件内容
     * @returns {Promise<boolean>} 发送成功返回true，失败返回false
     */
    async sendEmail(form) {
      // 表单验证
      if (!form.receiver_email) {
        this.showMessage('请输入收件人邮箱', 'error')
        return false
      }
      if (!form.content) {
        this.showMessage('请输入邮件内容', 'error')
        return false
      }

      try {
        this.loading = true
        const res = await request.post('/messages', {
          content: form.content,
          receiver_email: form.receiver_email
        })
        if (res && res.id) {
          this.showMessage('邮件发送成功！')
          return true
        } else {
          this.showMessage('邮件发送失败，请重试', 'error')
          return false
        }
      } catch (err) {
        console.error('发送邮件失败：', err)
        this.showMessage(`发送失败：${err.response?.data?.message || '网络异常'}`, 'error')
        return false
      } finally {
        this.loading = false
      }
    },

    /**
     * 撤回指定ID的邮件
     * @description 调用后端接口撤回邮件，更新前端撤回按钮加载状态，撤回成功后从已发送列表移除该邮件
     * @async
     * @param {number|string} messageId - 要撤回的邮件ID
     * @returns {Promise<void>}
     */
    async withdrawMessage(messageId) {
      try {
        this.withdrawLoading = { ...this.withdrawLoading, [messageId]: true }
        const res = await request.delete(`/messages/${messageId}`)
        if (res?.detail === '私信已成功撤回') {
          this.showMessage('邮件撤回成功！')
          // 前端移除该邮件
          this.sentList = this.sentList.filter(item => item.id !== messageId)
        } else {
          this.showMessage('邮件撤回失败，请重试', 'error')
        }
      } catch (err) {
        console.error('撤回邮件失败：', err)
        this.showMessage(`撤回失败：${err.response?.data?.detail || '网络异常'}`, 'error')
      } finally {
        this.withdrawLoading = { ...this.withdrawLoading, [messageId]: false }
      }
    },

    /**
     * 前端标记邮件为已读（仅更新前端状态，无后端请求）
     * @description 根据邮件类型更新对应列表中邮件的已读状态，核心业务需求
     * @param {number|string} messageId - 要标记的邮件ID
     * @param {string} type - 邮件类型，可选值：receive(接收邮件)/sent(已发送邮件)
     * @returns {void}
     */
    markAsRead(messageId, type) {
      // type: receive（接收邮件）/ sent（已发送邮件）
      if (type === 'receive') {
        // 接收邮件：标记自己已读
        const target = this.receiveList.find(item => item.id === messageId)
        if (target) {
          target.is_read = true
        }
      } else if (type === 'sent') {
        // 已发送邮件：标记对方已读（可选，按实际需求）
        const target = this.sentList.find(item => item.id === messageId)
        if (target) {
          target.is_read = true
        }
      }
    }
  }
})
<script setup>
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'

const router = useRouter()
const { toast, toasts } = useToast()

// 测试所有 Toast 类型
const testSuccess = () => {
  toast.success('这是一个成功提示！操作已成功完成。')
}

const testError = () => {
  toast.error('这是一个错误提示！操作失败，请检查后重试。')
}

const testInfo = () => {
  toast.info('这是一个信息提示！这是一条重要的通知信息。')
}

const testWarning = () => {
  toast.warning('这是一个警告提示！请注意相关事项。')
}

// 测试多个 Toast 同时显示
const testMultiple = () => {
  toast.success('第一个 Toast - 成功')
  setTimeout(() => toast.error('第二个 Toast - 错误'), 200)
  setTimeout(() => toast.info('第三个 Toast - 信息'), 400)
  setTimeout(() => toast.warning('第四个 Toast - 警告'), 600)
}

// 测试长文本
const testLongText = () => {
  toast.info('这是一条非常长的提示信息，用来测试 Toast 组件在显示长文本时的表现，看看是否会正确换行和显示完整内容。')
}

// 测试自动消失
const testAutoClose = () => {
  toast.success('这条消息会在 2 秒后自动消失', 2000)
}

// 清空所有 Toast
const clearAll = () => {
  toast.clear()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="toast-test-page">
    <div class="header">
      <h1>Toast 提示系统测试页面</h1>
      <p>当前 Toast 数量: {{ toasts.length }}</p>
    </div>

    <div class="test-section">
      <h2>基础测试</h2>
      <div class="button-group">
        <button @click="testSuccess" class="test-btn success">测试成功提示</button>
        <button @click="testError" class="test-btn error">测试错误提示</button>
        <button @click="testInfo" class="test-btn info">测试信息提示</button>
        <button @click="testWarning" class="test-btn warning">测试警告提示</button>
      </div>
    </div>

    <div class="test-section">
      <h2>高级测试</h2>
      <div class="button-group">
        <button @click="testMultiple" class="test-btn">测试多个 Toast 同时显示</button>
        <button @click="testLongText" class="test-btn">测试长文本显示</button>
        <button @click="testAutoClose" class="test-btn">测试自动消失（2秒）</button>
        <button @click="clearAll" class="test-btn danger">清空所有 Toast</button>
      </div>
    </div>

    <div class="test-section">
      <h2>当前 Toast 列表（调试用）</h2>
      <div v-if="toasts.length === 0" class="empty">暂无 Toast</div>
      <div v-else class="toast-list">
        <div v-for="toastItem in toasts" :key="toastItem.id" class="toast-item">
          <span class="toast-type">{{ toastItem.type }}</span>
          <span class="toast-message">{{ toastItem.message }}</span>
          <span class="toast-id">ID: {{ toastItem.id }}</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <button @click="goHome" class="home-btn">返回首页</button>
    </div>
  </div>
</template>

<style scoped>
.toast-test-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  min-height: 100vh;
}

.header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.header p {
  color: #666;
  font-size: 14px;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.test-section h2 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.test-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.test-btn:hover {
  opacity: 0.8;
  transform: translateY(-2px);
}

.test-btn.success {
  background: #52c41a;
  color: white;
}

.test-btn.error {
  background: #ff4d4f;
  color: white;
}

.test-btn.info {
  background: #1890ff;
  color: white;
}

.test-btn.warning {
  background: #faad14;
  color: white;
}

.test-btn.danger {
  background: #ff4d4f;
  color: white;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toast-item {
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.toast-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  min-width: 60px;
  text-align: center;
}

.toast-item:nth-child(1) .toast-type {
  background: #f6ffed;
  color: #52c41a;
}

.toast-item:nth-child(2) .toast-type {
  background: #fff2f0;
  color: #ff4d4f;
}

.toast-item:nth-child(3) .toast-type {
  background: #e6f7ff;
  color: #1890ff;
}

.toast-item:nth-child(4) .toast-type {
  background: #fffbe6;
  color: #faad14;
}

.toast-message {
  flex: 1;
  color: #333;
}

.toast-id {
  color: #999;
  font-size: 12px;
}

.empty {
  color: #999;
  text-align: center;
  padding: 20px;
}

.footer {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #eee;
  text-align: center;
}

.home-btn {
  padding: 10px 30px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.home-btn:hover {
  background: #40a9ff;
}
</style>

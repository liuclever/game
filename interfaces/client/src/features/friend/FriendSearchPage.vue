<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const { message, messageType, showMessage } = useMessage()

const userId = ref(String(route.query.id || ''))

const doSearch = () => {
  const id = String(userId.value || '').trim()
  if (!id) {
    showMessage('请输入要查找的用户id', 'info')
    return
  }
  router.push({ path: '/player/detail', query: { id } })
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="friend-search-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="section">
      请输入要查找的用户id:
      <input class="id-input" v-model="userId" />
      <button class="btn" @click="doSearch">查找</button>
    </div>

    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.friend-search-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 6px 0;
}

.id-input {
  width: 220px;
  height: 22px;
  padding: 0 6px;
  border: 1px solid #aaa;
  margin: 0 6px;
}

.btn {
  height: 22px;
  padding: 0 8px;
  border: 1px solid #aaa;
  background: #f7f7f7;
  cursor: pointer;
}

.btn:hover {
  background: #eeeeee;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>

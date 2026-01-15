<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref } from 'vue'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const targetId = route.query.target_id
const targetName = route.query.target_name || '该玩家'
const loading = ref(false)

const handleConfirm = async () => {
  if (loading.value) return
  if (!targetId) {
    router.push({
      path: '/message',
      query: {
        message: '缺少目标用户ID',
        type: 'error'
      }
    })
    return
  }
  
  loading.value = true
  try {
    const res = await http.post('/mail/unblock', { target_id: parseInt(targetId) })
    if (res.data.ok) {
      router.push({
        path: '/message',
        query: {
          message: res.data.message || '已成功解除拉黑',
          type: 'success'
        }
      })
    } else {
      router.push({
        path: '/message',
        query: {
          message: res.data.error || '解除拉黑失败',
          type: 'error'
        }
      })
    }
  } catch (e) {
    router.push({
      path: '/message',
      query: {
        message: e?.response?.data?.error || '解除拉黑失败',
        type: 'error'
      }
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="unblock-confirm-page">
    <div class="section">确定要解除拉黑{{ targetName }}吗？</div>
    <div class="section">解除拉黑后可以重新接收对方的消息和好友请求。</div>
    
    <div class="section spacer">
      <a class="link" @click="handleConfirm" v-if="!loading">确定</a>
      <span v-else>处理中...</span>
      <a class="link" @click="handleCancel" style="margin-left: 10px;" v-if="!loading">取消</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.unblock-confirm-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.spacer {
  margin-top: 16px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: underline;
}

.link:hover {
  text-decoration: underline;
}
</style>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref } from 'vue'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const message = route.query.message || '确定要执行此操作吗？'
const action = route.query.action || '' // challenge 或 occupy
const type = route.query.type || 'normal' // 场次类型
const ballName = route.query.ballName || '捕捉球'
const loading = ref(false)

const handleConfirm = async () => {
  if (loading.value) return
  loading.value = true
  
  try {
    let apiUrl = ''
    if (action === 'challenge') {
      apiUrl = '/arena/challenge'
    } else if (action === 'occupy') {
      apiUrl = '/arena/occupy'
    } else {
      router.back()
      return
    }
    
    const res = await http.post(apiUrl, { type })
    if (res.data.ok) {
      // 操作成功，返回擂台页面
      router.push('/arena')
    } else {
      // 操作失败，跳转到错误消息页面
      router.push({
        path: '/message',
        query: {
          message: res.data.error || '操作失败',
          type: 'error'
        }
      })
    }
  } catch (e) {
    router.push({
      path: '/message',
      query: {
        message: e.response?.data?.error || '操作失败',
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
  <div class="confirm-page">
    <div class="section">{{ message }}</div>
    
    <div class="section spacer">
      <button class="btn btn-confirm" @click="handleConfirm" :disabled="loading">
        {{ loading ? '处理中...' : '确定' }}
      </button>
      <button class="btn btn-cancel" @click="handleCancel" :disabled="loading">取消</button>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.confirm-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.spacer {
  margin-top: 16px;
}

.btn {
  padding: 4px 16px;
  font-size: 16px;
  cursor: pointer;
  border: 1px solid #CCCCCC;
  margin-right: 8px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-confirm {
  background: #0066CC;
  color: white;
  border-color: #0066CC;
}

.btn-cancel {
  background: white;
  color: black;
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

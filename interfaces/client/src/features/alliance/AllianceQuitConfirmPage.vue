<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(false)

const handleConfirm = async () => {
  if (loading.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/alliance/quit')
    
    if (res.data?.ok) {
      router.push('/alliance')
    } else {
      router.push({
        path: '/alliance/council',
        query: {
          error: res.data?.error || '退出联盟失败'
        }
      })
    }
  } catch (err) {
    console.error('退出联盟失败', err)
    router.push({
      path: '/alliance/council',
      query: {
        error: err.response?.data?.error || '退出联盟失败，请稍后重试'
      }
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/alliance/council')
}

const goBack = () => {
  router.push('/alliance/council')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="quit-confirm-page">
    <div class="section">确定要退出联盟吗？</div>
    <div class="section">退出后需要等待48小时才能再次加入联盟。</div>
    
    <div class="section spacer">
      <a class="link" @click="handleConfirm" v-if="!loading">确定</a>
      <span v-else>处理中...</span>
      <a class="link" @click="handleCancel" style="margin-left: 10px;" v-if="!loading">取消</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goBack">返回议事厅</a>
    </div>
    
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.quit-confirm-page {
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

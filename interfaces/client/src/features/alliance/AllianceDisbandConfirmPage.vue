<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const errorMsg = ref('')

const handleConfirm = async () => {
  if (loading.value) return
  
  loading.value = true
  
  try {
    const res = await http.post('/alliance/disband')
    
    if (res.data?.ok) {
      router.push({
        path: '/alliance/disband-result',
        query: {
          success: 'true',
          message: res.data?.message || '联盟已解散'
        }
      })
    } else {
      errorMsg.value = res.data?.error || '解散联盟失败'
    }
  } catch (err) {
    console.error('解散联盟失败', err)
    errorMsg.value = err.response?.data?.error || '解散联盟失败，请稍后重试'
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
  <div class="disband-confirm-page">
    <div class="section title">【解散联盟】</div>
    
    <div class="section warning">
      警告：解散联盟后，所有成员将被移除，联盟数据将被永久删除，此操作不可恢复！
    </div>
    
    <div v-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <div class="section">
      <div>确定要解散联盟吗？</div>
    </div>
    
    <div class="section">
      <a class="link" @click="handleConfirm" v-if="!loading">确定解散</a>
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
.disband-confirm-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
}

.warning {
  color: #CC0000;
  font-weight: bold;
}

.error {
  color: #CC0000;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.spacer {
  margin-top: 16px;
}
</style>

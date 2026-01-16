<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const action = route.query.action || ''  // 'kick' 或 'assign'
const targetUserId = route.query.target_user_id || ''
const targetNickname = route.query.target_nickname || ''
const armyType = route.query.army_type || ''
const armyName = route.query.army_name || ''
const loading = ref(false)

const message = ref('')
const detailMessage = ref('')

onMounted(() => {
  if (action === 'kick') {
    message.value = `确定要将${targetNickname || `玩家${targetUserId}`}踢出军队吗？`
    detailMessage.value = '踢出后该成员将进入"未分配"队列'
  } else if (action === 'assign') {
    message.value = `确定要将${targetNickname || `玩家${targetUserId}`}分配到${armyName}吗？`
    detailMessage.value = `分配后该成员将加入${armyName}`
  } else {
    message.value = '无效的操作'
  }
})

const handleConfirm = async () => {
  if (loading.value) return
  if (!action || !targetUserId) {
    router.push('/alliance/barracks')
    return
  }
  
  loading.value = true
  
  try {
    const params = {
      target_user_id: parseInt(targetUserId),
      action: action
    }
    
    if (action === 'assign' && armyType) {
      params.army_type = parseInt(armyType)
    }
    
    const res = await http.post('/alliance/members/manage-army', params)
    
    if (res.data?.ok) {
      // 操作成功，返回兵营页面
      router.push('/alliance/barracks')
    } else {
      // 操作失败，显示错误信息（可以跳转到错误页面或返回）
      router.push({
        path: '/alliance/barracks',
        query: {
          error: res.data?.error || '操作失败'
        }
      })
    }
  } catch (err) {
    console.error('manage member army failed', err)
    router.push({
      path: '/alliance/barracks',
      query: {
        error: err.response?.data?.error || '操作失败'
      }
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/alliance/barracks')
}

const goBarracks = () => {
  router.push('/alliance/barracks')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="confirm-page">
    <div class="section">{{ message }}</div>
    <div class="section">{{ detailMessage }}</div>
    
    <div class="section spacer">
      <a class="link" @click="handleConfirm" v-if="!loading">确定</a>
      <span v-else>处理中...</span>
      <a class="link" @click="handleCancel" style="margin-left: 10px;" v-if="!loading">取消</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goBarracks">返回联盟兵营</a>
    </div>
    
    <div class="section">
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

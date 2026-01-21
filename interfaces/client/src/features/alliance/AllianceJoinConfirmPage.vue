<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

const allianceId = computed(() => route.query.alliance_id)
const allianceName = computed(() => route.query.alliance_name || '')
const allianceLevel = computed(() => route.query.alliance_level || '')
const memberCount = computed(() => route.query.member_count || '')
const memberCapacity = computed(() => route.query.member_capacity || '')

const handleConfirm = async () => {
  if (loading.value) return
  if (!allianceId.value) {
    router.push('/alliance/hall')
    return
  }
  
  loading.value = true
  
  try {
    const res = await http.post('/alliance/join', { alliance_id: parseInt(allianceId.value) })
    
    if (res.data?.ok) {
      router.push({
        path: '/alliance/join-result',
        query: {
          success: 'true',
          message: res.data?.message || '加入联盟成功',
          alliance_name: allianceName.value
        }
      })
    } else {
      router.push({
        path: '/alliance/join-result',
        query: {
          success: 'false',
          error: res.data?.error || '加入失败',
          alliance_name: allianceName.value
        }
      })
    }
  } catch (err) {
    console.error('加入联盟失败', err)
    router.push({
      path: '/alliance/join-result',
      query: {
        success: 'false',
        error: err.response?.data?.error || '加入失败，请稍后重试',
        alliance_name: allianceName.value
      }
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/alliance/hall')
}

const goBack = () => {
  router.push('/alliance/hall')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  if (!allianceId.value) {
    router.push('/alliance/hall')
  }
})
</script>

<template>
  <div class="join-confirm-page">
    <div class="section">确定加入【{{ allianceName }}】吗？</div>
    <div v-if="allianceLevel || memberCount" class="section">
      <span v-if="allianceLevel">等级：{{ allianceLevel }}级</span>
      <span v-if="memberCount && memberCapacity">，成员：{{ memberCount }}/{{ memberCapacity }}</span>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="handleConfirm" v-if="!loading">确定</a>
      <span v-else>处理中...</span>
      <a class="link" @click="handleCancel" style="margin-left: 10px;" v-if="!loading">取消</a>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goBack">返回联盟大厅</a>
    </div>
    
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.join-confirm-page {
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

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isSuccess = computed(() => route.query.success === 'true')
const message = computed(() => route.query.message || '')
const error = computed(() => route.query.error || '')
const allianceName = computed(() => route.query.alliance_name || '')

const goHall = () => {
  router.push('/alliance/hall')
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="join-result-page">
    <div v-if="isSuccess" class="section message success">
      {{ message || '加入联盟成功' }}
    </div>
    <div v-else class="section message error">
      {{ error || message || '加入联盟失败' }}
    </div>

    <div v-if="isSuccess && allianceName" class="section detail">
      已成功加入【{{ allianceName }}】
    </div>

    <div class="section spacer">
      <a class="link" @click="goHall">返回联盟大厅</a>
    </div>
    <div class="section">
      <a class="link" @click="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.join-result-page {
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

.message {
  font-weight: bold;
  margin-bottom: 8px;
}

.message.success {
  color: green;
}

.message.error {
  color: #CC0000;
}

.detail {
  color: #333;
  margin-bottom: 8px;
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

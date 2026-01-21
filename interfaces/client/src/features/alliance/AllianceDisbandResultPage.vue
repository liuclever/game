<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isSuccess = computed(() => route.query.success === 'true')
const message = computed(() => route.query.message || '')

const goHall = () => {
  router.push('/alliance/hall')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="disband-result-page">
    <div v-if="isSuccess" class="section message success">
      {{ message || '联盟已解散' }}
    </div>
    <div v-else class="section message error">
      {{ message || '解散联盟失败' }}
    </div>

    <div class="section spacer">
      <a class="link" @click="goHall">前往联盟大厅</a>
    </div>
    
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.disband-result-page {
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

.message {
  font-weight: bold;
}

.success {
  color: #155724;
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

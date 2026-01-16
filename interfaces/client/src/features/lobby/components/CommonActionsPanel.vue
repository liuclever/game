<template>
  <div class="panel">
    <div class="title">【常用功能】</div>
    <div class="tabs">
      <router-link to="/cultivation" class="link">[修行]</router-link>
      <span>[竞技]</span>
      <router-link to="/tasks/daily" class="link">[任务]</router-link>
      <span>[师徒]</span>
    </div>
    <div class="cultivation-status" v-if="cultivationStatus">
      修行: {{ cultivationStatus.is_cultivating ? '修行中' : '空闲中' }}
      <router-link to="/cultivation" class="link">{{ cultivationStatus.is_cultivating ? '[结束修行]' : '[开始修行]' }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/services/http.js'

const cultivationStatus = ref(null)

const fetchCultivationStatus = async () => {
  try {
    const res = await http.get('/cultivation/status')
    if (res.data.ok !== false) {
      cultivationStatus.value = res.data
    }
  } catch (e) {
    console.error('获取修行状态失败', e)
  }
}

onMounted(() => {
  fetchCultivationStatus()
})
</script>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
}

.title {
  margin-bottom: 4px;
}

.tabs .link + .link {
  margin-left: 4px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  text-decoration: none;
}

.cultivation-status {
  margin-top: 4px;
  font-size: 16px;
}
</style>

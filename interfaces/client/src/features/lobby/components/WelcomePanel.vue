<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToDailyTasks = () => {
  router.push('/tasks/daily')
}
</script>

<template>
  <div class="panel">
    <div>
      欢迎您，<span class="name">杨明</span> 🐦 (ID:12211)
      <span class="link">好友 &gt;&gt;</span>
    </div>
    <div class="mt">
      每日必做 <span class="strong">12/14</span> 项
      <span class="link" @click="goToDailyTasks">查看</span>
    </div>
    <div class="mt">今日已签到</div>
      <div class="mt">
        任务：通关【回音之谷】 <span class="link" @click="goToDailyTasks">前往</span>
      </div>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 6px 8px;
}

.mt {
  margin-top: 2px;
}

.name {
  color: #cc3300;
  font-weight: bold;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-left: 4px;
}

.strong {
  color: #cc0000;
  font-weight: bold;
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const dailyTasks = ref([
  { id: 'login_game', points: 10, name: '登录游戏', current: 0, total: 1 },
  { id: 'crystal_tower', points: 9, name: '水晶灌注3次', current: 0, total: 3 },
  { id: 'offline_practice', points: 7, name: '离线修行1次', current: 0, total: 1 },
  { id: 'dungeon_2', points: 10, name: '通关副本2次', current: 0, total: 2 },
  { id: 'arena_1', points: 5, name: '擂台争霸1次', current: 0, total: 1 },
  { id: 'duel_3', points: 9, name: '比武切磋3次', current: 0, total: 3 },
  { id: 'tower_2', points: 10, name: '勇闯重塔2次', current: 0, total: 2 },
  { id: 'battlefield_1', points: 5, name: '古战场报名1次', current: 0, total: 1 },
  { id: 'bone_1', points: 5, name: '战骨强化1次', current: 0, total: 1 },
  { id: 'hunt_5', points: 5, name: '猎魂5次', current: 0, total: 5 },
  { id: 'fire_energy_1', points: 5, name: '领取火能原料1次', current: 0, total: 1 },
  { id: 'fortune_talisman_1', points: 10, name: '使用招财神符1次', current: 0, total: 1 },
  { id: 'alliance_donate_10', points: 10, name: '联盟捐贡10点', current: 0, total: 10 },
])

const activePoints = ref(0)

const fetchActivity = async () => {
  try {
    const response = await fetch('/api/task/daily_activity')
    const result = await response.json()
    if (result.ok) {
      activePoints.value = result.data.activity_value
      const completed = result.data.completed_tasks || []
      dailyTasks.value.forEach(task => {
        if (completed.includes(task.id)) {
          task.current = task.total
        }
      })
    }
  } catch (error) {
    console.error('Failed to fetch activity:', error)
  }
}

onMounted(() => {
  fetchActivity()
})

const completedCount = computed(() => dailyTasks.value.filter(t => t.current >= t.total).length)
const uncompletedCount = computed(() => dailyTasks.value.length - completedCount.value)

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="daily-tasks-page">
    <div class="header">
      【今日活跃:{{ activePoints }}点】<br />
      <span class="link" @click="router.push('/tasks/activity-gifts')">领取礼包>></span>
    </div>
    
    <div class="title-section">
      <div class="title">【每日事务】</div>
      <div class="stats">未完成项:{{ uncompletedCount }}| <span class="link" @click="router.push('/tasks/completed')">已完成项:{{ completedCount }}</span></div>
    </div>

    <div class="task-list">
      <div v-for="(task, index) in dailyTasks" :key="index" class="task-item">
        {{ index + 1 }}. ({{ task.points }}点){{ task.name }} {{ task.current }}/{{ task.total }}
      </div>
    </div>

    <div class="footer-note">
      轻松积累活跃度，喜得4重大礼包！积累就从每日事务开始··· <span class="link">详情>></span>
    </div>

    <div class="footer">
      <span class="link" @click="goHome">返回游戏首页</span>
    </div>
  </div>
</template>

<style scoped>
.daily-tasks-page {
  background-color: #fff;
  min-height: 100vh;
  padding: 10px;
  font-size: 14px;
  color: #000;
  line-height: 1.5;
}

.header {
  margin-bottom: 5px;
  font-weight: bold;
}

.title-section {
  margin-top: 10px;
  margin-bottom: 5px;
}

.title {
  font-weight: bold;
}

.stats {
  font-size: 14px;
}

.task-list {
  margin-bottom: 15px;
}

.task-item {
  margin-bottom: 2px;
}

.link {
  color: #0000ee;
  text-decoration: underline;
  cursor: pointer;
}

.footer-note {
  margin-top: 10px;
  margin-bottom: 5px;
  font-size: 14px;
}

.footer {
  margin-top: 20px;
}
</style>

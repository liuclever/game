<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const allTargets = ref([
  { id: 1, seq: 1, name: '林中空地1号土地', signupCount: 18 },
  { id: 2, seq: 2, name: '幻灵镇1号土地', signupCount: 26 },
  { id: 3, seq: 3, name: '林中空地2号土地', signupCount: 9 },
  { id: 4, seq: 4, name: '林中空地1号据点', signupCount: 4 },
  { id: 5, seq: 5, name: '幻灵镇1号据点', signupCount: 7 },
])

const visibleTargets = computed(() => allTargets.value.filter((target) => target.id !== 3))

const handleAttack = async (target) => {
  const confirmed = window.confirm(`确认报名攻打 ${target.name} 吗？`)
  if (!confirmed) {
    return
  }
  try {
    const res = await http.post('/alliance/war/target-signup', {
      target_id: target.id,
      army: 'dragon',
    })
    if (res.data?.ok) {
      alert('报名成功，等待盟主确认。')
    } else {
      alert(res.data?.error || '报名失败')
    }
  } catch (err) {
    console.error('攻打报名失败', err)
    alert(err.response?.data?.error || '报名失败')
  }
}

const goBack = () => {
  router.back()
}

const goWar = () => {
  router.push('/alliance/war')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="targets-page">
    <div class="section title">【土地详情】</div>
    <div class="section header">序号.土地.报名联盟数</div>

    <div
      v-for="target in visibleTargets"
      :key="target.id"
      class="section row"
    >
      <span>{{ target.seq }}.</span>
      <span class="blue">{{ target.name }}.</span>
      <span>{{ target.signupCount }}</span>
      <a class="link" @click.prevent="handleAttack(target)">攻打</a>
    </div>

    <div class="section footer-links">
      <a class="link" @click.prevent="goBack">返回前页</a>
      <a class="link" @click.prevent="goWar">返回盟战</a>
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.targets-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 14px 18px 32px;
  font-size: 13px;
  line-height: 1.6;
  font-family: 'SimSun', '宋体', serif;
  color: #000000;
}

.section {
  margin: 6px 0;
}

.title {
  font-weight: bold;
}

.header {
  font-weight: bold;
  margin-top: 2px;
}

.row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.blue {
  color: #0066cc;
}

.link {
  color: #0066cc;
  cursor: pointer;
  margin-left: 8px;
}

.link:hover {
  text-decoration: underline;
}

.footer-links {
  margin-top: 24px;
  display: flex;
  gap: 18px;
}
</style>

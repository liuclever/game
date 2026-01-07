<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goDetail = (landId) => {
  router.push(`/alliance/war/land/${landId}`)
}

const landTargets = ref([
  { id: 1, label: '林中空地1号土地', owner: 'ぜ紫月遮天づ' },
  { id: 2, label: '幻灵镇1号土地', owner: '蹲街_浅/唱_季`沫✨' },
  { id: 4, label: '林中空地1号据点', owner: '无' },
  { id: 5, label: '幻灵镇1号据点', owner: '明月' },
])
</script>

<template>
  <div class="targets-page">
    <div class="section title">【土地详情】</div>
    <div class="section header">序号.土地.占领联盟</div>

    <div
      v-for="(land, index) in landTargets"
      :key="land.id"
      class="section row clickable"
      @click="goDetail(land.id)"
    >
      {{ index + 1 }}.<span class="blue">{{ land.label }}.</span> {{ land.owner }}
    </div>

    <div class="section footer-links">
      <div @click="goAlliance" class="link">返回联盟</div>
      <div @click="goHome" class="link">返回游戏首页</div>
    </div>
  </div>
</template>

<style scoped>
.targets-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px 24px;
  font-family: 'SimSun', '宋体', serif;
  font-size: 13px;
  line-height: 1.6;
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
  gap: 4px;
  align-items: center;
}

.clickable {
  cursor: pointer;
}

.clickable:hover .blue {
  text-decoration: underline;
}

.blue {
  color: #0066cc;
  margin: 0 6px 0 2px;
}

.footer-links {
  margin-top: 20px;
  display: flex;
  gap: 16px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}
</style>

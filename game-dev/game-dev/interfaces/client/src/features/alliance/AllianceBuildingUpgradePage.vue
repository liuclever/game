<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const alliance = ref(null)
const buildings = ref([])
const upgradeInfo = ref(null)
const errorMsg = ref('')
const successMsg = ref('')

const fetchBuildings = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/buildings')
    if (res.data.ok) {
      alliance.value = res.data.alliance
      buildings.value = res.data.buildings || []
      upgradeInfo.value = res.data.councilUpgrade || null
    } else {
      errorMsg.value = res.data.error || '获取建筑信息失败'
    }
  } catch (err) {
    console.error('获取建筑信息失败', err)
    errorMsg.value = '网络异常，稍后再试'
  } finally {
    loading.value = false
  }
}

const councilBlockReasons = computed(() => upgradeInfo.value?.blockedReasons || [])
const isMaxLevel = computed(() => !!upgradeInfo.value?.isMaxLevel)

const showComingSoon = (building) => {
  errorMsg.value = ''
  successMsg.value = ''
  errorMsg.value = `${building.name} 暂未开放升级`
}

const goCouncilUpgrade = () => {
  router.push('/alliance/council/upgrade')
}

const goFurnaceUpgrade = () => {
  router.push('/alliance/furnace/upgrade')
}

const goTalentUpgrade = () => {
  router.push('/alliance/talent/upgrade')
}

const goBeastUpgrade = () => {
  router.push('/alliance/beast/upgrade')
}

const goItemUpgrade = () => {
  router.push('/alliance/item/upgrade')
}

const goBackCouncil = () => {
  router.push('/alliance/council')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchBuildings()
})
</script>

<template>
  <div class="building-upgrade-page">
    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="alliance">
            <div class="section title">联盟建筑升级</div>

      <div class="section building-list">
        <div
          v-for="building in buildings"
          :key="building.key"
          class="building-item"
        >
          <span class="name">{{ building.name }} ({{ building.level }}级)</span>
          <a
            v-if="building.key === 'council'"
            class="link"
            @click.prevent="goCouncilUpgrade"
          >
            升级
          </a>
          <a
            v-else-if="building.key === 'furnace'"
            class="link"
            @click.prevent="goFurnaceUpgrade"
          >
            升级
          </a>
          <a
            v-else-if="building.key === 'talent'"
            class="link"
            @click.prevent="goTalentUpgrade"
          >
            升级
          </a>
          <a
            v-else-if="building.key === 'beast'"
            class="link"
            @click.prevent="goBeastUpgrade"
          >
            升级
          </a>
          <a
            v-else-if="building.key === 'warehouse'"
            class="link"
            @click.prevent="goItemUpgrade"
          >
            升级
          </a>
          <a
            v-else
            class="link"
            @click.prevent="showComingSoon(building)"
          >
            升级
          </a>
        </div>
      </div>

      <div class="section info-block" v-if="successMsg || errorMsg || councilBlockReasons.length || isMaxLevel">
        <div v-if="successMsg" class="success">{{ successMsg }}</div>
        <div v-else-if="errorMsg" class="error">{{ errorMsg }}</div>
        <div v-else-if="isMaxLevel">议事厅已达到最高等级。</div>
        <template v-else-if="councilBlockReasons.length">
          <div>无法升级原因：</div>
          <div v-for="(reason, idx) in councilBlockReasons" :key="idx" class="error">
            {{ reason }}
          </div>
        </template>
      </div>

      <div class="section nav">
        <a class="link" @click="goBackCouncil">返回议事厅</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>

    </template>
    <div v-else class="section">未加入联盟，无法查看建筑信息</div>
  </div>
</template>

<style scoped>
.building-upgrade-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 18px;
  font-size: 14px;
  line-height: 1.7;
  font-family: 'Microsoft YaHei', '微软雅黑', SimSun, '宋体', sans-serif;
  color: #000;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
  color: #000;
}

.building-list {
  border-top: 1px solid #d9d9d9;
}

.building-item {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dotted #b5b5b5;
  padding: 6px 0;
}

.name {
  color: #000;
}

.link {
  color: #1a5fd0;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.info-block {
  border: 1px solid #c3c3c3;
  padding: 6px 10px;
  background: #f5f6f8;
}

.success {
  color: #0f7a0d;
}

.error {
  color: #cc0000;
}

.footer-info {
  margin-top: 16px;
  color: #53627a;
  font-size: 12px;
  border-top: 1px solid #dfe4ea;
  padding-top: 8px;
}
</style>

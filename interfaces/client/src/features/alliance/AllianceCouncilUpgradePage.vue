<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const alliance = ref(null)
const upgradeInfo = ref(null)
const errorMsg = ref('')
const successMsg = ref('')

const fetchUpgradeInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/buildings')
    if (res.data.ok) {
      alliance.value = res.data.alliance
      upgradeInfo.value = res.data.councilUpgrade || null
    } else {
      errorMsg.value = res.data.error || '获取升级信息失败'
    }
  } catch (err) {
    console.error('获取升级信息失败', err)
    errorMsg.value = '网络异常，请稍后再试'
  } finally {
    loading.value = false
  }
}

const requirements = computed(() => upgradeInfo.value?.requirements || [])
const canUpgrade = computed(() => !!upgradeInfo.value?.canUpgrade && !saving.value)
const isMaxLevel = computed(() => !!upgradeInfo.value?.isMaxLevel)

const confirmUpgrade = async () => {
  if (!canUpgrade.value || saving.value) {
    return
  }
  saving.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/council/upgrade')
    if (res.data.ok) {
      successMsg.value = res.data.message || '升级成功'
      await fetchUpgradeInfo()
    } else {
      errorMsg.value = res.data.error || '升级失败'
    }
  } catch (err) {
    console.error('升级失败', err)
    errorMsg.value = '网络异常，请稍后再试'
  } finally {
    saving.value = false
  }
}

const goAlliance = () => router.push('/alliance')
const goBuildings = () => router.push('/alliance/buildings')
const goHome = () => router.push('/')

onMounted(() => {
  fetchUpgradeInfo()
})
</script>

<template>
  <div class="council-upgrade-page">
    <div v-if="loading" class="line">加载中...</div>
    <template v-else>
      <div class="title">议事厅升级</div>

      <template v-if="upgradeInfo && !isMaxLevel">
        <div class="line">
          建筑等级：{{ upgradeInfo.currentLevel }} → {{ upgradeInfo.nextLevel }}
        </div>
        <div class="line">
          联盟成员上限：{{ upgradeInfo.memberCapacity }} → {{ upgradeInfo.memberCapacity + 10 }}
        </div>
        <div class="subtitle">要求：</div>
        <div class="line" v-for="req in requirements" :key="req.key">
          {{ req.name }}等级达到{{ req.requiredLevel }}
        </div>
        <div class="line">消耗资金：{{ upgradeInfo.costs?.funds ?? 0 }}</div>
        <div class="line">消耗焚火晶：{{ upgradeInfo.costs?.crystals ?? 0 }}</div>
        <div class="line">
          繁荣值达到{{ upgradeInfo.prosperityRequirement }}
        </div>

        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
        <div v-if="successMsg" class="success">{{ successMsg }}</div>

        <button class="confirm-btn" :disabled="!canUpgrade" @click="confirmUpgrade">
          {{ saving ? '升级中...' : '确定升级' }}
        </button>
      </template>
      <template v-else>
        <div class="line">
          {{ isMaxLevel ? '议事厅已达到最高等级。' : (errorMsg || '无法获取升级信息') }}
        </div>
      </template>

      <div class="nav">
        <a class="link" @click="goAlliance">返回联盟</a><br>
        <a class="link" @click="goBuildings">返回建筑升级</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.council-upgrade-page {
  background: #fff;
  min-height: 100vh;
  padding: 20px;
  font-size: 18px;
  color: #000;
  line-height: 1.8;
  font-family: 'Microsoft YaHei', '微软雅黑', SimSun, '宋体', sans-serif;
}

.title {
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 12px;
}

.subtitle {
  font-weight: bold;
  margin-top: 10px;
}

.line {
  margin: 4px 0;
}

.confirm-btn {
  margin-top: 12px;
  padding: 6px 16px;
  background: #1a5fd0;
  color: #fff;
  border: none;
  cursor: pointer;
}

.confirm-btn:disabled {
  background: #c2c2c2;
  cursor: not-allowed;
}

.link {
  color: #1a5fd0;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.nav {
  margin-top: 20px;
}

.error {
  color: #cc0000;
}

.success {
  color: #0f7a0d;
}
</style>

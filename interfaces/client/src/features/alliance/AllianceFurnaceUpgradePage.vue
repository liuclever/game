<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const furnace = ref(null)
const alliance = ref(null)
const errorMsg = ref('')
const successMsg = ref('')

const blockedReasons = computed(() => furnace.value?.blockedReasons || [])
const canUpgrade = computed(() => !!furnace.value?.canUpgrade)
const isMaxLevel = computed(() => !!furnace.value?.isMaxLevel)

const fetchFurnaceInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/furnace/upgrade-info')
    if (res.data.ok) {
      alliance.value = res.data.alliance || null
      furnace.value = res.data.furnace || null
    } else {
      errorMsg.value = res.data.error || '获取焚天炉信息失败'
    }
  } catch (err) {
    console.error('获取焚天炉信息失败', err)
    errorMsg.value = '网络异常，稍后再试'
  } finally {
    loading.value = false
  }
}

const confirmUpgrade = async () => {
  if (!canUpgrade.value) {
    errorMsg.value = furnace.value?.blockedReasons?.[0] || '暂无法升级'
    return
  }
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/furnace/upgrade')
    if (res.data.ok) {
      successMsg.value = res.data.message || '升级成功'
      await fetchFurnaceInfo()
    } else {
      errorMsg.value = res.data.error || '升级失败'
    }
  } catch (err) {
    console.error('升级失败', err)
    errorMsg.value = '网络异常，稍后再试'
  }
}

const goAlliance = () => router.push('/alliance')
const goBuildings = () => router.push('/alliance/buildings')
const goHome = () => router.push('/')

onMounted(() => {
  fetchFurnaceInfo()
})
</script>

<template>
  <div class="furnace-upgrade-page">
    <div v-if="loading" class="line">加载中...</div>
    <template v-else>
      <div class="title">焚天炉升级</div>
      <template v-if="furnace && !isMaxLevel">
        <div class="line">
          建筑等级：{{ furnace.currentLevel }} → {{ furnace.nextLevel }}
        </div>
        <div class="line">
          修行房间数：{{ furnace.trainingRooms }} → {{
            furnace.trainingRooms + 1
          }}
        </div>
        <div class="line">
          修行焚火晶奖励：每人 +{{ furnace.crystalBonus }} → +{{
            furnace.crystalBonus + 2
          }}
        </div>
        <div class="subtitle">要求：</div>
        <div class="line">
          议事厅等级达到 {{ furnace.requiredCouncilLevel }}
        </div>
        <div class="line">消耗资金 {{ furnace.costs?.funds || 0 }}</div>
        <div class="line">消耗焚火晶 {{ furnace.costs?.crystals || 0 }}</div>
        <div class="line">繁荣值达到 {{ furnace.prosperityRequirement }}</div>

        <div v-if="successMsg" class="success">{{ successMsg }}</div>
        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
        <div v-if="blockedReasons.length" class="blocked">
          <div>无法升级原因：</div>
          <div v-for="(reason, idx) in blockedReasons" :key="idx" class="error">
            {{ reason }}
          </div>
        </div>

        <button class="confirm-btn" :disabled="!canUpgrade" @click="confirmUpgrade">
          确定升级
        </button>
      </template>
      <template v-else>
        <div class="line">焚天炉已达到最高等级或暂未开放更高级。</div>
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
.furnace-upgrade-page {
  background: #fff;
  min-height: 100vh;
  padding: 20px;
  font-size: 18px;
  color: #000;
  line-height: 1.8;
  font-family: 'Microsoft YaHei', '微软雅黑', SimSun, '宋体', sans-serif;
}

.title {
  font-size: 18px;
  font-weight: bold;
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
  background: #c8c8c8;
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

.footer-info {
  margin-top: 20px;
  color: #53627a;
  font-size: 18px;
  border-top: 1px solid #dfe4ea;
  padding-top: 8px;
}

.error {
  color: #cc0000;
}

.success {
  color: #0f7a0d;
}

.blocked {
  margin-top: 8px;
}
</style>

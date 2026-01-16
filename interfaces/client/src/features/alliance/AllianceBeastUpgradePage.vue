<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const info = ref(null)
const alliance = ref(null)
const errorMsg = ref('')
const successMsg = ref('')

const blockedReasons = computed(() => info.value?.blockedReasons || [])
const canUpgrade = computed(() => !!info.value?.canUpgrade)
const isMaxLevel = computed(() => !!info.value?.isMaxLevel)

const fetchInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.get('/alliance/beast/upgrade-info')
    if (res.data.ok) {
      alliance.value = res.data.alliance || null
      info.value = res.data.beastRoom || null
    } else {
      errorMsg.value = res.data.error || '获取幻兽室信息失败'
    }
  } catch (err) {
    console.error('获取幻兽室信息失败', err)
    errorMsg.value = '网络异常，稍后再试'
  } finally {
    loading.value = false
  }
}

const confirmUpgrade = async () => {
  if (!canUpgrade.value) {
    errorMsg.value = info.value?.blockedReasons?.[0] || '暂无法升级'
    successMsg.value = ''
    return
  }
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const res = await http.post('/alliance/beast/upgrade')
    if (res.data.ok) {
      successMsg.value = res.data.message || '升级成功'
      await fetchInfo()
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
  fetchInfo()
})
</script>

<template>
  <div class="beast-upgrade-page">
    <div v-if="loading" class="line">加载中...</div>
    <template v-else>
      <div class="line title">幻兽室升级</div>
      <template v-if="info && !isMaxLevel">
        <div class="line">
          建筑等级：{{ info.currentLevel }} → {{ info.nextLevel }}
        </div>
        <div class="line">
          可寄存幻兽数量：{{ info.capacity }} → {{ info.capacity + 1 }}
        </div>

        <div class="line subtitle">要求：</div>
        <div class="line">议事厅等级达到 {{ info.requiredCouncilLevel }}</div>
        <div class="line">消耗资金 {{ info.costs?.funds || 0 }}</div>
        <div class="line">消耗焚火晶 {{ info.costs?.crystals || 0 }}</div>
        <div class="line">繁荣值达到 {{ info.prosperityRequirement }}</div>

        <div v-if="successMsg" class="line success">{{ successMsg }}</div>
        <div v-if="errorMsg" class="line error">{{ errorMsg }}</div>
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
        <div class="line">幻兽室已达到最高等级或暂未开放更高级。</div>
      </template>

      <div class="line link" @click="goAlliance">返回联盟</div>
      <div class="line link" @click="goHome">返回游戏首页</div>
      <div class="line link" @click="goBuildings">返回建筑升级</div>

    </template>
  </div>
</template>

<style scoped>
.beast-upgrade-page {
  background: #fff;
  min-height: 100vh;
  padding: 12px 18px;
  font-size: 17px;
  line-height: 1.8;
  font-family: 'Microsoft YaHei', '微软雅黑', SimSun, '宋体', sans-serif;
  color: #000;
}

.line {
  margin: 4px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
}

.subtitle {
  font-weight: bold;
  margin-top: 8px;
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

.footer {
  margin-top: 12px;
  color: #5a6785;
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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { fetchLandDetail } from '@/api/alliance'

const router = useRouter()
const route = useRoute()

const landId = computed(() => Number(route.params.landId ?? route.query.landId ?? 1))
const loading = ref(true)
const error = ref('')
const landName = ref('')
const buffs = ref([])
const alliances = ref([])

const buffDescription = computed(() => {
  if (!buffs.value.length) {
    return '暂无属性描述'
  }
  // 根据图1，每个属性单独一行显示，用换行符分隔
  return buffs.value.join('\n')
})

const loadLandDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    // 加载土地详情与报名联盟名单，供详情页展示
    const res = await fetchLandDetail(landId.value)
    if (res?.ok) {
      landName.value = res.data.land_name
      buffs.value = res.data.buffs || []
      alliances.value = res.data.alliances || []
    } else {
      error.value = res?.error || '土地信息获取失败'
    }
  } catch (err) {
    error.value = err?.response?.data?.error || '网络异常，稍后重试'
  } finally {
    loading.value = false
  }
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goList = () => {
  router.push('/alliance/war/targets')
}

onMounted(() => {
  loadLandDetail()
})
</script>

<template>
  <div class="targets-page">
    <div class="section title">【{{ landName || '土地详情' }}】</div>

    <div v-if="loading" class="section status">加载土地信息中...</div>
    <div v-else>
      <div v-if="error" class="section error">{{ error }}</div>

      <template v-else>
        <div class="section header">属性:</div>
        <div class="section buff">{{ buffDescription }}</div>

        <div class="section header">报名联盟:</div>
        <div class="alliances-box">
          <template v-if="alliances.length">
            <div
              v-for="(alliance, index) in alliances"
              :key="alliance.alliance_id || index"
              class="alliance-row"
            >
              <span class="blue">{{ alliance.name }}</span>
            </div>
          </template>
          <div v-else class="empty">暂无报名联盟</div>
        </div>
      </template>
    </div>

    <div class="section footer-links">
      <div @click="goList" class="link">返回攻城目标</div>
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
  font-size: 16px;
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
  margin-top: 6px;
}

.buff {
  background: #ffffff;
  border: 1px dashed #ccc;
  padding: 8px;
  word-break: break-all;
  white-space: pre-line;  /* 支持换行显示 */
}

.alliances-box {
  border: 1px solid #ddd;
  padding: 8px;
  border-radius: 4px;
}

.alliance-row {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px dashed #eee;
}

.alliance-row:last-child {
  border-bottom: none;
}

.blue {
  color: #0066cc;
}

.footer-links {
  margin-top: 20px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.empty {
  color: #666;
  font-style: italic;
}

.status {
  color: #666;
}

.error {
  color: #c0392b;
  font-weight: bold;
}
</style>

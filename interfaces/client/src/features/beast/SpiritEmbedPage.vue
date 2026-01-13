<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 路由参数 ==========
const beastId = computed(() => parseInt(route.params.beastId) || 0)
const elementKey = computed(() => route.params.element || '')

// ========== 数据状态 ==========
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMsg = ref('')
const beast = ref(null)
const availableSpirits = ref([])
const playerLevel = ref(0)

// 元素名称映射
const elementNames = {
  earth: '土',
  fire: '火',
  water: '水',
  wood: '木',
  metal: '金',
  god: '神',
}

// ========== 加载数据 ==========
const loadData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const playerRes = await http.get('/player/info')
    if (playerRes.data?.ok) {
      playerLevel.value = playerRes.data.player?.level || 0
    }
    if ((playerLevel.value || 0) < 35) {
      errorMsg.value = '35级才能解锁'
      return
    }

    // 获取幻兽信息
    const beastRes = await http.get(`/beast/${beastId.value}`)
    if (beastRes.data.ok) {
      beast.value = beastRes.data.beast
    } else {
      errorMsg.value = beastRes.data.error || '获取幻兽信息失败'
      return
    }
    
    // 获取灵件室中的战灵
    const spiritsRes = await http.get('/spirit/warehouse')
    if (spiritsRes.data.ok) {
      // 筛选匹配当前元素和种族的战灵
      const allSpirits = spiritsRes.data.spirits || []
      availableSpirits.value = allSpirits.filter(sp => {
        // 元素必须匹配
        if (sp.element !== elementKey.value) return false
        // 种族必须匹配（或者战灵是通用种族）
        if (sp.race && sp.race !== beast.value.race) return false
        return true
      })
    } else {
      errorMsg.value = spiritsRes.data.error || '获取战灵列表失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// ========== 计算属性 ==========
const elementName = computed(() => elementNames[elementKey.value] || elementKey.value)

// 计算战灵的已解锁属性条数
const getUnlockedLineCount = (spirit) => {
  if (!spirit.lines) return 0
  return spirit.lines.filter(ln => ln.unlocked).length
}

// ========== 操作 ==========
const embedSpirit = async (spiritId) => {
  try {
    const res = await http.post(`/spirit/${spiritId}/equip`, {
      beast_id: beastId.value
    })
    if (res.data.ok) {
      showMessage('镶嵌成功！', 'success')
      // 返回战灵页面
      router.push(`/beast/${beastId.value}/spirit`)
    } else {
      showMessage(res.data.error || '镶嵌失败', 'error')
    }
  } catch (err) {
    // 处理服务器返回的错误信息
    const errorMessage = err.response?.data?.error || '网络错误，请稍后重试'
    showMessage(errorMessage, 'error')
    console.error('镶嵌战灵失败:', err)
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.push(`/beast/${beastId.value}/spirit`)
}

const goHome = () => {
  router.push('/')
}

const goToSpiritDetail = (spiritId) => {
  router.push(`/spirit/${spiritId}`)
}
</script>

<template>
  <div class="embed-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 幻兽信息 -->
      <div class="section title-section">
        【{{ beast?.name }}({{ beast?.race }})】
      </div>
      
      <!-- 可选战灵列表 -->
      <div v-if="availableSpirits.length > 0" class="spirits-section">
        <div v-for="spirit in availableSpirits" :key="spirit.id" class="section spirit-row">
          <a class="link spirit-info" @click="goToSpiritDetail(spirit.id)">
            {{ elementName }}灵·{{ spirit.race }}（{{ getUnlockedLineCount(spirit) }}条属性）
          </a>
          <a class="link action-btn" @click.prevent="embedSpirit(spirit.id)">镶嵌</a>
        </div>
      </div>
      <div v-else class="section">
        暂无可用的{{ elementName }}灵战灵
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回战灵首页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
  </div>
</template>

<style scoped>
.embed-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-section {
  font-weight: bold;
  margin-bottom: 8px;
}

.spirit-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spirit-info {
  color: #0066CC;
}

.action-btn {
  color: #0066CC;
  cursor: pointer;
}

.action-btn:hover {
  text-decoration: underline;
}

.spacer {
  margin-top: 16px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.error {
  color: red;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.gray {
  color: #666;
}

.small {
  font-size: 11px;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>

<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMsg = ref('')

// 从路由参数获取
const beastId = ref(null)
const slotType = ref('')  // 槽位类型：头骨、胸骨等

// 幻兽信息
const beast = ref(null)

// 可用的战骨列表
const availableBones = ref([])

// ========== 加载数据 ==========
const loadPageData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  beastId.value = parseInt(route.params.beastId)
  slotType.value = route.query.slot || ''
  
  if (!beastId.value) {
    errorMsg.value = '缺少幻兽ID'
    loading.value = false
    return
  }
  
  try {
    // 获取幻兽信息
    const beastRes = await http.get(`/beast/${beastId.value}`)
    if (beastRes.data.ok) {
      beast.value = beastRes.data.beast
    } else {
      errorMsg.value = beastRes.data.error || '获取幻兽信息失败'
      loading.value = false
      return
    }
    
    // 获取可用的战骨
    const bonesRes = await http.get(`/bone/unequipped?slot=${encodeURIComponent(slotType.value)}`)
    if (bonesRes.data.ok) {
      availableBones.value = bonesRes.data.bones || []
    } else {
      availableBones.value = []
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPageData()
})

// ========== 操作 ==========
// 使用战骨（装备到幻兽）
const useBone = async (bone) => {
  try {
    let res
    if (bone.isInventoryItem) {
      // 背包物品：调用 use-item API（消耗物品创建战骨并装备）
      res = await http.post('/bone/use-item', {
        itemId: bone.itemId,
        beastId: beastId.value,
      })
    } else {
      // 已有战骨实体：调用 equip API
      res = await http.post('/bone/equip', {
        boneId: bone.id,
        beastId: beastId.value,
      })
    }
    if (res.data.ok) {
      
      // 返回上一页
      router.back()
    } else {
      showMessage(res.data.error || '装备失败', 'error')
    }
  } catch (err) {
    showMessage('网络错误', 'error')
    console.error('装备战骨失败:', err)
  }
}

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="bone-select-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 幻兽信息 -->
      <div class="section beast-info" v-if="beast">
        幻兽:{{ beast.name }}({{ beast.level }}级)
      </div>
      
      <!-- 可选战骨列表 -->
      <div v-if="availableBones.length === 0" class="section empty-msg">
        背包中没有可用的{{ slotType }}
      </div>
      <div v-else class="bone-list">
        <div v-for="(bone, index) in availableBones" :key="bone.isInventoryItem ? `inv-${bone.itemId}-${index}` : bone.id" class="section bone-item">
          <template v-if="bone.isInventoryItem">
            {{ bone.name }}[背包×{{ bone.quantity }}] 
          </template>
          <template v-else>
            {{ bone.name }}[{{ bone.qualityName }}{{ bone.level }}级]{{ bone.attrText }} 
          </template>
          <a class="link" @click="useBone(bone)">使用</a>
        </div>
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
  </div>
</template>

<style scoped>
.bone-select-page {
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

.beast-info {
  font-weight: bold;
}

.bone-list {
  margin: 8px 0;
}

.bone-item {
  line-height: 1.8;
}

.empty-msg {
  color: #999;
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

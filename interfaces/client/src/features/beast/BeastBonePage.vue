<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')

// 玩家资源
const gold = ref(0)
const enhancementStone = ref(0)

// 幻兽列表
const beasts = ref([])
const selectedBeastId = ref(null)

// 当前选中幻兽的战骨槽位
const slots = ref({})

// 槽位配置
const slotConfig = [
  { key: '头', label: '头', fullName: '头骨' },
  { key: '胸', label: '胸', fullName: '胸骨' },
  { key: '臂', label: '臂', fullName: '臂骨' },
  { key: '手', label: '手', fullName: '手骨' },
  { key: '腿', label: '腿', fullName: '腿骨' },
  { key: '尾', label: '尾', fullName: '尾骨' },
  { key: '魂', label: '魂', fullName: '元魂' },
]


// ========== 加载数据 ==========
const loadPageData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/bone/page-data')
    if (res.data.ok) {
      beasts.value = res.data.beasts || []
      gold.value = res.data.gold || 0
      enhancementStone.value = res.data.enhancementStone || 0
      
      // 如果URL有指定幻兽ID，使用它；否则默认选第一只
      const urlBeastId = parseInt(route.params.beastId)
      if (urlBeastId && beasts.value.some(b => b.id === urlBeastId)) {
        selectedBeastId.value = urlBeastId
      } else if (beasts.value.length > 0) {
        selectedBeastId.value = beasts.value[0].id
      }
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载战骨页面数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 加载指定幻兽的战骨
const loadBeastBones = async (beastId) => {
  if (!beastId) return
  
  try {
    const res = await http.get(`/bone/beast/${beastId}/equipped`)
    if (res.data.ok) {
      slots.value = res.data.slots || {}
    }
  } catch (err) {
    console.error('加载幻兽战骨失败:', err)
  }
}

// 监听选中幻兽变化
watch(selectedBeastId, (newId) => {
  if (newId) {
    loadBeastBones(newId)
  }
})

onMounted(() => {
  loadPageData()
})

// ========== 选中的幻兽信息 ==========
const selectedBeast = computed(() => {
  return beasts.value.find(b => b.id === selectedBeastId.value)
})

// ========== 操作 ==========
const selectBeast = (beastId) => {
  selectedBeastId.value = beastId
}

// 打开选择战骨页面
const openBoneSelector = (slotFullName) => {
  // 跳转到战骨选择页面
  router.push({
    path: `/beast/${selectedBeastId.value}/bone/select`,
    query: { slot: slotFullName }
  })
}

// 查看战骨详情
const viewBoneDetail = (boneId) => {
  router.push(`/bone/${boneId}`)
}

// 卸下战骨
const unequipBone = async (slotKey) => {
  const boneData = slots.value[slotKey]
  if (!boneData) return
  
  try {
    const res = await http.post(`/bone/unequip/${boneData.id}`)
    if (res.data.ok) {
      alert('卸下成功')
      await loadBeastBones(selectedBeastId.value)
    } else {
      alert(res.data.error || '卸下失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error('卸下战骨失败:', err)
  }
}

// 强化战骨
const enhanceBone = (slotKey) => {
  const boneData = slots.value[slotKey]
  if (!boneData) return
  alert(`强化${boneData.name}（功能待实现）`)
}

// 一键卸下
const unequipAll = async () => {
  if (!selectedBeastId.value) return

  try {
    const res = await http.post(`/bone/unequip-all/${selectedBeastId.value}`)
    if (res.data.ok) {
      alert(res.data.message || '卸下成功')
      await loadBeastBones(selectedBeastId.value)
    } else {
      alert(res.data.error || '卸下失败')
    }
  } catch (err) {
    alert('网络错误')
    console.error('一键卸下失败:', err)
  }
}

const showIntro = () => {
  alert('幻兽战骨简介：战骨可以提升幻兽的属性...')
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
  <div class="bone-page">
    <!-- 标题 -->
    <div class="section title-section">
      【幻兽战骨】 <a class="link" @click="showIntro">简介</a>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 幻兽列表 -->
      <div class="section beast-list">
        <template v-for="(beast, index) in beasts" :key="beast.id">
          <a 
            class="link beast-item"
            :class="{ active: beast.id === selectedBeastId }"
            @click="selectBeast(beast.id)"
          >{{ beast.name }}-{{ beast.realm }} ({{ beast.level }}级)</a>
          <span v-if="index < beasts.length - 1">| </span>
        </template>
      </div>
      
      <!-- 战骨槽位 -->
      <div class="slots-section">
        <div v-for="slot in slotConfig" :key="slot.key" class="section slot-row">
          <span class="slot-label">{{ slot.label }}:</span>
          <template v-if="slots[slot.key]">
            <a class="link bone-name" @click="viewBoneDetail(slots[slot.key].id)">{{ slots[slot.key].name }}</a>
            <a class="link unequip-btn" @click="unequipBone(slot.key)">卸下</a>
          </template>
          <template v-else>
            <span class="empty-slot">空</span>.<a class="link use-btn" @click="openBoneSelector(slot.fullName)">使用</a>
          </template>
        </div>
      </div>
      
      <!-- 一键卸下 -->
      <div class="section">
        <a class="link" @click="unequipAll">一键卸下</a>
      </div>
      
      <!-- 资源显示 -->
      <div class="section resource">
        铜钱:{{ gold }}
      </div>
      <div class="section resource">
        强化石:{{ enhancementStone }}
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
.bone-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title-section {
  font-weight: bold;
}

.beast-list {
  line-height: 1.8;
}

.beast-item {
  margin-right: 2px;
}

.beast-item.active {
  color: #FF6600;
  font-weight: bold;
}

.slot-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.slot-label {
  font-weight: bold;
  min-width: 20px;
}

.bone-name {
  color: #0066CC;
}

.unequip-btn {
  color: #CC0000;
  margin-left: 4px;
}

.empty-slot {
  color: #999;
}

.resource {
  font-weight: bold;
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
  font-size: 17px;
}

.enhance-btn {
  color: #0066CC;
}

.use-btn {
  color: #0066CC;
}
</style>

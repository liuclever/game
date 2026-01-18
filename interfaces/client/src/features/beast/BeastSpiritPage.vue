<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()
const route = useRoute()

// ========== 数据状态 ==========
const loading = ref(true)
const errorMsg = ref('')

// 玩家资源
const spiritPower = ref(0)
const warehouseCount = ref(0)
const warehouseCapacity = ref(100)
const playerLevel = ref(0)
const unlockedElements = ref([])

// 幻兽列表
const beasts = ref([])
const selectedBeastId = ref(null)

// 当前选中幻兽的战灵槽位
const slots = ref({})

// 元素槽位配置
const elementConfig = [
  { key: 'earth', label: '土位', name: '土' },
  { key: 'fire', label: '火位', name: '火' },
  { key: 'water', label: '水位', name: '水' },
  { key: 'wood', label: '木位', name: '木' },
  { key: 'metal', label: '金位', name: '金' },
  { key: 'god', label: '神位', name: '神' },
]

// ========== 加载数据 ==========
const loadPageData = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/spirit/page-data')
    if (res.data.ok) {
      beasts.value = res.data.beasts || []
      spiritPower.value = res.data.spiritPower || 0
      warehouseCount.value = res.data.warehouseCount || 0
      warehouseCapacity.value = res.data.warehouseCapacity || 100
      playerLevel.value = res.data.playerLevel || 0
      unlockedElements.value = res.data.unlockedElements || []
      
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
    console.error('加载战灵页面数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 加载指定幻兽的战灵
const loadBeastSpirits = async (beastId) => {
  if (!beastId) return
  
  try {
    const res = await http.get(`/spirit/beast/${beastId}/equipped`)
    if (res.data.ok) {
      slots.value = res.data.slots || {}
    }
  } catch (err) {
    console.error('加载幻兽战灵失败:', err)
  }
}

// 监听选中幻兽变化
watch(selectedBeastId, (newId) => {
  if (newId) {
    loadBeastSpirits(newId)
  }
})

onMounted(() => {
  loadPageData()
})

// ========== 选中的幻兽信息 ==========
const selectedBeast = computed(() => {
  return beasts.value.find(b => b.id === selectedBeastId.value)
})

// ========== 获取已装备战灵数量 ==========
const equippedCount = computed(() => {
  return Object.keys(slots.value).length
})

const isElementUnlocked = (elementKey) => {
  if ((playerLevel.value || 0) < 35) return false
  return (unlockedElements.value || []).includes(elementKey)
}

// ========== 操作 ==========
const selectBeast = (beastId) => {
  selectedBeastId.value = beastId
}

const unequipSpirit = async (elementKey) => {
  const spiritData = slots.value[elementKey]
  if (!spiritData) {
    alert('该槽位没有装备战灵')
    return
  }
  
  try {
    const res = await http.post(`/spirit/${spiritData.id}/unequip`)
    if (res.data.ok) {
      // 重新加载当前幻兽的战灵
      await loadBeastSpirits(selectedBeastId.value)
      // 更新仓库数量
      warehouseCount.value += 1
      alert('卸下成功，战灵已存入灵件室')
    } else {
      alert(res.data.error || '卸下失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('卸下战灵失败:', err)
  }
}

const showIntro = () => {
  alert('战灵简介：战灵可以提升幻兽的百分比属性加成，每只幻兽可装备6个元素位置的战灵（土、火、水、木、金、神）。')
}

const viewWarehouse = () => {
  if ((playerLevel.value || 0) < 35) {
    alert('35级才能解锁')
    return
  }
  router.push('/spirit/warehouse')
}

// ========== 导航 ==========
const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const goToEmbed = (elementKey) => {
  if (!isElementUnlocked(elementKey)) {
    alert('35级才能解锁')
    return
  }
  router.push(`/beast/${selectedBeastId.value}/spirit/embed/${elementKey}`)
}

// 跳转到战灵详情页
const goToSpiritDetail = (spiritId) => {
  router.push(`/spirit/${spiritId}`)
}
</script>

<template>
  <div class="spirit-page">
    <!-- 标题 -->
    <div class="section title-section">
      【战灵】
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <template v-else>
      <!-- 灵件室信息 -->
      <div class="section">
        灵件室：{{ warehouseCount }}/{{ warehouseCapacity }} <a class="link" @click="viewWarehouse">查看</a>
      </div>
      <div class="section">
        灵力：{{ spiritPower }}
      </div>
      
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
      
      <!-- 元素槽位 -->
      <div class="slots-section">
        <div v-for="slot in elementConfig" :key="slot.key" class="section slot-row">
          <span class="slot-label">{{ slot.label }}:</span>
          <template v-if="!isElementUnlocked(slot.key)">
            <span class="gray">待解锁</span>
            <span class="gray small">35级才能解锁</span>
          </template>
          <template v-else>
            <template v-if="slots[slot.key]">
              <a class="link spirit-name" @click="goToSpiritDetail(slots[slot.key].id)">{{ slot.name }}灵·{{ slots[slot.key].race }}</a>
              <a class="link action-btn" @click.prevent="unequipSpirit(slot.key)">卸下</a>
            </template>
            <template v-else>
              <a class="link action-btn" @click.prevent="goToEmbed(slot.key)">镶嵌</a>
            </template>
          </template>
        </div>
      </div>
      
      <!-- 导航 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <!-- 底部菜单（同款） -->
      <MainMenuLinks />
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    
  </div>
</template>

<style scoped>
.spirit-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17.6px; /* +10% */
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
  min-width: 40px;
}

.spirit-name {
  color: #0066CC;
}

.action-btn {
  color: #0066CC;
  margin-left: 4px;
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
  font-size: 18.7px; /* +10% */
}
</style>

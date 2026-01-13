<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const { message, messageType, showMessage } = useMessage()

const loading = ref(false)
const targetMosoul = ref(null)
const materialMosouls = ref([])
const selectedMaterialId = ref(null)

const targetId = computed(() => parseInt(route.query.id))

const loadData = async () => {
  loading.value = true
  try {
    const res = await http.get(`/mosoul/absorb/info?target_id=${targetId.value}`)
    if (res.data.ok) {
      targetMosoul.value = res.data.target
      materialMosouls.value = res.data.materials || []
    } else {
      showMessage(res.data.error || '加载失败', 'error')
    }
  } catch (e) {
    console.error('加载失败', e)
    showMessage('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

const getExpProvide = (grade) => {
  const expMap = {
    '下品': 100,
    '中品': 300,
    '上品': 1000,
    '极品': 3000
  }
  return expMap[grade] || 100
}

const doAbsorb = async (materialId) => {
  const materialMosoul = materialMosouls.value.find(m => m.id === materialId)
  if (!materialMosoul) {
    showMessage('请选择要消耗的魔魂', 'error')
    return
  }
  
  const expProvide = getExpProvide(materialMosoul.grade)
  // 已移除确认提示
  
  try {
    const res = await http.post('/mosoul/absorb', {
      target_id: targetId.value,
      material_id: materialId
    })
    
    if (res.data.ok) {
      showMessage(res.data.message || '吸收成功', 'success')
      await loadData()
    } else {
      showMessage(res.data.error || '吸收失败', 'error')
    }
  } catch (e) {
    console.error('吸收失败', e)
    showMessage(e?.response?.data?.error || '吸收失败', 'error')
  }
}

const goBack = () => {
  router.push('/mosoul')
}

onMounted(() => {
  if (!targetId.value) {
    showMessage('缺少目标魔魂ID', 'error')
    router.push('/mosoul')
    return
  }
  loadData()
})
</script>

<template>
  <div class="page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="section title">【魔魂吸收】</div>
    
    <div v-if="loading" class="section">加载中...</div>
    
    <template v-else-if="targetMosoul">
      <div class="section">
        <div>目标魔魂: {{ targetMosoul.name }}</div>
        <div>品级: {{ targetMosoul.grade }}</div>
        <div>当前经验: {{ targetMosoul.exp }} / {{ targetMosoul.max_exp }}</div>
      </div>
      
      <div class="section title">选择要消耗的魔魂:</div>
      
      <div v-if="materialMosouls.length === 0" class="section">
        没有可用的材料魔魂
      </div>
      
      <div v-for="material in materialMosouls" :key="material.id" class="section">
        <div>{{ material.name }} ({{ material.grade }})</div>
        <div>提供经验: {{ getExpProvide(material.grade) }}</div>
        <div>
          <a class="link" @click="doAbsorb(material.id)">吸收</a>
        </div>
      </div>
    </template>
    
    <div class="section">
      <a class="link" @click="goBack">返回魔魂</a>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 10px;
  background: #f5f5dc;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
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

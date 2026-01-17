<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const info = ref(null)

const fetchSacredBeast = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/sacred-beast')
    if (res.data?.ok) {
      info.value = res.data
    } else {
      // 如果API返回错误，使用默认数据
      info.value = {
        buildingLevel: 10,
        expeditionQueue: [],
        expeditionCapacity: 1,
        beasts: [],
        penCapacity: 4,
      }
    }
  } catch (err) {
    console.error('load sacred beast failed', err)
    // API调用失败时，使用默认数据
    info.value = {
      buildingLevel: 10,
      expeditionQueue: [],
      expeditionCapacity: 1,
      beasts: [],
      penCapacity: 4,
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchSacredBeast)

const buildingLevel = computed(() => info.value?.buildingLevel || info.value?.level || 10)
const expeditionQueue = computed(() => {
  const queue = info.value?.expeditionQueue || []
  const capacity = info.value?.expeditionCapacity || 1
  return {
    list: queue,
    used: queue.length,
    capacity: capacity
  }
})
const sacredBeastPen = computed(() => {
  const beasts = info.value?.beasts || []
  const capacity = info.value?.penCapacity || 4
  return {
    list: beasts,
    used: beasts.length,
    capacity: capacity
  }
})

const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')
</script>

<template>
  <div>
    <div>
      <h1>【圣兽山】简介 <a href="#" @click.prevent="goAlliance" style="color: #0066cc; text-decoration: underline;">返回</a></h1>
    </div>
    
    <div v-if="loading" style="padding: 20px;">加载中...</div>
    <template v-else-if="info">
      <div style="padding: 10px;">
        建筑等级:{{ buildingLevel }}级
      </div>
      
      <div style="padding: 10px;">
        [出战队列 ({{ expeditionQueue.used }}/{{ expeditionQueue.capacity }})]
      </div>
      
      <div style="padding: 10px;">
        <div v-if="expeditionQueue.list.length > 0">
          <div v-for="(beast, index) in expeditionQueue.list" :key="index" style="padding: 5px 0;">
            {{ index + 1 }}. {{ beast.name || '未知圣兽' }}
          </div>
        </div>
        <div v-else style="padding: 5px 0;">
          1. 空
        </div>
      </div>
      
      <div style="padding: 10px;">
        [圣兽栏({{ sacredBeastPen.used }}/{{ sacredBeastPen.capacity }})]
      </div>
      
      <div style="padding: 10px;">
        <div v-if="sacredBeastPen.list.length > 0">
          <div v-for="(beast, index) in sacredBeastPen.list" :key="index" style="padding: 5px 0;">
            {{ index + 1 }}.{{ beast.name || `圣兽${index + 1}` }}
          </div>
        </div>
        <div v-else style="padding: 20px; color: #999;">暂无圣兽</div>
      </div>
      
      <div style="padding: 10px; color: #666;">
        提示:盟战只能出战1只圣兽
      </div>
      
      <div style="padding: 10px;">
        圣兽赐福
      </div>
      
      <div style="padding: 10px;">
        <a
          href="#"
          @click.prevent="goAlliance"
          style="color: #0066cc; text-decoration: underline;"
        >返回联盟</a>
        <span> </span>
        <a
          href="#"
          @click.prevent="goHome"
          style="color: #0066cc; text-decoration: underline;"
        >返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
div {
  font-family: SimSun, "宋体", serif;
  font-size: 16px;
  line-height: 1.6;
}

h1 {
  margin: 10px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>

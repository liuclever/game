<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const info = ref(null)
const playerBeasts = ref([])
const viewMode = ref('storage') // 'bag' for 背包寄存, 'storage' for 仓库取出
const currentPage = ref(1)
const pageSize = ref(20)

const fetchStorageInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/beast-storage')
    if (res.data?.ok) {
      info.value = res.data
    }
    
    // 获取玩家幻兽列表
    const beastRes = await http.get('/beast/list')
    if (beastRes.data?.ok) {
      // 过滤掉战斗队中的幻兽（不能寄存）
      // 注意：后端API已经过滤掉了已存储的幻兽
      playerBeasts.value = (beastRes.data.beastList || []).filter(beast => !beast.inTeam)
    }
  } catch (err) {
    console.error('load storage failed', err)
  } finally {
    loading.value = false
  }
}

const storeBeast = async (beastId) => {
  try {
    const res = await http.post('/alliance/beast-storage/store', { beastId })
    if (res.data?.ok) {
      await fetchStorageInfo()
    } else {
      showMessage(res.data?.error || '寄存失败', 'error')
    }
  } catch (err) {
    console.error('store beast failed', err)
    showMessage(err.response?.data?.error || '寄存失败', 'error')
  }
}

const retrieveBeast = async (storageId) => {
  try {
    const res = await http.post('/alliance/beast-storage/retrieve', { storageId })
    if (res.data?.ok) {
      await fetchStorageInfo()
    } else {
      showMessage(res.data?.error || '取出失败', 'error')
    }
  } catch (err) {
    console.error('retrieve beast failed', err)
    showMessage(err.response?.data?.error || '取出失败', 'error')
  }
}

onMounted(fetchStorageInfo)

const beastRoomLevel = computed(() => info.value?.beastRoomLevel || info.value?.storage?.level || 1)
const storageCapacity = computed(() => {
  const storage = info.value?.storage
  return {
    used: storage?.used || 0,
    capacity: storage?.capacity || 0
  }
})

const beastPenInfo = computed(() => info.value?.beastPen || info.value?.playerBeastSlots || { used: 0, capacity: 0 })

// 仓库物品（用于取出）- 只显示当前用户的
const storageList = computed(() => {
  const list = info.value?.storageList || info.value?.storage?.items || []
  return list.filter(item => item.ownerIsSelf !== false)
})

// 当前视图的幻兽列表
const currentBeasts = computed(() => {
  if (viewMode.value === 'bag') {
    return playerBeasts.value
  } else {
    return storageList.value
  }
})

const paginatedBeasts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return currentBeasts.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(currentBeasts.value.length / pageSize.value))
})

const goToPage = (page) => {
  const pageNum = parseInt(page) || 1
  if (pageNum >= 1 && pageNum <= totalPages.value) {
    currentPage.value = pageNum
  }
}

const switchViewMode = (mode) => {
  viewMode.value = mode
  currentPage.value = 1
}

const formatBeastName = (beast) => {
  const name = beast.name || beast.nickname || `幻兽${beast.id || beast.beastId}`
  const realm = beast.realm || ''
  const level = beast.level || 0
  if (realm) {
    return `${name}-${realm}(${level}级)`
  }
  return `${name}(${level}级)`
}

const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')
</script>

<template>
  <div>
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div>
      <h1>【幻兽室】简介 <a href="#" @click.prevent="goAlliance" style="color: #0066cc; text-decoration: underline;">返回</a></h1>
      <p>帮助成员幻兽更好成长的场所,目前暂只开放幻兽寄存。</p>
    </div>
    
    <div v-if="loading" style="padding: 20px;">加载中...</div>
    <template v-else-if="info">
      <div style="padding: 10px;">
        <div>建筑等级:{{ beastRoomLevel }}级</div>
        <div>可寄存幻兽:{{ storageCapacity.capacity }}只</div>
      </div>
      
      <div style="padding: 10px;">
        【幻兽栏({{ beastPenInfo.used }}/{{ beastPenInfo.capacity }})|寄存室({{ storageCapacity.used }}/{{ storageCapacity.capacity }})】
      </div>
      
      <div style="padding: 10px;">
        <a
          href="#"
          @click.prevent="switchViewMode('bag')"
          :style="viewMode === 'bag' ? 'color: #0066cc; font-weight: bold; text-decoration: underline;' : 'color: #0066cc; text-decoration: underline;'"
        >背包寄存</a>
        <span> | </span>
        <a
          href="#"
          @click.prevent="switchViewMode('storage')"
          :style="viewMode === 'storage' ? 'color: #0066cc; font-weight: bold; text-decoration: underline;' : 'color: #0066cc; text-decoration: underline;'"
        >仓库取出</a>
      </div>
      
      <div style="padding: 10px;">
        <div v-if="paginatedBeasts.length > 0">
          <div v-for="(beast, index) in paginatedBeasts" :key="viewMode === 'bag' ? beast.id : beast.storageId" style="padding: 5px 0;">
            <span v-if="viewMode === 'bag'">
              {{ (currentPage - 1) * pageSize + index + 1 }}. {{ formatBeastName(beast) }} <a href="#" @click.prevent="storeBeast(beast.id)" style="color: #0066cc; text-decoration: underline; margin-left: 5px;">寄存</a>
            </span>
            <span v-else>
              {{ (currentPage - 1) * pageSize + index + 1 }}. {{ formatBeastName(beast) }} <a href="#" @click.prevent="retrieveBeast(beast.storageId)" style="color: #0066cc; text-decoration: underline; margin-left: 5px;">取出</a>
            </span>
          </div>
        </div>
        <div v-else style="padding: 20px; color: #999;">暂无幻兽</div>
      </div>
      
      <div v-if="totalPages > 1" style="padding: 10px;">
        <a
          href="#"
          @click.prevent="goToPage(currentPage + 1)"
          style="color: #0066cc; text-decoration: underline;"
        >下页</a>
        <span> </span>
        <a
          href="#"
          @click.prevent="goToPage(totalPages)"
          style="color: #0066cc; text-decoration: underline;"
        >末页</a>
        <span> </span>
        <span>{{ currentPage }}/{{ totalPages }}页 </span>
        <input
          type="number"
          :min="1"
          :max="totalPages"
          :value="currentPage"
          @change="goToPage($event.target.value)"
          style="width: 40px;"
        />
        <span> 跳转</span>
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
  font-size: 13px;
  line-height: 1.6;
}

h1 {
  margin: 10px 0;
  font-size: 13px;
  font-weight: bold;
}

p {
  margin: 5px 0;
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

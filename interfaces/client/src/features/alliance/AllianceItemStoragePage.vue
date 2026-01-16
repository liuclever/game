<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const info = ref(null)
const activeCategory = ref('道具')
const currentPage = ref(1)
const pageSize = ref(20)
const viewMode = ref('bag') // 'bag' for 背包寄存, 'storage' for 仓库取出

const categories = ['道具', '材料', '召唤球', '卷轴', '技能书']

const mapTypeToCategory = (type) => {
  if (!type) return '材料'
  const typeLower = (type || '').toLowerCase()
  if (typeLower.includes('consumable')) return '道具'
  if (typeLower.includes('material')) return '材料'
  if (typeLower.includes('capture') || typeLower.includes('捕捉')) return '召唤球'
  if (typeLower.includes('scroll')) return '卷轴'
  if (typeLower.includes('skill')) return '技能书'
  return '材料'
}

const fetchStorageInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/item-storage')
    if (res.data?.ok) {
      info.value = res.data
      currentPage.value = 1
    }
  } catch (err) {
    console.error('load storage failed', err)
  } finally {
    loading.value = false
  }
}

const depositItem = async (itemId, quantity) => {
  try {
    const res = await http.post('/alliance/item-storage/deposit', {
      itemId: itemId,
      quantity: quantity
    })
    if (res.data?.ok) {
      // 跳转到成功页面
      const item = bagItems.value.find(i => i.itemId === itemId)
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'true',
          message: res.data.message || '寄存成功',
          operation: 'deposit',
          itemName: item ? `${item.name} × ${quantity}` : ''
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: res.data?.error || '寄存失败',
          operation: 'deposit'
        }
      })
    }
  } catch (err) {
    console.error('deposit item failed', err)
    // 检查是否有响应数据（即使状态码是400，axios也会抛出异常，但response.data可能包含错误信息）
    const errorData = err.response?.data
    if (errorData && typeof errorData === 'object') {
      // 如果响应中有数据，使用响应中的错误信息
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: errorData.error || '寄存失败',
          operation: 'deposit'
        }
      })
    } else {
      // 网络错误或其他异常
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: '寄存失败，请稍后再试',
          operation: 'deposit'
        }
      })
    }
  }
}

const withdrawItem = async (storageId, quantity) => {
  try {
    const res = await http.post('/alliance/item-storage/withdraw', {
      storageId: storageId,
      quantity: quantity
    })
    if (res.data?.ok) {
      // 跳转到成功页面
      const item = storageItems.value.find(i => i.storageId === storageId)
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'true',
          message: res.data.message || '取出成功',
          operation: 'withdraw',
          itemName: item ? `${item.name} × ${quantity}` : ''
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: res.data?.error || '取出失败',
          operation: 'withdraw'
        }
      })
    }
  } catch (err) {
    console.error('withdraw item failed', err)
    // 检查是否有响应数据（即使状态码是400，axios也会抛出异常，但response.data可能包含错误信息）
    const errorData = err.response?.data
    if (errorData && typeof errorData === 'object') {
      // 如果响应中有数据，使用响应中的错误信息
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: errorData.error || '取出失败',
          operation: 'withdraw'
        }
      })
    } else {
      // 网络错误或其他异常
      router.push({
        path: '/alliance/item-storage/result',
        query: {
          success: 'false',
          message: '取出失败，请稍后再试',
          operation: 'withdraw'
        }
      })
    }
  }
}

onMounted(fetchStorageInfo)

// 监听路由变化，如果从结果页面返回则刷新数据
watch(() => route.query.refresh, (newVal) => {
  if (newVal === '1') {
    fetchStorageInfo()
  }
})

const storageLevel = computed(() => info.value?.storage?.level || 1)
const storageCapacity = computed(() => {
  const storage = info.value?.storage
  return {
    used: storage?.used || 0,
    capacity: storage?.capacity || 0
  }
})

const bagInfo = computed(() => info.value?.bag || null)

// 背包物品（用于寄存）
const bagItems = computed(() => info.value?.inventory || [])

// 仓库物品（用于取出）
const storageItems = computed(() => info.value?.storage?.ownItems || [])

// 当前视图的物品列表
const currentItems = computed(() => {
  if (viewMode.value === 'bag') {
    return bagItems.value
  } else {
    return storageItems.value
  }
})

const filteredItems = computed(() => {
  const items = currentItems.value
  return items.filter(item => mapTypeToCategory(item.type) === activeCategory.value)
})

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredItems.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredItems.value.length / pageSize.value))
})

const goToPage = (page) => {
  const pageNum = parseInt(page) || 1
  if (pageNum >= 1 && pageNum <= totalPages.value) {
    currentPage.value = pageNum
  }
}

const switchViewMode = (mode) => {
  viewMode.value = mode
  activeCategory.value = '道具'
  currentPage.value = 1
}

const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')
</script>

<template>
  <div>
    <div>
      <h1>【寄存仓库】</h1>
      <p>帮助成员存放暂时不用的背包物品</p>
    </div>
    
    <div v-if="loading" style="padding: 20px;">加载中...</div>
    <template v-else-if="info">
      <div style="padding: 10px;">
        <div>建筑等级:{{ storageLevel }}级</div>
        <div>可寄存物品{{ storageCapacity.capacity }}格</div>
      </div>
      
      <div style="padding: 10px;">
        【背包({{ bagInfo?.used_slots || 0 }}/{{ bagInfo?.capacity || 0 }})|仓库({{ storageCapacity.used }}/{{ storageCapacity.capacity }})】
      </div>
      
      <div style="padding: 10px;">
        <span
          v-for="(cat, index) in categories"
          :key="cat"
        >
          <a
            v-if="activeCategory !== cat"
            href="#"
            @click.prevent="activeCategory = cat; currentPage = 1"
            style="color: #0066cc; text-decoration: underline;"
          >{{ cat }}</a>
          <span v-else style="color: #0066cc; font-weight: bold;">{{ cat }}</span>
          <span v-if="index < categories.length - 1"> | </span>
        </span>
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
        <div v-if="paginatedItems.length > 0">
          <div v-for="item in paginatedItems" :key="viewMode === 'bag' ? item.itemId : item.storageId" style="padding: 5px 0;">
            <span v-if="viewMode === 'bag'">
              {{ item.name }}×{{ item.quantity }} <a href="#" @click.prevent="depositItem(item.itemId, item.quantity)" style="color: #0066cc; text-decoration: underline;">寄存</a>
            </span>
            <span v-else>
              {{ item.name }}×{{ item.quantity }} <a href="#" @click.prevent="withdrawItem(item.storageId, item.quantity)" style="color: #0066cc; text-decoration: underline;">取出</a>
            </span>
          </div>
        </div>
        <div v-else style="padding: 20px; color: #999;">暂无物品</div>
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
      
      <div style="padding: 10px; color: #666;">
        注:离开联盟后,只要加入新联盟,物品会重新显示
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

p {
  margin: 5px 0;
}
</style>

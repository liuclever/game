<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 数据状态
const loading = ref(false)
const crystalCount = ref(0)  // 拥有的灵力水晶数量
const currentSpiritPower = ref(0)  // 当前灵力
const useQuantity = ref(1)  // 使用数量

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    // 获取背包中的灵力水晶数量
    const invRes = await http.get('/inventory/list')
    if (invRes.data.ok) {
      const crystal = invRes.data.items.find(item => item.item_id === 6101)
      crystalCount.value = crystal ? crystal.quantity : 0
    }
    
    // 获取当前灵力
    const spiritRes = await http.get('/spirit/account')
    if (spiritRes.data.ok) {
      currentSpiritPower.value = spiritRes.data.account.spirit_power || 0
    }
  } catch (err) {
    console.error('加载数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

// 计算可获得的灵力
const gainedPower = computed(() => {
  return useQuantity.value * 10
})

// 使用灵力水晶
const useCrystal = async () => {
  if (useQuantity.value < 1) {
    alert('请输入有效的使用数量')
    return
  }
  
  if (useQuantity.value > crystalCount.value) {
    alert('灵力水晶数量不足')
    return
  }
  
  loading.value = true
  try {
    const res = await http.post('/spirit/consume-crystal', {
      quantity: useQuantity.value
    })
    
    if (res.data.ok) {
      alert(`成功使用${useQuantity.value}个灵力水晶，获得${res.data.gained_spirit_power}灵力`)
      // 刷新数据
      await loadData()
      useQuantity.value = 1
    } else {
      alert(res.data.error || '使用失败')
    }
  } catch (err) {
    console.error('使用灵力水晶失败:', err)
    alert('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 快捷设置数量
const setQuantity = (qty) => {
  if (qty === 'max') {
    useQuantity.value = crystalCount.value
  } else {
    useQuantity.value = Math.min(qty, crystalCount.value)
  }
}

// 返回
const goBack = () => {
  router.back()
}

const goToInventory = () => {
  router.push('/inventory')
}

const goToSpirit = () => {
  router.push('/spirit/warehouse')
}
</script>

<template>
  <div class="crystal-use-page">
    <div class="section title">【使用灵力水晶】</div>
    
    <div class="section" v-if="loading">加载中...</div>
    
    <template v-if="!loading">
      <div class="section">
        拥有灵力水晶：<span class="orange">{{ crystalCount }}</span> 个
      </div>
      
      <div class="section">
        当前灵力：<span class="blue">{{ currentSpiritPower }}</span>
      </div>
      
      <div class="section spacer">
        使用规则：1个灵力水晶 = 10灵力
      </div>
      
      <div class="section">
        使用数量：
        <input 
          type="number" 
          v-model.number="useQuantity" 
          min="1" 
          :max="crystalCount"
          class="quantity-input"
        />
      </div>
      
      <div class="section">
        <a class="link" @click="setQuantity(1)">1个</a> | 
        <a class="link" @click="setQuantity(10)">10个</a> | 
        <a class="link" @click="setQuantity(50)">50个</a> | 
        <a class="link" @click="setQuantity('max')">全部</a>
      </div>
      
      <div class="section">
        可获得灵力：<span class="green">{{ gainedPower }}</span>
      </div>
      
      <div class="section spacer">
        <button 
          class="use-btn" 
          @click="useCrystal"
          :disabled="crystalCount === 0 || loading"
        >
          确定使用
        </button>
      </div>
      
      <div class="section gray small">
        灵力用于洗练战灵的属性条，洗练可以重新随机战灵的属性值
      </div>
    </template>
    
    <div class="section spacer">
      <a class="link" @click="goToSpirit">前往战灵</a> | 
      <a class="link" @click="goToInventory">返回背包</a>
    </div>
    
    <div class="section">
      <a class="link" @click="goBack">返回上一页</a>
    </div>
  </div>
</template>

<style scoped>
.crystal-use-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
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

.orange {
  color: #ff6600;
  font-weight: bold;
}

.blue {
  color: #3366cc;
  font-weight: bold;
}

.green {
  color: #009900;
  font-weight: bold;
}

.gray {
  color: #888;
}

.small {
  font-size: 12px;
}

.quantity-input {
  width: 80px;
  font-size: 13px;
  border: 1px solid #CCCCCC;
  padding: 2px 6px;
  font-family: SimSun, "宋体", serif;
}

.use-btn {
  font-size: 13px;
  padding: 6px 20px;
  background: #ff6600;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-family: SimSun, "宋体", serif;
}

.use-btn:hover {
  background: #ff8833;
}

.use-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}
</style>

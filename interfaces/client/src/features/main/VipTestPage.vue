<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(false)
const status = ref({})
const message = ref('')

// 表单数据
const vipLevel = ref(0)
const vipExp = ref(0)
const addYuanbao = ref(1000)
const addCopper = ref(10000)
const addDiamond = ref(100)
const itemId = ref(6001)
const itemQuantity = ref(10)

const loadStatus = async () => {
  loading.value = true
  try {
    const res = await http.get('/vip-test/status')
    if (res.data?.ok) {
      status.value = res.data
      vipLevel.value = res.data.vip_level || 0
      vipExp.value = res.data.vip_exp || 0
    }
  } catch (e) {
    message.value = '加载失败: ' + e.message
  } finally {
    loading.value = false
  }
}

const setVip = async () => {
  try {
    const res = await http.post('/vip-test/set-vip', {
      vip_level: parseInt(vipLevel.value),
      vip_exp: parseInt(vipExp.value)
    })
    message.value = res.data?.message || '设置成功'
    loadStatus()
  } catch (e) {
    message.value = '设置失败: ' + e.message
  }
}

const resetDaily = async () => {
  try {
    const res = await http.post('/vip-test/reset-daily')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const resetGifts = async () => {
  try {
    const res = await http.post('/vip-test/reset-gifts')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const resetPlayer = async () => {
  if (!confirm('确定要重置玩家所有数据吗？这将清空背包、幻兽、VIP等所有数据！')) {
    return
  }
  try {
    const res = await http.post('/vip-test/reset-player')
    message.value = res.data?.message || '重置成功'
    loadStatus()
  } catch (e) {
    message.value = '重置失败: ' + e.message
  }
}

const addCurrency = async () => {
  try {
    const res = await http.post('/vip-test/add-currency', {
      yuanbao: parseInt(addYuanbao.value) || 0,
      copper: parseInt(addCopper.value) || 0,
      diamond: parseInt(addDiamond.value) || 0
    })
    message.value = res.data?.message || '添加成功'
    loadStatus()
  } catch (e) {
    message.value = '添加失败: ' + e.message
  }
}

const addItem = async () => {
  try {
    const res = await http.post('/vip-test/add-item', {
      item_id: parseInt(itemId.value),
      quantity: parseInt(itemQuantity.value)
    })
    message.value = res.data?.message || '添加成功'
  } catch (e) {
    message.value = '添加失败: ' + e.message
  }
}

const goBack = () => router.push('/')
const goVip = () => router.push('/vip')

onMounted(() => {
  loadStatus()
})
</script>

<template>
  <div class="test-page">
    <div class="section">【VIP测试面板】</div>
    
    <div v-if="message" class="section msg">{{ message }}</div>
    
    <div class="section">【当前状态】</div>
    <div class="section" v-if="loading">加载中...</div>
    <template v-else>
      <div class="section">VIP等级: {{ status.vip_level }} | VIP经验: {{ status.vip_exp }}</div>
      <div class="section">元宝: {{ status.yuanbao }} | 铜币: {{ status.copper }} | 宝石: {{ status.diamond }}</div>
      <div class="section">已领礼包: {{ status.claimed_gift_levels || '无' }}</div>
      <div class="section">今日铜币: {{ status.daily_copper_claimed ? '已领' : '未领' }}</div>
      <div class="section">招财神符今日使用: {{ status.fortune_talisman_used }}次</div>
      <div class="section">擂台今日挑战: {{ status.arena_challenge_used }}次</div>
    </template>
    
    <div class="section">【设置VIP】</div>
    <div class="section">
      等级: <input type="number" v-model="vipLevel" min="0" max="10" class="input-sm" />
      经验: <input type="number" v-model="vipExp" min="0" class="input-md" />
      <a class="link" @click="setVip">设置</a>
    </div>
    
    <div class="section">【快捷设置】</div>
    <div class="section">
      <a class="link" @click="vipLevel=1;vipExp=1;setVip()">VIP1</a> |
      <a class="link" @click="vipLevel=3;vipExp=100;setVip()">VIP3</a> |
      <a class="link" @click="vipLevel=5;vipExp=500;setVip()">VIP5</a> |
      <a class="link" @click="vipLevel=7;vipExp=2000;setVip()">VIP7</a> |
      <a class="link" @click="vipLevel=10;vipExp=20000;setVip()">VIP10</a>
    </div>
    
    <div class="section">【重置状态】</div>
    <div class="section">
      <a class="link" @click="resetDaily">重置每日状态</a> |
      <a class="link" @click="resetGifts">重置礼包领取</a> |
      <a class="link danger" @click="resetPlayer">重置玩家(危险)</a>
    </div>
    
    <div class="section">【添加货币】</div>
    <div class="section">
      元宝: <input type="number" v-model="addYuanbao" class="input-md" />
      铜币: <input type="number" v-model="addCopper" class="input-md" />
      宝石: <input type="number" v-model="addDiamond" class="input-md" />
      <a class="link" @click="addCurrency">添加</a>
    </div>
    
    <div class="section">【添加物品】</div>
    <div class="section">
      物品ID: <input type="number" v-model="itemId" class="input-md" />
      数量: <input type="number" v-model="itemQuantity" class="input-sm" />
      <a class="link" @click="addItem">添加</a>
    </div>
    <div class="section hint">
      常用物品: 6001化仙丹 6002骰子包 6003金袋 6018传送符 6019招财神符
    </div>
    
    <div class="section">
      <a class="link" @click="goVip">前往VIP页面</a> | <a class="link" @click="goBack">返回首页</a>
    </div>
  </div>
</template>

<style scoped>
.test-page {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 10px 15px;
  font-size: 17px;
  color: #333;
  font-family: 'SimSun', '宋体', serif;
  line-height: 1.8;
}
.section { margin: 4px 0; }
.link { color: #0066cc; cursor: pointer; }
.link:hover { text-decoration: underline; }
.link.danger { color: #cc0000; }
.msg { color: #006600; background: #e6ffe6; padding: 4px 8px; }
.input-sm { width: 50px; margin: 0 4px; }
.input-md { width: 80px; margin: 0 4px; }
.hint { font-size: 18px; color: #666; }
</style>

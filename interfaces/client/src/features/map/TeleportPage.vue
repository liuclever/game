<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 目标城市
const { message, messageType, showMessage } = useMessage()

const targetCity = ref('')
const teleportCount = ref(0)
const playerLevel = ref(1)
const loading = ref(true)

// 城市等级配置
const CITIES_LEVELS = {
  '林中空地': 1,
  '幻灵镇': 10,
  '定老城': 20,
  '迷雾城': 30,
  '飞龙港': 40,
  '落龙镇': 50,
  '圣龙城': 60,
  '乌托邦': 70,
}

// 城市副本配置
const CITY_DUNGEONS = {
  '林中空地': [
    { name: '森林入口', level_range: '1-2级' },
    { name: '宁静之森', level_range: '3-5级' },
    { name: '森林秘境', level_range: '6-9级' },
  ],
  '幻灵镇': [
    { name: '呼啸平原', level_range: '10-14级' },
    { name: '天罚山', level_range: '15-19级' },
  ],
  '定老城': [
    { name: '石工矿场', level_range: '20-24级' },
    { name: '幻灵湖畔', level_range: '25-29级' },
  ],
  '迷雾城': [
    { name: '回音之谷', level_range: '30-34级' },
    { name: '死亡沼泽', level_range: '35-39级' },
  ],
  '飞龙港': [
    { name: '日落海峡', level_range: '40-44级' },
    { name: '聚灵孤岛', level_range: '45-49级' },
  ],
  '落龙镇': [
    { name: '龙骨墓地', level_range: '50-54级' },
    { name: '巨龙冰原', level_range: '55-59级' },
  ],
  '圣龙城': [
    { name: '圣龙城郊', level_range: '60-64级' },
    { name: '皇城迷宫', level_range: '65-69级' },
  ],
  '乌托邦': [
    { name: '梦幻海湾', level_range: '70-74级' },
    { name: '幻光公园', level_range: '75级以上' },
  ],
}

// 当前城市的副本
const dungeons = computed(() => {
  return CITY_DUNGEONS[targetCity.value] || []
})

// 加载数据
const loadData = async () => {
  targetCity.value = route.query.city || '林中空地'
  try {
    const [countRes, infoRes] = await Promise.all([
      http.get('/map/teleport-count'),
      http.get('/map/info')
    ])
    
    if (countRes.data.ok) {
      teleportCount.value = Number(countRes.data.count ?? 0)
    }
    if (infoRes.data.ok) {
      playerLevel.value = infoRes.data.level || 1
    }
  } catch (e) {
    console.error('加载数据失败', e)
  } finally {
    loading.value = false
  }
}

// 进入副本
const enterDungeon = (dungeon) => {
  showMessage(`进入副本: ${dungeon.name} 功能待实现`, 'info')
}

// 传送到该城市
const doTeleport = async () => {
  const minLevel = CITIES_LEVELS[targetCity.value] || 1
  if (playerLevel.value < minLevel) {
    showMessage(`等级不足，需要${minLevel}级才能传送到${targetCity.value}`, 'error')
    return
  }

  if (teleportCount.value <= 0) {
    showMessage('传送符不足！', 'error')
    return
  }
  
  try {
    const res = await http.post('/map/teleport', { city: targetCity.value })
    if (res.data.ok) {
      router.push('/map/teleport-success')
    } else {
      showMessage(res.data.error, 'error')
    }
  } catch (e) {
    console.error('传送失败', e)
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 返回地图首页
const goMap = () => {
  router.push('/map')
}

// 返回游戏首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="teleport-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 标题 -->
    <div class="section title">【召唤大陆地图】</div>
    
    <!-- 传送位置 -->
    <div class="section">
      传送位置:<span class="bold">{{ targetCity }}</span>
    </div>
    
    <!-- 副本地图 -->
    <div class="section">副本地图:</div>
    <div v-for="d in dungeons" :key="d.name" class="section">
      <a class="link" @click="enterDungeon(d)">{{ d.name }}</a> ({{ d.level_range }})
    </div>
    
    <!-- 传送信息 -->
    <div class="section">
      使用传送符传送可以马上到达目的地 
      <a class="link" @click="doTeleport">传送</a>
    </div>
    <div class="section" v-if="teleportCount > 0">
      现有传送符{{ teleportCount }}
    </div>
    
    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goMap">返回地图首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.teleport-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 6px;
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

.bold {
  font-weight: bold;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
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

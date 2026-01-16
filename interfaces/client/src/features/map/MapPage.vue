<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 地图数据
const currentLocation = ref('落龙镇')
const dungeons = ref([])
const cities = ref([])
const loading = ref(true)
const moving = ref(false)
const movingTo = ref('')
const remainingSeconds = ref(0)
let moveTimer = null

// 城市配置
const CITIES = [
  { name: '林中空地', level_range: '1~9级', min_level: 1, max_level: 9 },
  { name: '幻灵镇', level_range: '10~19级', min_level: 10, max_level: 19 },
  { name: '定老城', level_range: '20~29级', min_level: 20, max_level: 29 },
  { name: '迷雾城', level_range: '30~39级', min_level: 30, max_level: 39 },
  { name: '飞龙港', level_range: '40~49级', min_level: 40, max_level: 49 },
  { name: '落龙镇', level_range: '50~59级', min_level: 50, max_level: 59 },
  { name: '圣龙城', level_range: '60~69级', min_level: 60, max_level: 69 },
  { name: '乌托邦', level_range: '70~79级', min_level: 70, max_level: 79 },
]

// 副本配置
const DUNGEONS = [
  // 林中空地
  { name: '森林入口', level_range: '1-2级', city: '林中空地' },
  { name: '宁静之森', level_range: '3-5级', city: '林中空地' },
  { name: '森林秘境', level_range: '6-9级', city: '林中空地' },
  // 幻灵镇
  { name: '呼啸平原', level_range: '10-14级', city: '幻灵镇' },
  { name: '天罚山', level_range: '15-19级', city: '幻灵镇' },
  // 定老城
  { name: '石工矿场', level_range: '20-24级', city: '定老城' },
  { name: '幻灵湖畔', level_range: '25-29级', city: '定老城' },
  // 迷雾城
  { name: '回音之谷', level_range: '30-34级', city: '迷雾城' },
  { name: '死亡沼泽', level_range: '35-39级', city: '迷雾城' },
  // 飞龙港
  { name: '日落海峡', level_range: '40-44级', city: '飞龙港' },
  { name: '聚灵孤岛', level_range: '45-49级', city: '飞龙港' },
  // 落龙镇
  { name: '龙骨墓地', level_range: '50-54级', city: '落龙镇' },
  { name: '巨龙冰原', level_range: '55-59级', city: '落龙镇' },
  // 圣龙城
  { name: '圣龙城郊', level_range: '60-64级', city: '圣龙城' },
  { name: '皇城迷宫', level_range: '65-69级', city: '圣龙城' },
  // 乌托邦
  { name: '梦幻海湾', level_range: '70-74级', city: '乌托邦' },
  { name: '幻光公园', level_range: '75级以上', city: '乌托邦' },
]

// 玩家等级
const playerLevel = ref(1)

// 加载地图数据
const loadMapData = async () => {
  try {
    const res = await http.get('/map/info')
    if (res.data.ok) {
      currentLocation.value = res.data.current_location || '落龙镇'
      playerLevel.value = res.data.level || 1
      moving.value = !!res.data.moving
      movingTo.value = res.data.moving_to || ''
      remainingSeconds.value = Number(res.data.remaining_seconds || 0)

      if (moveTimer) {
        clearInterval(moveTimer)
        moveTimer = null
      }
      if (moving.value && remainingSeconds.value > 0) {
        moveTimer = setInterval(() => {
          if (remainingSeconds.value > 0) {
            remainingSeconds.value -= 1
          }
          if (remainingSeconds.value <= 0) {
            clearInterval(moveTimer)
            moveTimer = null
            loadMapData()
          }
        }, 1000)
      }
    }
  } catch (e) {
    console.error('加载地图数据失败', e)
  } finally {
    loading.value = false
  }
}

// 获取当前城市的副本
const currentDungeons = computed(() => {
  return DUNGEONS.filter(d => d.city === currentLocation.value)
})

// 判断城市是否可移动（相邻城市）
const canMove = (cityName) => {
  const currentIndex = CITIES.findIndex(c => c.name === currentLocation.value)
  const targetIndex = CITIES.findIndex(c => c.name === cityName)
  return Math.abs(currentIndex - targetIndex) === 1
}

// 判断是否是当前城市
const isCurrentCity = (cityName) => {
  return cityName === currentLocation.value
}

// 移动到城市（免费，只能移动到相邻城市）
const moveToCity = async (cityName) => {
  if (moving.value) {
    alert(`移动中，无法再次移动（剩余${remainingSeconds.value}秒）`)
    return
  }
  const city = CITIES.find(c => c.name === cityName)
  if (city && playerLevel.value < city.min_level) {
    alert(`等级不足，需要${city.min_level}级才能前往${cityName}`)
    return
  }
  try {
    const res = await http.post('/map/move', { city: cityName })
    if (res.data.ok) {
      await loadMapData()
      if (res.data.message) {
        alert(res.data.message)
      }
    } else {
      alert(res.data.error)
    }
  } catch (e) {
    console.error('移动失败', e)
  }
}

// 传送到城市（跳转到传送页面）
const teleportToCity = (cityName) => {
  if (moving.value) {
    alert(`移动中，无法传送（剩余${remainingSeconds.value}秒）`)
    return
  }
  router.push({
    path: '/map/teleport',
    query: { city: cityName }
  })
}

// 进入副本
const enterDungeon = (dungeon) => {
  if (moving.value) {
    alert(`移动中，无法挑战副本（剩余${remainingSeconds.value}秒）`)
    return
  }
  router.push(`/dungeon/challenge/${encodeURIComponent(dungeon.name)}`)
}

// 重置副本
const resetDungeon = async (dungeon) => {
  if (moving.value) {
    alert(`移动中，无法重置副本（剩余${remainingSeconds.value}秒）`)
    return
  }
  if (!confirm(`确认重置副本【${dungeon.name}】？`)) {
    return
  }
  try {
    const res = await http.post('/dungeon/reset', { dungeon_name: dungeon.name })
    if (res.data.ok) {
      alert(res.data.message || '重置成功')
    } else {
      alert(res.data.error || '重置失败')
    }
  } catch (e) {
    console.error('重置失败', e)
    alert('重置失败')
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 点击链接
const handleLink = (name) => {
  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '地图': '/map',
    '擂台': '/arena',
    '闯塔': '/tower',
    '排行': '/ranking',
    '召唤之王挑战赛': '/king',
    '商城': '/shop',
    '兑换': '/exchange',
    '图鉴': '/handbook',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    alert(`${name} 功能待实现`)
  }
}

onMounted(() => {
  loadMapData()
})

onUnmounted(() => {
  if (moveTimer) {
    clearInterval(moveTimer)
    moveTimer = null
  }
})
</script>

<template>
  <div class="map-page">
    <!-- 标题 -->
    <div class="section title">【召唤大陆地图】</div>
    
    <!-- 当前位置 -->
    <div class="section">
      当前位置:<span class="bold">{{ currentLocation }}</span>
    </div>

    <div class="section" v-if="moving">
      移动中:<span class="bold">{{ movingTo }}</span>
      <span class="gray">（剩余{{ remainingSeconds }}秒）</span>
    </div>
    
    <!-- 副本地图 -->
    <div class="section">副本地图:</div>
    <template v-if="currentDungeons.length > 0">
      <div v-for="d in currentDungeons" :key="d.name" class="section indent">
        <a class="link" @click="enterDungeon(d)">{{ d.name }}</a> ({{ d.level_range }}) 
        <a class="link" @click="enterDungeon(d)">挑战</a>
        <a class="link" @click="resetDungeon(d)">重置</a>
      </div>
    </template>
    <div v-else class="section indent gray">当前城市没有副本</div>
    
    <!-- 临近城市 -->
    <div class="section title-small">[临近城市]</div>
    <div v-for="city in CITIES" :key="city.name" class="section">
      <a class="link" :class="{ 'current': isCurrentCity(city.name) }">{{ city.name }}</a> 
      ({{ city.level_range }}) 
      <template v-if="isCurrentCity(city.name)">
        <span class="gray">你在这里</span>
      </template>
      <template v-else>
        <a class="link" @click="moveToCity(city.name)">移动</a>
        <a class="link" @click="teleportToCity(city.name)">传送</a>
      </template>
    </div>
    
    <!-- 皇城 -->
    <div class="section spacer">
      皇城:<span class="link readonly">召唤之王挑战赛</span>
    </div>
    
    <!-- 导航菜单 -->
    <div class="section">
      <a class="link" @click="handleLink('幻兽')">幻兽</a>. 
      <a class="link" @click="handleLink('背包')">背包</a>. 
      <a class="link" @click="handleLink('商城')">商城</a>. 
      <a class="link" @click="handleLink('赞助')">赞助</a>. 
      <a class="link" @click="handleLink('礼包')">礼包</a>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('联盟')">联盟</a>. 
      <a class="link" @click="handleLink('盟战')">盟战</a>. 
      <a class="link" @click="handleLink('地图')">地图</a>. 
      <span class="link readonly">天赋</span>. 
      <a class="link" @click="handleLink('化仙')">化仙</a>
    </div>
    <div class="section">
      <span class="link readonly">切磋</span>. 
      <a class="link" @click="handleLink('闯塔')">闯塔</a>. 
      <a class="link" @click="handleLink('战场')">战场</a>. 
      <a class="link" @click="handleLink('擂台')">擂台</a>. 
      <span class="link readonly">坐骑</span>
    </div>
    <div class="section">
      <a class="link" @click="router.push('/tree')">古树</a>. 
      <a class="link" @click="handleLink('排行')">排行</a>. 
      <span class="link readonly">成就</span>. 
      <a class="link" @click="handleLink('图鉴')">图鉴</a>. 
      <span class="link readonly">攻略</span>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('兑换')">兑换</a>. 
      <span class="link readonly">签到</span>. 
      <span class="link readonly">论坛</span>. 
      <a class="link" @click="handleLink('VIP')">VIP</a>. 
      <span class="link readonly">安全锁</span>
    </div>
    
    <!-- 返回首页 -->
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.map-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
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

.title-small {
  margin-top: 12px;
  margin-bottom: 4px;
}

.indent {
  padding-left: 12px;
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

.link.readonly {
  color: #000000;
  cursor: default;
  pointer-events: none;
  text-decoration: none;
}

.link.readonly:hover {
  text-decoration: none;
}

.link.current {
  color: #CC6600;
  font-weight: bold;
}

.bold {
  font-weight: bold;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

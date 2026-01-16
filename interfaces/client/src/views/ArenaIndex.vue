<template>
  <div class="arena-index-page">
    <!-- 标题 -->
    <div class="section title">【常用功能】</div>

    <!-- 功能列表 -->
    <div class="section indent">
      【<a class="link" @click="router.push('/cultivation')">修行</a>| 竞技| <a class="link" @click="router.push('/tasks/rewards')">任务</a>| 师徒】
    </div>

    <!-- 幻兽信息 -->
    <div class="section">
      幻兽: <span v-if="beasts.length === 0">暂无出战幻兽</span>
      <span v-else v-for="(beast, idx) in beasts" :key="idx">
        <a class="link" @click="viewBeast(beast.id)">{{ beast.name }}</a>
        <span v-if="idx < beasts.length - 1"> · </span>
      </span>
    </div>

    <div class="section">
      综合战力:{{ totalPower }}
    </div>

    <!-- 挑战 -->
    <div class="section">
      挑战: {{ kingInfo.area }}.{{ kingInfo.rank }}名 <a class="link" @click="router.push('/king')">挑战</a>
    </div>

    <!-- 切磋 -->
    <div class="section">
      切磋:今日胜利:50/50
    </div>

    <!-- 连胜竞技场 -->
    <div class="section">
      <a class="link" @click="router.push('/arena/streak')">连胜竞技场</a>:连胜50
    </div>

    <div class="section indent">
      <div v-if="loading">加载中...</div>
      <div v-else-if="opponents.length === 0">暂无对手</div>
      <div v-else v-for="(opp, idx) in opponents" :key="idx">
        <a class="link" @click="viewPlayer(opp.user_id)">{{ opp.nickname }}</a> ({{ opp.level }}级). 
        <a class="link" @click="spar(opp.user_id)">切磋</a>
        <br v-if="idx < opponents.length - 1">
      </div>
    </div>

    <!-- 战场 -->
    <div class="section">
      战场: 已报名蓝队 <a class="link" @click="router.push('/battlefield')">查看</a>
    </div>

    <!-- 擂台 -->
    <div class="section">
      擂台:2星以上召唤师的舞台
    </div>

    <!-- 闯塔 -->
    <div class="section">
      闯塔: 今日闯塔:4/4 <a class="link" @click="router.push('/tower')">查看</a>
    </div>

    <!-- 盟战 -->
    <div class="section">
      盟战:周六20点开战
    </div>

    <!-- 分隔线 -->
    <div class="section"></div>

    <!-- 皇城 -->
    <div class="section">
      皇城:<a class="link" @click="router.push('/king')">召唤之王挑战赛</a>
    </div>

    <!-- 底部链接 - 和主页保持一致 -->
    <div class="section">
      <a class="link" @click="router.push('/beast')">幻兽</a>. 
      <a class="link" @click="router.push('/inventory')">背包</a>. 
      <a class="link" @click="router.push('/shop')">商城</a>. 
      <a class="link" @click="router.push('/gifts')">赞助</a>. 
      <a class="link" @click="router.push('/gifts')">礼包</a>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/alliance')">联盟</a>. 
      <a class="link" @click="router.push('/battlefield')">盟战</a>. 
      <a class="link" @click="router.push('/map')">地图</a>. 
      <span class="link readonly">天赋</span>. 
      <a class="link" @click="router.push('/huaxian')">化仙</a>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/friend')">切磋</a>. 
      <a class="link" @click="router.push('/tower')">闯塔</a>. 
      <a class="link" @click="router.push('/battlefield')">战场</a>. 
      <a class="link" @click="router.push('/arena')">擂台</a>. 
      <span class="link readonly">坐骑</span>
    </div>

    <div class="section">
      <span class="link readonly">古树</span>. 
      <a class="link" @click="router.push('/ranking')">排行</a>. 
      <span class="link readonly">成就</span>. 
      <a class="link" @click="router.push('/handbook')">图鉴</a>. 
      <span class="link readonly">攻略</span>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/exchange')">兑换</a>. 
      <a class="link" @click="router.push('/signin')">签到</a>. 
      <span class="link readonly">论坛</span>. 
      <a class="link" @click="router.push('/vip')">VIP</a>. 
      <span class="link readonly">安全锁</span>
    </div>

    <!-- 返回 -->
    <div class="section">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const beasts = ref([])
const opponents = ref([])
const loading = ref(false)
const totalPower = ref(0)

// 召唤之王信息
const kingInfo = ref({
  area: '',
  rank: 0
})

// 加载召唤之王信息
const loadKingInfo = async () => {
  try {
    const res = await http.get('/king/info')
    if (res.data.ok) {
      kingInfo.value = {
        area: res.data.areaName || '1赛区',
        rank: res.data.myRank || 0
      }
    }
  } catch (e) {
    console.error('加载召唤之王信息失败', e)
  }
}

// 加载玩家出战幻兽
const loadBeasts = async () => {
  try {
    const res = await http.get('/beast/team')
    if (res.data.ok) {
      const teamBeasts = res.data.beasts || []
      // 保存完整的幻兽信息（包含ID）
      beasts.value = teamBeasts.map(b => {
        const realmName = ['', '凡界', '人界', '地界', '天界', '神界'][b.realm] || ''
        return {
          id: b.id,
          name: `${b.name}-${realmName}`
        }
      })
      
      // 计算总战力（使用接口返回的战力）
      totalPower.value = teamBeasts.reduce((sum, b) => sum + (b.power || 0), 0)
    }
  } catch (e) {
    console.error('加载幻兽失败', e)
    beasts.value = []
    totalPower.value = 0
  }
}

// 查看幻兽详情
const viewBeast = (beastId) => {
  if (beastId) {
    router.push(`/beast/${beastId}`)
  }
}

// 加载连胜竞技场对手列表
const loadOpponents = async () => {
  loading.value = true
  try {
    const res = await http.get('/arena-streak/info')
    if (res.data.ok) {
      // 只取前2个对手
      opponents.value = (res.data.opponents || []).slice(0, 2)
    }
  } catch (e) {
    console.error('加载对手列表失败', e)
  } finally {
    loading.value = false
  }
}

// 查看玩家信息
const viewPlayer = (userId) => {
  if (userId) {
    router.push({ path: '/player/detail', query: { id: userId } })
  }
}

// 切磋（跳转到连胜竞技场进行战斗）
const spar = (opponentId) => {
  router.push({ path: '/arena/streak', query: { opponent: opponentId } })
}

onMounted(() => {
  loadBeasts()
  loadOpponents()
  loadKingInfo()
})
</script>

<style scoped>
.arena-index-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.section.title {
  font-weight: bold;
  margin: 12px 0;
}

.section.indent {
  margin-left: 20px;
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
</style>

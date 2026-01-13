<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 当前场次类型
const { message, messageType, showMessage } = useMessage()

const currentType = ref('normal')

// 玩家等级信息
const playerLevel = ref(1)
const playerNickname = ref('')
const rankName = ref('见习')
const arenaName = ref('擂台')
const arenaTypeName = ref('普通场')
const canArena = ref(false)
const levelMessage = ref('')

// 球的信息
const ballName = ref('捕捉球')
const ballCount = ref(0)

// 挑战次数
const remainingChallenges = ref(10)
const dailyChallengeLimit = ref(10)

// 擂台信息
const arenaInfo = ref({
  champion: null,
  championUserId: null,
  consecutiveWins: 0,
  prizePool: 0,
  isChampion: false,
  isEmpty: true,
})

// 操作状态
const loading = ref(false)
const resultMessage = ref('')

// 动态类型
const dynamicType = ref('arena')

// 擂台动态
const arenaDynamics = ref([])

// 加载擂台信息
const loadArenaInfo = async () => {
  try {
    const res = await http.get(`/arena/info?type=${currentType.value}`)
    if (res.data.ok) {
      playerLevel.value = res.data.playerLevel
      playerNickname.value = res.data.playerNickname
      rankName.value = res.data.rankName
      canArena.value = res.data.canArena
      
      if (res.data.canArena) {
        arenaName.value = res.data.arenaName
        arenaTypeName.value = res.data.arenaTypeName
        ballName.value = res.data.ballName
        ballCount.value = res.data.ballCount
        remainingChallenges.value = res.data.remainingChallenges ?? 10
        dailyChallengeLimit.value = res.data.dailyChallengeLimit ?? 10
        arenaInfo.value = res.data.arena || {
          champion: null,
          consecutiveWins: 0,
          prizePool: 0,
          isChampion: false,
          isEmpty: true,
        }


      } else {
        levelMessage.value = res.data.message
      }
    }
  } catch (e) {
    console.error('加载擂台信息失败', e)
  }
}

// 加载动态
const loadDynamics = async () => {
  try {
    const res = await http.get(`/arena/dynamics?type=${dynamicType.value}`)
    if (res.data.ok) {
      arenaDynamics.value = res.data.dynamics
    }
  } catch (e) {
    console.error('加载擂台动态失败', e)
  }
}

// 切换场次类型
const switchType = (type) => {
  currentType.value = type
  loadArenaInfo()
}

// 切换动态类型
const switchDynamic = (type) => {
  dynamicType.value = type
  loadDynamics()
}

// 查看战报
const viewBattle = (dynamic) => {
  if (!dynamic || !dynamic.id) return
  router.push(`/arena/battle?id=${dynamic.id}`)
}

// 查看英豪榜
const viewRanking = () => {
  router.push('/ranking?type=arena')
}

// 查看简介
const viewIntro = () => {
  router.push('/arena/intro')
}

// 查看玩家信息（擂主 / 动态里的玩家）
const viewPlayer = (userId) => {
  if (userId) {
    router.push(`/player/profile?id=${userId}`)
  }
}

// 占领擂台
const occupyArena = async () => {
  if (loading.value) return
  if (ballCount.value < 1) {
    showMessage(`${ballName.value}不足，请先购买！`, 'error')
    return
  }
  
  // 已移除确认提示
  
  loading.value = true
  resultMessage.value = ''
  try {
    const res = await http.post('/arena/occupy', { type: currentType.value })
    if (res.data.ok) {
      resultMessage.value = res.data.message
      loadArenaInfo()
      loadDynamics() // 刷新擂台动态
    } else {
      showMessage(res.data.error || '占领失败', 'error')
    }
  } catch (e) {
    showMessage('占领失败：' + e.message, 'error')
  } finally {
    loading.value = false
  }
}

// 挑战擂主
const challenge = async () => {
  if (loading.value) return
  if (ballCount.value < 1) {
    showMessage(`${ballName.value}不足，请先购买！`, 'error')
    return
  }
  
  // 已移除确认提示
  
  loading.value = true
  resultMessage.value = ''
  try {
    const res = await http.post('/arena/challenge', { type: currentType.value })
    if (res.data.ok) {
      resultMessage.value = res.data.message
      loadArenaInfo()
      loadDynamics() // 刷新擂台动态
    } else {
      showMessage(res.data.error || '挑战失败', 'error')
    }
  } catch (e) {
    showMessage('挑战失败：' + e.message, 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadArenaInfo()
  loadDynamics()
})

// 点击链接
const handleLink = (name) => {
  const routes = {
    '幻兽': '/beast',
    '背包': '/inventory',
    '商城': '/shop',
    '地图': '/map',
    '闯塔': '/tower',
    '擂台': '/arena',
    '排行': '/ranking',
    '召唤之王挑战赛': '/king',
    '兑换': '/exchange',
    'VIP': '/vip',
    '提升': '/vip',
    '活力': '/vip',
    '图鉴': '/handbook',
    '签到': '/signin',
    '赞助': '/sponsor',
    '礼包': '/gifts',
    '联盟': '/alliance',
    '盟战': '/alliance/war',
    '战场': '/battlefield',
    '化仙': '/huaxian',
  }
  if (routes[name]) {
    router.push(routes[name])
  } else {
    showMessage(`点击了: ${name}`, 'info')
  }
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="arena-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 标题 -->
    <div class="section title">
      【{{ arenaName }}】 
      <a class="link" @click="viewRanking">英豪榜</a> | 
      <a class="link" @click="viewIntro">简介</a>
    </div>

    <!-- 等级不足提示 -->
    <template v-if="!canArena">
      <div class="section">
        您当前等级：{{ playerLevel }}级（{{ rankName }}）
      </div>
      <div class="section warning">
        {{ levelMessage }}
      </div>
      <div class="section">
        快去升级吧！达到20级即可参与<span class="orange">黄阶擂台</span>
      </div>
    </template>

    <!-- 可以参与擂台 -->
    <template v-else>
      <!-- 场次切换 -->
      <div class="section">
        <a 
          class="link" 
          :class="{ active: currentType === 'normal' }"
          @click="switchType('normal')"
        >普通场</a> | 
        <a 
          class="link"
          :class="{ active: currentType === 'gold' }"
          @click="switchType('gold')"
        >黄金场</a>
        <span class="gray">（消耗：{{ ballName }}）</span>
      </div>

      <!-- 球的数量 -->
      <div class="section">
        你的{{ ballName }}：<span class="orange">{{ ballCount }}</span>个
      </div>

      <!-- 擂台信息 -->
      <template v-if="arenaInfo.isEmpty">
        <div class="section">
          当前擂主：<span class="gray">空置</span>
        </div>
        <div class="section">
          擂台奖池：<span class="orange">{{ arenaInfo.prizePool }}</span>个{{ ballName }}
        </div>
        <div class="section">
          <a class="link action" @click="occupyArena" :class="{ disabled: loading }">
            {{ loading ? '占领中...' : '占领擂台' }}
          </a>
          <span class="gray">（消耗1个{{ ballName }}）</span>
        </div>
      </template>
      <template v-else>
        <div class="section">
          当前擂主：
          <a class="link username" @click="viewPlayer(arenaInfo.championUserId)">{{ arenaInfo.champion }}</a>
        </div>
        <div class="section">
          累计连胜：{{ arenaInfo.consecutiveWins }}场
        </div>
        <div class="section">
          擂台奖池：<span class="orange">{{ arenaInfo.prizePool }}</span>个{{ ballName }}
        </div>
        <div class="section" v-if="arenaInfo.isChampion">
          你环视台下，寂寞的等待着<span class="orange">下一个挑战者</span>
        </div>
        <div class="section" v-else>
          <a class="link action" @click="challenge" :class="{ disabled: loading }">
            {{ loading ? '挑战中...' : '挑战擂主' }}
          </a>
          <span class="gray">（消耗1个{{ ballName }}）</span>
        </div>
      </template>

      <!-- 挑战次数 -->
      <div class="section">
        今日剩余挑战次数：<span class="orange">{{ remainingChallenges }}</span>/{{ dailyChallengeLimit }}
      </div>

      <!-- 战斗结果 -->
      <div class="section result" v-if="resultMessage">
        {{ resultMessage }}
      </div>

    <!-- 擂台规则 -->
    <div class="section title2">【擂台规则】</div>
    <div class="section gray">
      · 普通场消耗捕捉球，黄金场消耗强力捕捉球
    </div>
    <div class="section gray">
      · 挑战消耗的球进入奖池，打赢获得全部奖池
    </div>
    <div class="section gray">
      · 擂主连胜10场可领走奖池并下台
    </div>

    <!-- 动态切换 -->
    <div class="section title2">
      【<a 
        class="link" 
        :class="{ active: dynamicType === 'arena' }"
        @click="switchDynamic('arena')"
      >擂台动态</a> 
      <a 
        class="link"
        :class="{ active: dynamicType === 'personal' }"
        @click="switchDynamic('personal')"
      >个人动态</a>】
    </div>

    <!-- 动态列表 -->
    <div v-for="(d, index) in arenaDynamics" :key="index" class="section">
      <span class="gray">({{ d.time }})</span> 
      <a class="link username" @click="viewPlayer(d.playerId)">{{ d.player }}</a> 
      {{ d.action }}
      <template v-if="d.opponent">
        <a class="link username" @click="viewPlayer(d.opponentId)">{{ d.opponent }}</a>
      </template>
      <template v-if="d.extra">
        <span class="orange"> {{ d.extra }}</span>
      </template>
      <template v-if="d.hasDetail">
        <a class="link" @click="viewBattle(d)"> 查看</a>
      </template>
    </div>
    </template>

    <!-- 皇城 -->
    <div class="section spacer">
      皇城:<a class="link" @click="handleLink('召唤之王挑战赛')">召唤之王挑战赛</a>. 
      <a class="link" @click="router.push('/arena/streak')">连胜竞技场</a>
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
      <a class="link" @click="router.push('/spar/report')">切磋</a>. 
      <a class="link" @click="handleLink('闯塔')">闯塔</a>. 
      <a class="link" @click="handleLink('战场')">战场</a>. 
      <a class="link active">擂台</a>. 
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
      <a class="link" @click="handleLink('签到')">签到</a>. 
      <span class="link readonly">论坛</span>. 
      <a class="link" @click="handleLink('VIP')">VIP</a>. 
      <span class="link readonly">安全锁</span>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.arena-page {
  padding: 10px;
  font-size: 14px;
  background: #f5f5dc;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
  line-height: 1.6;
}

.title {
  font-weight: bold;
  color: #333;
}

.title2 {
  font-weight: bold;
  margin-top: 15px;
  color: #333;
}

.link {
  color: #1e90ff;
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

.link.active {
  color: #ff6600;
  font-weight: bold;
}

.link.username {
  color: #1e90ff;
}

.link.orange {
  color: #ff6600;
}

.gray {
  color: #888;
}

.orange {
  color: #ff6600;
}

.green {
  color: #228b22;
}

.spacer {
  margin-top: 20px;
}

.warning {
  color: #cc0000;
  font-weight: bold;
}

.link.action {
  color: #228b22;
  font-weight: bold;
}

.link.action:hover {
  color: #1e8b1e;
}

.link.disabled {
  color: #999;
  pointer-events: none;
}

.result {
  color: #228b22;
  font-weight: bold;
  padding: 8px;
  background: #f0fff0;
  border: 1px solid #228b22;
  border-radius: 4px;
  margin: 10px 0;
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

<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const player = ref(null)
const currentUserId = ref(null)

const isOtherPlayer = computed(() => {
  // 如果没有加载到玩家信息，返回 false
  if (!player.value) return false
  // 如果没有获取到当前用户ID（未登录），也显示切磋按钮
  if (!currentUserId.value) return true
  // 如果是查看其他玩家，显示切磋按钮
  return player.value.id !== currentUserId.value
})

const formatReputation = (prestige, required) => {
  const cur = Number(prestige || 0)
  const target = required ?? '已满级'
  return `${cur}/${target}`
}

const vipConfig = ref(null)

const loadVipConfig = async () => {
  try {
    const res = await http.get('/configs/vip_privileges.json')
    vipConfig.value = res.data
  } catch (e) {
    console.error('加载VIP配置失败', e)
  }
}

const formatEnergy = (energy, vipLevel = 0) => {
  const cur = Number(energy || 0)
  let max = 100
  if (vipConfig.value && vipConfig.value.vip_levels) {
    const levelData = vipConfig.value.vip_levels.find((v) => v.level === vipLevel)
    if (levelData && levelData.privileges) {
      max = levelData.privileges.vitality_max
    }
  }
  return `${cur}/${max}`
}

const formatCrystalTower = (spiritStone) => {
  const cur = Number(spiritStone || 0)
  // 先按首页示例：/100（后续可接入真实上限）
  return `${cur}/100`
}

const computeBattlePower = (beasts) => {
  return (beasts || []).reduce((sum, b) => sum + Number(b?.combat_power || 0), 0)
}

// 加载玩家信息（按ID）
const loadPrestigeRequirement = async () => {
  try {
    const res = await http.get('/cultivation/status')
    if (res.data && res.data.ok && player.value) {
      const required = res.data.prestige_required
      player.value.prestigeRequired = required
      player.value.reputation = formatReputation(player.value.prestige, required)
    }
  } catch (e) {
    console.error('加载声望阈值失败', e)
  }
}

const loadPlayerInfo = async () => {
  const playerId = String(route.query.id || '').trim()
  if (!playerId) {
    loading.value = false
    player.value = null
    showMessage('缺少玩家ID', 'error')
    return
  }

  loading.value = true
  try {
    // 复用后端接口：/api/player/profile?id=xxx
    const res = await http.get(`/player/profile?id=${encodeURIComponent(playerId)}`)
    if (res.data && res.data.ok) {
      const p = res.data.player || {}
      const beasts = res.data.beasts || []
      const dynamics = res.data.dynamics || []
      const lv = Number(p.level || 1)
      const vipLevel = Number(p.vip_level || 0)
      const prestige = Number(p.prestige || 0)

      player.value = {
        id: p.user_id,
        nickname: p.nickname || '',
        gender: p.gender || '男',
        level: lv,
        levelTitle: `${lv}级召唤师`,
        vipLevel: vipLevel,

        charmLevel: p.charm_level || 1,
        charmExp: `${Number(p.charm || 0)}/1000`,

        prestige,
        prestigeRequired: null,
        reputation: formatReputation(prestige, null),
        energyRaw: Number(p.energy || 0),
        crystalTower: formatCrystalTower(p.spirit_stone),
        gold: Number(p.gold || 0),

        beasts,
        battlePower: computeBattlePower(beasts),
        battleRecord: `${Number(p.wins || 0)}/${Number(p.battles || 0)}`,
        challengeRank: `${Number(p.arena_rank || 1)}赛区.${Number(p.arena_position || 1)}名`,
        status: `${p.status || '落龙镇'} (${p.status_detail || '修行中'})`,
        mount: p.mount || '未携带',
        pvpTeam: '切磋',
        talent: '查看',
        alliance: p.alliance || '未加入',
        allianceLevel: Number(p.alliance_level || 1),
        sealTitle: p.title || p.rank_name || '',

        dynamics: dynamics.map((d) => ({
          time: d.time || '',
          content: d.text || '',
          hasDetail: false,
        })),
      }
      await loadPrestigeRequirement()
    } else {
      player.value = null
      showMessage(res.data?.error || '加载失败', 'error')
    }
  } catch (e) {
    console.error('加载玩家信息失败', e)
    player.value = null
    const msg = e?.response?.data?.error || '加载失败'
    showMessage(msg, 'info')
  } finally {
    loading.value = false
  }
}

// 写信
const sendMessage = () => {
  if (!player.value?.id) return
  router.push({ 
    path: '/mail/chat', 
    query: { target_id: player.value.id, name: player.value.nickname } 
  })
}

// 加为好友
const addingFriend = ref(false)
const addFriend = async () => {
  if (!player.value?.id) return
  if (addingFriend.value) return
  
  addingFriend.value = true
  try {
    const res = await http.post('/mail/friend-request/send', { target_id: player.value.id })
    if (res.data.ok) {
      showMessage(res.data.message || '好友请求已发送', 'info')
    } else {
      showMessage(res.data.error || '发送失败', 'error')
    }
  } catch (e) {
    console.error('发送好友请求失败', e)
    showMessage(e?.response?.data?.error || '发送失败', 'error')
  } finally {
    addingFriend.value = false
  }
}

// 拉黑
const blockPlayer = () => {
  showMessage('拉黑玩家', 'info')
}

// 灌注
const infusing = ref(false)
const doInfuse = async () => {
  if (!player.value?.id) return
  if (infusing.value) return
  
  infusing.value = true
  try {
    const res = await http.post('/player/infuse', { target_id: player.value.id })
    if (res.data.ok) {
      showMessage(res.data.message, 'success')
      loadPlayerInfo()
    } else {
      showMessage(res.data.error || '灌注失败', 'error')
    }
  } catch (e) {
    console.error('灌注失败', e)
    showMessage(e?.response?.data?.error || '灌注失败', 'error')
  } finally {
    infusing.value = false
  }
}

// 切磋
const sparring = ref(false)
const challenge = async () => {
  if (!player.value?.id) return
  if (sparring.value) return
  
  sparring.value = true
  try {
    const res = await http.post('/player/spar', { target_id: player.value.id })
    if (res.data.ok) {
      router.push({
        path: '/spar/report',
        query: { data: JSON.stringify(res.data.battle) }
      })
    } else {
      showMessage(res.data.error || '切磋失败', 'error')
    }
  } catch (e) {
    console.error('切磋失败', e)
    showMessage(e?.response?.data?.error || '切磋失败', 'error')
  } finally {
    sparring.value = false
  }
}

// 查看天赋
const viewTalent = () => {
  showMessage('查看天赋', 'info')
}

// 查看联盟
const viewAlliance = () => {
  showMessage('查看联盟', 'info')
}

// 查看战宠详情
const viewBeast = (beast) => {
  const beastId = beast?.id
  if (!beastId) {
    showMessage('无效的战宠', 'info')
    return
  }
  router.push({
    path: '/tower/beast',
    query: {
      beastType: 'player',
      beastId,
    },
  })
}

// 查看动态详情
const viewDynamicDetail = (dynamic) => {
  showMessage('查看动态详情', 'info')
}

// 返回前页
const goBack = () => {
  router.back()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

const loadCurrentUser = async () => {
  try {
    const res = await http.get('/auth/status')
    if (res.data.logged_in) {
      currentUserId.value = res.data.user_id
    }
  } catch (e) {
    console.error('获取当前用户失败', e)
  }
}

onMounted(async () => {
  await loadCurrentUser()
  await loadVipConfig()
  loadPlayerInfo()
})
</script>

<template>
  <div class="player-detail-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="player">
      <!-- 玩家名称 -->
      <div class="section">
        昵称: <span class="orange">{{ player.nickname }}</span> ({{ player.gender }})
      </div>

      <!-- 操作按钮 -->
      <div class="section">
        <a class="link" @click="sendMessage">写信</a> 
        <a class="link" @click="addFriend">{{ addingFriend ? '发送中...' : '加为好友' }}</a> 
        <a class="link" @click="blockPlayer">拉黑</a>
      </div>

      <!-- 基本信息 -->
      <div class="section">ID: {{ player.id }}</div>
      <div class="section">等级:{{ player.levelTitle }}(Lv.{{ player.level }})</div>
      <div class="section">魅力等级:{{ player.charmLevel }}级({{ player.charmExp }})</div>
      <div class="section">声望:{{ player.reputation }}</div>
      <div class="section">活力:{{ formatEnergy(player.energyRaw, player.vipLevel) }}</div>
        <div class="section">水晶塔:{{ player.crystalTower }} <a v-if="isOtherPlayer" class="link" @click="doInfuse">{{ infusing ? '灌注中...' : '灌注' }}</a></div>
      <div class="section">铜钱:{{ player.gold }}</div>

      <!-- 战宠（战斗队） -->
      <div class="section">
        战宠(战斗队):
        <template v-if="player.beasts && player.beasts.length">
          <template v-for="(beast, index) in player.beasts" :key="beast.id || index">
            <a class="link orange" @click="viewBeast(beast)">{{ beast.name }}-{{ beast.realm }}</a>
            <template v-if="index < player.beasts.length - 1"> </template>
          </template>
        </template>
        <span v-else class="gray">无</span>
      </div>

      <!-- 战力信息 -->
      <div class="section">综合战力:{{ player.battlePower }}</div>
      <div class="section">战绩:{{ player.battleRecord }} <a v-if="isOtherPlayer" class="link" @click="challenge">{{ sparring ? '切磋中...' : '切磋' }}</a></div>
      <div class="section">挑战排名: {{ player.challengeRank }}</div>
      <div class="section">状态:{{ player.status }}</div>
     
      
      <div class="section">
        联盟: <a class="link" @click="viewAlliance">{{ player.alliance }}</a>({{ player.allianceLevel }}级)
      </div>
      

      <!-- 动态 -->
      <div class="section title2">【动态】</div>
      <div class="section" v-for="(d, index) in player.dynamics" :key="index">
        {{ index + 1 }}.({{ d.time }}) {{ d.content }}
        <a v-if="d.hasDetail" class="link" @click="viewDynamicDetail(d)">查看</a>
      </div>
    </template>

    <!-- 返回 -->
    <div class="nav-links">
      <div><a class="link" @click="goBack">返回前页</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

   
  </div>
</template>

<style scoped>
.player-detail-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title2 {
  font-weight: bold;
  margin-top: 15px;
}

.section {
  margin: 4px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
  margin-right: 8px;
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

.orange {
  color: #FF6600;
}

.gray {
  color: #666;
}

.nav-links {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.footer {
  margin-top: 20px;
}

.small {
  font-size: 11px;
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

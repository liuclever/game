<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const player = ref(null)
const currentUserId = ref(null)
const isBlocked = ref(false)

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
    alert('缺少玩家ID')
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
      // 检查拉黑状态
      await checkBlockStatus()
    } else {
      player.value = null
      alert(res.data?.error || '加载失败')
    }
  } catch (e) {
    console.error('加载玩家信息失败', e)
    player.value = null
    const msg = e?.response?.data?.error || '加载失败'
    alert(msg)
  } finally {
    loading.value = false
  }
}

// 检查拉黑状态
const checkBlockStatus = async () => {
  if (!player.value?.id || !currentUserId.value) return
  if (player.value.id === currentUserId.value) return
  
  try {
    const res = await http.get(`/mail/block/check?target_id=${player.value.id}`)
    if (res.data.ok) {
      isBlocked.value = res.data.is_blocked || false
    }
  } catch (e) {
    console.error('检查拉黑状态失败', e)
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
      alert(res.data.message || '好友请求已发送')
    } else {
      alert(res.data.error || '发送失败')
    }
  } catch (e) {
    console.error('发送好友请求失败', e)
    alert(e?.response?.data?.error || '发送失败')
  } finally {
    addingFriend.value = false
  }
}

// 拉黑/解除拉黑
const blockPlayer = () => {
  if (!player.value?.id) return
  if (isBlocked.value) {
    // 已拉黑，跳转到解除拉黑确认页面
    router.push({
      path: '/block/unblock',
      query: {
        target_id: player.value.id,
        target_name: player.value.nickname || '该玩家'
      }
    })
  } else {
    // 未拉黑，跳转到拉黑确认页面
    router.push({
      path: '/block/confirm',
      query: {
        target_id: player.value.id,
        target_name: player.value.nickname || '该玩家'
      }
    })
  }
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
      alert(res.data.message)
      loadPlayerInfo()
    } else {
      alert(res.data.error || '灌注失败')
    }
  } catch (e) {
    console.error('灌注失败', e)
    alert(e?.response?.data?.error || '灌注失败')
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
      alert(res.data.error || '切磋失败')
    }
  } catch (e) {
    console.error('切磋失败', e)
    alert(e?.response?.data?.error || '切磋失败')
  } finally {
    sparring.value = false
  }
}

// 查看天赋
const viewTalent = () => {
  alert('查看天赋')
}

// 查看联盟
const viewAlliance = () => {
  alert('查看联盟')
}

// 查看战宠详情
const viewBeast = (beast) => {
  const beastId = beast?.id
  if (!beastId) {
    alert('无效的战宠')
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
  alert('查看动态详情')
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
  // 并行加载不依赖的数据，提升加载速度
  await Promise.all([
    loadCurrentUser(),
    loadVipConfig()
  ])
  // 然后加载玩家信息（依赖当前用户ID）
  loadPlayerInfo()
})
</script>

<template>
  <div class="player-detail-page">
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
        <a class="link" @click="blockPlayer">{{ isBlocked ? '已拉黑' : '拉黑' }}</a>
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
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 17px;
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
  font-size: 17px;
}
</style>

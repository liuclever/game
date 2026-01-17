<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 玩家信息
const player = ref(null)
const beasts = ref([])
const dynamics = ref([])
const loading = ref(true)
const error = ref('')
const currentUserId = ref(null)
const isBlocked = ref(false)

const isOtherPlayer = computed(() => {
  if (!player.value) return false
  if (!currentUserId.value) return true
  return player.value.user_id !== currentUserId.value
})

const formatReputation = (prestige, required) => {
  const cur = Number(prestige || 0)
  const target = required === null || required === undefined ? '已满级' : Number(required)
  return `${cur}/${target}`
}

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

// 检查拉黑状态
const checkBlockStatus = async () => {
  if (!player.value?.user_id || !currentUserId.value) return
  if (player.value.user_id === currentUserId.value) return
  
  try {
    const res = await http.get(`/mail/block/check?target_id=${player.value.user_id}`)
    if (res.data.ok) {
      isBlocked.value = res.data.is_blocked || false
    }
  } catch (e) {
    console.error('检查拉黑状态失败', e)
  }
}

// 加载玩家信息
const loadPlayer = async () => {
  const playerId = route.query.id
  if (!playerId) {
    error.value = '无效的玩家ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/player/profile?id=${playerId}`)
    if (res.data.ok) {
      const p = res.data.player || {}
      const prestige = Number(p.prestige || 0)
      player.value = {
        ...p,
        prestige,
        prestigeRequired: null,
        reputation: formatReputation(prestige, null),
      }
      beasts.value = res.data.beasts || []
      dynamics.value = res.data.dynamics || []
      // 声望阈值加载不阻塞主数据，可以并行或延迟加载
      loadPrestigeRequirement()
      // 检查拉黑状态
      await checkBlockStatus()
    } else {
      error.value = res.data.error || '加载失败'
    }
  } catch (e) {
    console.error('加载玩家信息失败', e)
    error.value = '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadCurrentUser()
  loadPlayer()
})

// 综合战力
const totalPower = computed(() => {
  return beasts.value.reduce((sum, b) => sum + (b.combat_power || 0), 0)
})

// 切磋
const sparring = ref(false)
const challenge = async () => {
  if (!player.value?.user_id) return
  if (sparring.value) return
  
  sparring.value = true
  try {
    const res = await http.post('/player/spar', { target_id: player.value.user_id })
    if (res.data.ok) {
      router.push({
        path: '/spar/report',
        query: { data: JSON.stringify(res.data.battle) }
      })
    } else {
      router.push({
        path: '/message',
        query: {
          message: res.data.error || '切磋失败',
          type: 'error'
        }
      })
    }
  } catch (e) {
    console.error('切磋失败', e)
    router.push({
      path: '/message',
      query: {
        message: e?.response?.data?.error || '切磋失败',
        type: 'error'
      }
    })
  } finally {
    sparring.value = false
  }
}

// 返回前页
const goBack = () => {
  router.back()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 写信
const sendMessage = () => {
  if (!player.value?.user_id) return
  router.push({ 
    path: '/mail/chat', 
    query: { target_id: player.value.user_id, name: player.value.nickname } 
  })
}

// 加为好友
const addingFriend = ref(false)
const addFriend = async () => {
  if (!player.value?.user_id) return
  if (addingFriend.value) return
  
  addingFriend.value = true
  try {
    const res = await http.post('/mail/friend-request/send', { target_id: player.value.user_id })
    if (res.data.ok) {
      router.push({
        path: '/message',
        query: {
          message: res.data.message || '好友请求已发送',
          type: 'success'
        }
      })
    } else {
      router.push({
        path: '/message',
        query: {
          message: res.data.error || '发送失败',
          type: 'error'
        }
      })
    }
  } catch (e) {
    console.error('发送好友请求失败', e)
    router.push({
      path: '/message',
      query: {
        message: e?.response?.data?.error || '发送失败',
        type: 'error'
      }
    })
  } finally {
    addingFriend.value = false
  }
}

// 拉黑/解除拉黑
const blockPlayer = () => {
  if (!player.value?.user_id) return
  if (isBlocked.value) {
    // 已拉黑，跳转到解除拉黑确认页面
    router.push({
      path: '/block/unblock',
      query: {
        target_id: player.value.user_id,
        target_name: player.value.nickname || '该玩家'
      }
    })
  } else {
    // 未拉黑，跳转到拉黑确认页面
    router.push({
      path: '/block/confirm',
      query: {
        target_id: player.value.user_id,
        target_name: player.value.nickname || '该玩家'
      }
    })
  }
}

// 查看联盟
const viewAlliance = () => {
  if (!player.value?.alliance) {
    console.error('该玩家未加入联盟')
    return
  }
  
  // 如果查看的是自己的信息，跳转到自己的联盟页面
  if (!isOtherPlayer.value) {
    router.push('/alliance')
  } else {
    // 查看其他玩家的联盟：跳转到联盟大厅并搜索该联盟名称
    router.push({
      path: '/alliance/hall',
      query: {
        keyword: player.value.alliance
      }
    })
  }
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
    '商城': '/shop',
    '联盟': '/alliance',  // 添加联盟路由
  }
  if (routes[name]) {
    // 如果是联盟链接，使用专门的viewAlliance函数处理
    if (name === '联盟') {
      viewAlliance()
    } else {
      router.push(routes[name])
    }
  } else {
    router.push({
      path: '/message',
      query: {
        message: `${name} 功能待实现`,
        type: 'error'
      }
    })
  }
}

// 查看幻兽详情
const viewBeast = (beast) => {
  router.push({
    path: '/tower/beast',
    query: { 
      beastType: 'player',
      beastId: beast.id 
    }
  })
}
</script>

<template>
  <div class="profile-page">
    <!-- 加载中 -->
    <div v-if="loading" class="section gray">加载中...</div>

    <!-- 错误 -->
    <div v-else-if="error" class="section red">{{ error }}</div>

    <!-- 玩家信息 -->
    <template v-else-if="player">
      <!-- 基本信息 -->
      <div class="section">
        昵称: <span class="username">{{ player.nickname }}</span> 🐦 （{{ player.gender || '男' }}）
      </div>
      <div class="section">
        <a class="link" @click="sendMessage">写信</a>  
        <a class="link" @click="addFriend">{{ addingFriend ? '发送中...' : '加为好友' }}</a>  
        <a class="link" @click="blockPlayer">{{ isBlocked ? '已拉黑' : '拉黑' }}</a>
      </div>
      <div class="section">
        ID : {{ player.user_id }}
      </div>
      <div class="section">
        等级:Lv.{{ player.level }}
      </div>
      <div class="section">
        魅力等级:{{ player.charm_level || 1 }}级({{ player.charm || 0 }}/1000)
      </div>
      <div class="section">
        声望:{{ player.reputation }}
      </div>
        <div class="section">
          活力:{{ player.energy || 100 }}/{{ player.max_energy || 190 }}
        </div>
      <div class="section">
        水晶塔:{{ player.spirit_stone || 5 }}/100
      </div>
      <div class="section">
        铜钱:{{ player.gold || 0 }}
      </div>

      <!-- 战龙（幻兽）-->
      <div class="section">
        战龙: 
        <template v-if="beasts.length > 0">
          <template v-for="(beast, index) in beasts" :key="beast.id">
            <a class="link" @click="viewBeast(beast)">{{ beast.name }}-{{ beast.realm }}</a>
            <span v-if="index < beasts.length - 1">  </span>
          </template>
        </template>
        <span v-else class="gray">无</span>
      </div>

      <div class="section">
        综合战力:{{ totalPower }}
      </div>
      <div class="section">
        战绩:{{ player.wins || 0 }}/{{ player.battles || 0 }} <a v-if="isOtherPlayer" class="link" @click="challenge">{{ sparring ? '切磋中...' : '切磋' }}</a>
      </div>
      <div class="section" v-if="player.arena_rank && player.arena_position">
        挑战排名: {{ player.arena_rank }} 赛区.{{ player.arena_position }} 名
      </div>
      <div class="section">
        状态:{{ player.status || '落龙镇' }}<span v-if="player.status_detail"> ({{ player.status_detail }})</span>
      </div>
      <div class="section" v-if="player.mount">
        坐骑:<span class="link readonly">{{ player.mount }}</span>
      </div>
      <div class="section">
        联盟:<span v-if="player.alliance">
          <a class="link" @click="handleLink('联盟')">{{ player.alliance }}</a>
          <span v-if="player.alliance_title"> | {{ player.alliance_title }}</span>
          <span v-if="player.alliance_level">({{ player.alliance_level }}级)</span>
        </span>
        <span v-else class="gray">未加入</span>
      </div>
      <div class="section" v-if="player.title">
        封号:{{ player.title }}
      </div>

      <!-- 动态 -->
      <div class="section title">【动态】</div>
      <template v-if="dynamics.length > 0">
        <div v-for="(d, index) in dynamics" :key="index" class="section dynamic">
          {{ index + 1 }}.({{ d.time }}) {{ d.text }}
          <template v-if="d.link">
            <a class="link" @click="handleLink(d.link)">查看</a>
          </template>
        </div>
      </template>
      <div v-else class="section gray">暂无动态</div>

      <!-- 返回链接 -->
      <div class="section spacer">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>

    
  </div>
</template>

<style scoped>
.profile-page {
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
  margin-top: 12px;
  margin-bottom: 4px;
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

.username {
  color: #CC6600;
}

.gray {
  color: #666666;
}

.red {
  color: #CC0000;
}

.small {
  font-size: 17px;
}

.dynamic {
  color: #CC0000;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

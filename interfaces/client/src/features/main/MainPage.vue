<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import ChatPanel from '@/features/lobby/components/ChatPanel.vue'

const router = useRouter()

// 主页顶部固定活动时间（在时间范围内才展示）
const ACTIVITY_TIME_TEXT = '2026.1.25-2026.2.20'
// 注意：Date 构造使用本地时区；月份从 0 开始（1月=0，2月=1）
const ACTIVITY_START = new Date(2026, 0, 25, 0, 0, 0, 0)
const ACTIVITY_END = new Date(2026, 1, 20, 23, 59, 59, 999)
const nowMs = ref(Date.now())
let nowTimer = null
const shouldShowActivityTime = computed(() => {
  const now = new Date(nowMs.value)
  return now >= ACTIVITY_START && now <= ACTIVITY_END
})

// 公告列表
const announcements = ref([])
const loadingAnnouncements = ref(true)

// 加载公告
const loadAnnouncements = async () => {
  loadingAnnouncements.value = true
  try {
    const response = await fetch('/configs/announcements.json')
    if (response.ok) {
      const data = await response.json()
      // 过滤当前有效的公告（在活动时间内）
      const now = new Date()
      announcements.value = (data.announcements || []).filter(a => {
        const start = new Date(a.start_time)
        const end = new Date(a.end_time)
        return now >= start && now <= end
      })
    }
  } catch (e) {
    console.error('加载公告失败', e)
  } finally {
    loadingAnnouncements.value = false
  }
}

// 跳转到公告详情
const goAnnouncementDetail = (id) => {
  router.push(`/announcement/${id}`)
}

// 登录状态
const isLoggedIn = ref(false)
const currentUser = ref(null)
const loading = ref(true)

// 等级显示：1星=10级，1品=1级，例如 79 => 7星9品召唤师（前端计算）
const summonerTitle = computed(() => {
  const lv = Number(currentUser.value?.level || 0)
  if (!Number.isFinite(lv) || lv <= 0) return ''
  const star = Math.floor(lv / 10)
  const pin = lv % 10
  return `${star}星${pin}品召唤师`
})

const hasSignedToday = computed(() => {
  const last = String(currentUser.value?.last_signin_date || '').trim()
  if (!last) return false
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return last === `${yyyy}-${mm}-${dd}`
})

const signinRewardMsg = ref('')

// 古树（幸运果实）快捷状态：主页展示“今日幸运果实数字/是否已领取”，点击跳转古树
const treeStatus = ref(null)
const treeStatusError = ref('')
const loadTreeStatus = async () => {
  if (!isLoggedIn.value) return
  treeStatusError.value = ''
  try {
    const res = await http.get('/tree/status')
    if (res.data?.ok) {
      treeStatus.value = res.data
    } else {
      treeStatusError.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    treeStatusError.value = e?.response?.data?.error || '加载失败'
  }
}
const treeTodayNumber = computed(() => treeStatus.value?.today_number ?? null)
const treeClaimedToday = computed(() => !Boolean(treeStatus.value?.can_draw_today))
const goTree = () => router.push('/tree')

// 修行状态
const cultivation = ref({
  is_cultivating: false,
  remaining_seconds: 0,
  cultivation_reward: 0,
  can_harvest: false,
  prestige: 0,
  prestige_required: 100,
  can_levelup: false,
  incense_remaining_seconds: 0,
})

// 修行选项
const cultivationOptions = ref([])
const showCultivationOptions = ref(false)
const stopping = ref(false) // 防止重复点击终止按钮

const prestigeDisplay = computed(() => {
  const prestige = cultivation.value?.prestige
  const required = cultivation.value?.prestige_required
  const current = prestige ?? currentUser.value?.prestige ?? 0
  if (required === null || required === undefined) {
    return `${current}/已满级`
  }
  return `${current}/${Number(required)}`
})

// 当前位置和副本
const currentLocation = ref('林中空地')
const moving = ref(false)
const movingTo = ref('')
const remainingSeconds = ref(0)

// 召唤大陆联盟排行（前三名）
const allianceTop3 = ref([])
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

// 当前位置的副本
const currentDungeons = computed(() => {
  return DUNGEONS.filter(d => d.city === currentLocation.value)
})

// 倒计时定时器
let countdownTimer = null
let moveTimer = null

// 检查登录状态
const checkAuth = async () => {
  try {
    const res = await http.get('/auth/status')
    console.log('登录状态检查响应:', res.data)
    if (res.data && res.data.logged_in) {
      isLoggedIn.value = true
      currentUser.value = {
        id: res.data.user_id,
        nickname: res.data.nickname,
        level: res.data.level,
        rank_name: res.data.rank_name,
        gold: res.data.gold, // 兼容旧字段（不要在 UI 里当"铜钱"展示）
        copper: res.data.copper, // 铜钱
        exp: res.data.exp,
        battle_power: res.data.battle_power,
        prestige: res.data.prestige,
        energy: res.data.energy,
        max_energy: res.data.max_energy,
        vip_level: res.data.vip_level,
        crystal_tower: res.data.crystal_tower,
        yuanbao: res.data.yuanbao,
        last_signin_date: res.data.last_signin_date,
      }
      console.log('用户信息已加载:', currentUser.value)
      // 获取修行状态
      loadCultivationStatus()
      // 获取当前位置
      loadCurrentLocation()
      // 获取古树状态（用于“今日幸运果实”快捷展示）
      loadTreeStatus()
    } else {
      isLoggedIn.value = false
      currentUser.value = null
      console.log('用户未登录')
    }
  } catch (e) {
    console.error('检查登录状态失败', e)
    console.error('错误详情:', e.response?.data || e.message)
    // 如果请求失败，尝试从 localStorage 读取基本信息（作为降级方案）
    const userId = localStorage.getItem('user_id')
    if (userId) {
      console.warn('使用 localStorage 降级方案')
      isLoggedIn.value = true
      currentUser.value = {
        id: parseInt(userId),
        nickname: localStorage.getItem('nickname') || '未知',
        level: parseInt(localStorage.getItem('level') || '0'),
      }
    } else {
      isLoggedIn.value = false
      currentUser.value = null
    }
  } finally {
    loading.value = false
  }
}

// 加载召唤大陆联盟排行（前三名）
const loadAllianceTop3 = async () => {
  try {
    console.log('[MainPage] 开始加载联盟排行')
    const res = await http.get('/alliance/war/top3')
    if (res.data.ok && res.data.data) {
      allianceTop3.value = res.data.data.top3 || []
      console.log('[MainPage] 联盟排行加载成功')
    }
  } catch (e) {
    console.error('[MainPage] 加载联盟排行失败', e)
    allianceTop3.value = []
  }
}

// 加载修行状态
const loadCultivationStatus = async () => {
  try {
    const res = await http.get('/cultivation/status')
    if (res.data.ok) {
      cultivation.value = res.data
      // 更新用户声望
      if (currentUser.value) {
        currentUser.value.prestige = res.data.prestige
      }
      // 如果正在修行，启动倒计时
      if (res.data.is_cultivating) {
        startCountdown()
      }
    }
  } catch (e) {
    console.error('加载修行状态失败', e)
  }
}

// 加载当前位置
const loadCurrentLocation = async () => {
  try {
    const res = await http.get('/map/info')
    if (res.data.ok && res.data.current_location) {
      currentLocation.value = res.data.current_location
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
            loadCurrentLocation()
            loadCultivationOptions()
          }
        }, 1000)
      }
    }
  } catch (e) {
    console.error('加载当前位置失败', e)
  }
}

// 启动倒计时
const startCountdown = () => {
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (cultivation.value.remaining_seconds > 0) {
      cultivation.value.remaining_seconds--
      if (cultivation.value.remaining_seconds <= 0) {
        cultivation.value.can_harvest = true
      }
    }
    if ((cultivation.value.incense_remaining_seconds || 0) > 0) {
      cultivation.value.incense_remaining_seconds--
      if (cultivation.value.incense_remaining_seconds < 0) {
        cultivation.value.incense_remaining_seconds = 0
      }
    }
    // 不再在倒计时结束时自动设置 is_cultivating = false
    // 让用户手动点击收获
  }, 1000)
}

const formatIncenseCountdown = computed(() => {
  const seconds = Number(cultivation.value.incense_remaining_seconds || 0)
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) {
    return `${h}小时${m}分钟`
  }
  return `${m}分钟`
})

// 格式化倒计时（剩余时间）
const formatCountdown = computed(() => {
  const seconds = cultivation.value.remaining_seconds
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h}时${m.toString().padStart(2, '0')}分${s.toString().padStart(2, '0')}秒`
})

// 格式化已修行时间
const formatElapsed = computed(() => {
  const maxSeconds = cultivation.value.max_duration_seconds || 28800
  const remaining = cultivation.value.remaining_seconds || 0
  const elapsed = maxSeconds - remaining
  const h = Math.floor(elapsed / 3600)
  const m = Math.floor((elapsed % 3600) / 60)
  if (h > 0) {
    return `${h}小时${m}分钟`
  }
  return `${m}分钟`
})

// 加载修行选项
const loadCultivationOptions = async () => {
  try {
    const res = await http.get('/cultivation/options')
    if (res.data.ok) {
      cultivationOptions.value = res.data.options || res.data.areas || []
    }
  } catch (e) {
    console.error('加载修行选项失败', e)
    cultivationOptions.value = []
  }
}

// 显示修行选项
const toggleCultivationOptions = async () => {
  router.push('/cultivation')
}

// 当前位置可用的副本列表
const currentLocationDungeons = computed(() => {
  if (!cultivationOptions.value || cultivationOptions.value.length === 0) {
    return []
  }
  // 只取第一个区域（当前位置）的副本
  return cultivationOptions.value[0]?.dungeons || []
})

// 当前位置的区域名称
const currentCultivationArea = computed(() => {
  if (!cultivationOptions.value || cultivationOptions.value.length === 0) {
    return ''
  }
  return cultivationOptions.value[0]?.name || currentLocation.value
})

// 直接开始修行（使用当前地图第一个副本）
const startCultivationDirect = async () => {
  // 主界面不提供时长选择，统一跳转到修行页（在修行页选择 2/4/8/12/24 小时）
  router.push('/cultivation')
}

// 开始修行
const startCultivation = async (areaName, dungeonName) => {
  router.push('/cultivation')
}

// 领取修行奖励
const harvestCultivation = async () => {
  try {
    const res = await http.post('/cultivation/harvest')
    if (res.data.ok) {
      alert(res.data.message)
      loadCultivationStatus()
      checkAuth() // 刷新用户信息
    } else {
      alert(res.data.error)
    }
  } catch (e) {
    console.error('领取奖励失败', e)
  }
}

// 终止修行
const stopCultivation = async () => {
  if (stopping.value) {
    console.log('正在终止修行中，请稍候...')
    return
  }
  
  // 防止重复点击
  stopping.value = true
  
  try {
    // 先刷新一次状态，确保前后端一致
    await loadCultivationStatus()
    
    // 再次检查是否真的在修行中
    if (!cultivation.value.is_cultivating) {
      alert('当前未在修行')
      stopping.value = false
      return
    }
    
    const res = await http.post('/cultivation/stop')
    if (res.data.ok) {
      if (countdownTimer) clearInterval(countdownTimer)
      // 显示奖励信息
      if (res.data.rewards) {
        const rewards = res.data.rewards
        let msg = `${res.data.message}\n获得声望: ${rewards.prestige}\n获得强化石: ${rewards.spirit_stones}`
        if (rewards.beasts && rewards.beasts.length > 0) {
          rewards.beasts.forEach(b => {
            msg += `\n${b.name}: +${b.exp_gain}经验${b.leveled_up ? ' (升级!)' : ''}`
          })
        }
        if (rewards.items && rewards.items.length > 0) {
          msg += '\n获得物品: ' + rewards.items.join(', ')
        }
        alert(msg)
      } else {
        alert(res.data.message)
      }
      await loadCultivationStatus()
      await checkAuth() // 刷新用户信息
    } else {
      alert(res.data.error)
    }
  } catch (e) {
    console.error('终止修行失败', e)
    alert(e.response?.data?.error || '终止修行失败')
  } finally {
    stopping.value = false
  }
}

// 晋级提示消息
const levelupMessage = ref('')
const levelupMessageType = ref('') // success, error

// 晋级
const doLevelup = async () => {
  try {
    const res = await http.post('/player/levelup')
    if (res.data.ok) {
      // 显示页面内提示消息，而不是弹窗
      levelupMessage.value = res.data.message
      levelupMessageType.value = 'success'
      // 3秒后自动清除消息
      setTimeout(() => {
        levelupMessage.value = ''
        levelupMessageType.value = ''
      }, 3000)
      checkAuth() // 刷新用户信息
      loadCultivationStatus()
    } else {
      // 错误消息也显示在页面内
      levelupMessage.value = res.data.error
      levelupMessageType.value = 'error'
      setTimeout(() => {
        levelupMessage.value = ''
        levelupMessageType.value = ''
      }, 3000)
    }
  } catch (e) {
    console.error('晋级失败', e)
    levelupMessage.value = '晋级失败，请稍后重试'
    levelupMessageType.value = 'error'
    setTimeout(() => {
      levelupMessage.value = ''
      levelupMessageType.value = ''
    }, 3000)
  }
}

onMounted(async () => {
  console.log('[MainPage] 组件挂载，开始加载数据')
  try {
    await checkAuth()
    await loadAllianceTop3()
    await loadAnnouncements()
    // 定时刷新“系统时间”，避免页面常开跨天导致展示状态不更新
    if (nowTimer) clearInterval(nowTimer)
    nowTimer = setInterval(() => {
      nowMs.value = Date.now()
    }, 30 * 1000)
    console.log('[MainPage] 数据加载完成')
  } catch (e) {
    console.error('[MainPage] 数据加载失败:', e)
    // 即使加载失败，也要确保 loading 状态结束
    loading.value = false
  }
})

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (moveTimer) clearInterval(moveTimer)
  if (nowTimer) clearInterval(nowTimer)
})

// 登出
const doLogout = async () => {
  try {
    await http.post('/auth/logout')
    isLoggedIn.value = false
    currentUser.value = null
    localStorage.clear()
    router.push('/login')
  } catch (e) {
    console.error('登出失败', e)
  }
}

// 跳转登录
const goLogin = () => {
  router.push('/login')
}

// 签到（当日仅一次）
const handleSignin = async () => {
  if (!isLoggedIn.value) return
  if (hasSignedToday.value) return
  signinRewardMsg.value = ''
  try {
    const res = await http.post('/player/signin')
    if (res.data?.ok) {
      const issuer = String(res.data?.issuer_name || '').trim()
      const copper = res.data?.reward?.copper || 0
      const multi = res.data?.reward?.multiplier || 1
      signinRewardMsg.value = issuer
        ? `已发放奖励：颁发者【${issuer}】，铜钱+${copper}${multi >= 2 ? ' (×2)' : ''}`
        : `已发放奖励：铜钱+${copper}${multi >= 2 ? ' (×2)' : ''}`
      await checkAuth()
    } else {
      alert(res.data?.error || '签到失败')
    }
  } catch (e) {
    alert(e?.response?.data?.error || '签到失败')
  }
}

// 导航到背包
const goInventory = () => {
  router.push('/inventory')
}

// 导航到闯塔
const goTower = () => {
  router.push('/tower')
}

// 导航到幻兽
const goBeast = () => {
  router.push('/beast')
}

// 导航到副本挑战
const goDungeonChallenge = (name) => {
  router.push(`/dungeon/challenge/${encodeURIComponent(name)}`)
}

// 导航到战灵：优先跳到第一只幻兽的战灵页
const goSpirit = async () => {
  try {
    const res = await http.get('/spirit/page-data')
    if (res.data && res.data.ok) {
      const beasts = res.data.beasts || []
      const firstId = beasts.length ? beasts[0].id : null
      if (firstId) {
        return router.push(`/beast/${firstId}/spirit`)
      }
    }
  } catch (e) {
    console.error('获取战灵默认数据失败', e)
  }
  // 若无幻兽或请求失败，进入灵件室
  router.push('/spirit/warehouse')
}

// 导航到战骨：优先跳到第一只幻兽的战骨页
const goBone = async () => {
  try {
    const res = await http.get('/bone/page-data')
    if (res.data && res.data.ok) {
      const beasts = res.data.beasts || []
      const firstId = beasts.length ? beasts[0].id : null
      if (firstId) {
        return router.push(`/beast/${firstId}/bone`)
      }
    }
  } catch (e) {
    console.error('获取战骨默认数据失败', e)
  }
  // 若无幻兽或请求失败，提示用户
  alert('您暂无幻兽，无法查看战骨')
}

const goEvolve = async () => {
  router.push('/beast')
}

// 导航到地图
const goMap = () => {
  router.push('/map')
}

// 跳转到玩家首页
const goPlayerHome = (userId) => {
  if (!userId) return
  router.push({ path: '/player/detail', query: { id: userId } })
}

// 点击链接
const handleLink = (name) => {
  const key = String(name || '').trim()
  // 特殊处理：战灵
  if (key === '战灵') {
    return goSpirit()
  }
  // 特殊处理：战骨
  if (key === '战骨') {
    return goBone()
  }
  if (key === '进化') {
    return goEvolve()
  }
    // 特殊处理：魔魂
    if (key === '魔魂') {
      return router.push('/mosoul')
    }
    // 特殊处理：副本挑战
    if (key === '挑战') {
      return router.push('/dungeon/challenge')
    }
  const routes = {
      '背包': '/inventory',
      '幻兽': '/beast',
      '炼妖壶': '/refine-pot',
      '地图': '/map',
      '信件': '/mail',
      '赞助': '/sponsor',
      '好友': '/friend',
      '擂台': '/arena',
      '闯塔': '/tower',
      '排行': '/ranking',
      '召唤之王挑战赛': '/king',
      '商城': '/shop',
      '战场': '/battlefield',
      '竞技': '/arena/streak',
      '礼包': '/gifts',
        '任务': '/tasks/rewards',
        '查看': '/tasks/daily',
        '前往': '/tasks/daily',
        '定老城': '/map',
        '移动': '/map',
        '化仙': '/huaxian',
        'VIP': '/vip',
        '联盟': '/alliance',
        '盟战': '/alliance/war',
        '兑换': '/exchange',
        '提升': '/vip',
        '活力': '/vip',
        '图鉴': '/handbook',
      }

  if (routes[key]) {
    router.push(routes[key])
  } else {
    alert(`点击了: ${key}`)
  }
}
</script>

<template>
  <div class="main-page">
    <!-- 固定活动时间（仅在活动期内展示） -->
    <div class="section activity-time" v-if="shouldShowActivityTime">
      活动时间：<span class="red bold">{{ ACTIVITY_TIME_TEXT }}</span>
    </div>

    <!-- 公告列表 -->
    <div class="announcement-list" v-if="announcements.length > 0">
      <div 
        v-for="ann in announcements" 
        :key="ann.id" 
        class="announcement-item"
        @click="goAnnouncementDetail(ann.id)"
      >
        <span class="ann-new">[新]</span>
        <span class="ann-title">{{ ann.title }}</span>
      </div>
    </div>

    <!-- 欢迎区 -->
    <div class="section" v-if="isLoggedIn && currentUser">
      欢迎您，<a class="link username" @click="goPlayerHome(currentUser.id)">{{ currentUser.nickname }}</a><span v-if="Number(currentUser.vip_level || 0) > 0">👑</span>
      <span> (ID:{{ currentUser.id }}) </span>
      <a class="link" @click="handleLink('好友')">好友>></a>
    </div>
    <div class="section" v-else>
      <a class="link" @click="goLogin">点击登录</a>
    </div>

    <div class="section">
      今日
      <template v-if="isLoggedIn">
        <span v-if="hasSignedToday" class="link readonly">已签到</span>
        <a v-else class="link" @click="handleSignin">签到</a>
      </template>
      <template v-else>
        <span class="gray">未登录</span>
      </template>
      <div class="section indent red" v-if="signinRewardMsg">{{ signinRewardMsg }}</div>
    </div>
    <div class="section" v-if="isLoggedIn">
      今日幸运果实数字
      <template v-if="treeClaimedToday">
        <span class="gray">已领取</span>
      </template>
      <template v-else>
        <a class="link" @click="goTree">未领取</a>
      </template>
      <span class="gray" v-if="treeStatusError">（{{ treeStatusError }}）</span>
    </div>

    <!-- 召唤大陆联盟排行 -->
    <div class="section title">【召唤大陆联盟排行】</div>
    <template v-if="allianceTop3.length > 0">
      <div class="section indent" v-for="alliance in allianceTop3" :key="alliance.allianceId">
        <template v-if="alliance.rank === 1">第一联盟</template>
        <template v-else-if="alliance.rank === 2">第二联盟</template>
        <template v-else-if="alliance.rank === 3">第三联盟</template>
        <template v-else>第{{ alliance.rank }}名</template>：<span class="red bold">{{ alliance.allianceName }}({{ alliance.allianceLevel }}级)</span>
      </div>
    </template>
    <div class="section indent gray" v-else>
      暂无排名
    </div>

    <!-- 常用功能 -->
    <div class="section title">【常用功能】</div>
    <div class="section indent">
      【<a class="link" @click="toggleCultivationOptions">修行</a>| <a class="link" @click="handleLink('竞技')">竞技</a>| <a class="link" @click="handleLink('任务')">任务</a>| 师徒】
    </div>
      <!-- 修行选项 -->
      <template v-if="isLoggedIn">
        <div class="section indent" v-if="cultivation.is_cultivating && cultivation.can_harvest">
          修行: 修行中（已修行{{ formatElapsed }}）
          <a class="link" @click="router.push('/cultivation')">查看</a>
          <a class="link" @click="harvestCultivation">修行收获</a>
          <a class="link" @click="stopCultivation">终止</a>
        </div>
        <div class="section indent" v-else-if="cultivation.is_cultivating">
          修行: 修行中（{{ formatCountdown }}后可收获）  
          <a class="link" @click="router.push('/cultivation')">查看</a>
          <a class="link" @click="stopCultivation">终止</a>
        </div>
        <div class="section indent" v-else>
          修行: 空闲中 <a class="link" @click="startCultivationDirect">开始修行</a>
        </div>
      </template>
      <div class="section indent" v-if="isLoggedIn">
        活动副本:龙宫之谜 <a class="link" @click="router.push('/dragonpalace')">进入</a>
      </div>
      <div class="section indent small" v-if="isLoggedIn">
        (时间:10:00-24:00)
      </div>

    <!-- 副本列表 -->
    <div v-for="dungeon in currentDungeons" :key="dungeon.name" class="section indent">
      副本:<a class="link orange" @click="handleLink(dungeon.name)">{{ dungeon.name }}</a> ({{ dungeon.level_range }}) <a class="link" @click="goDungeonChallenge(dungeon.name)">挑战</a>
    </div>

    <!-- 庄园等 -->
    <div class="section indent">
      庄园:<router-link to="/manor" class="link">进入</router-link>
    </div>
    <div class="section indent">
      凝神香:
      <template v-if="(cultivation.incense_remaining_seconds || 0) > 0">
        剩余{{ formatIncenseCountdown }}
      </template>
      <template v-else>
        无
      </template>
    </div>
    <div class="section indent">
      能力: <a class="link" @click="handleLink('战骨')">战骨</a> <a class="link" @click="handleLink('魔魂')">魔魂</a> <a class="link" @click="handleLink('战灵')">战灵</a>
    </div>
    <div class="section indent">
      进阶: <a class="link" @click="handleLink('炼妖壶')">炼妖壶</a> <a class="link" @click="handleLink('进化')">进化</a> <span class="link readonly">转生</span>
    </div>

    <!-- 个人信息 -->
    <div class="section title">【个人信息】</div>
    <!-- 晋级提示消息 -->
    <div v-if="levelupMessage" class="section message" :class="levelupMessageType">
      {{ levelupMessage }}
    </div>
    <template v-if="isLoggedIn && currentUser">
      <div class="section indent">
        等级:<span class="bold">{{ summonerTitle }}</span>
      </div>
      <div class="section indent">
        声望:{{ prestigeDisplay }} <a
          v-if="cultivation.can_levelup"
          class="link red"
          @click="doLevelup"
        >晋级</a>
      </div>
        <div class="section indent">
          <a class="link blue" @click="handleLink('活力')">活力</a>:{{ currentUser.energy }}/{{ currentUser.max_energy || 190 }} ( <a class="link" @click="handleLink('提升')">提升</a> )
        </div>
      <div class="section indent">
        水晶塔:{{ currentUser.crystal_tower || 0 }}/100
      </div>
      <div class="section indent">
        战力:{{ currentUser.battle_power || 0 }}
      </div>
      <div class="section indent">
        铜钱:{{ currentUser.copper || 0 }}
      </div>
      <div class="section indent">
        元宝:{{ currentUser.yuanbao || 0 }}
      </div>
    </template>
    <div class="section indent gray" v-else>
      请先登录查看个人信息
    </div>

    <!-- 聊天区 -->
    <div class="section title">【聊天区】</div>
    <ChatPanel />

    <!-- 皇城：召唤之王挑战赛 -->
    <div class="section title">【皇城】</div>
    <div class="section indent">
      <a class="link" @click="handleLink('召唤之王挑战赛')">召唤之王挑战赛</a>
    </div>

    <!-- 导航菜单 -->
    <div class="section">
      <a class="link" @click="goBeast">幻兽</a>. <a class="link" @click="goInventory">背包</a>. <a class="link" @click="handleLink('商城')">商城</a>. <a class="link" @click="handleLink('赞助')">赞助</a>. <a class="link" @click="handleLink('礼包')">礼包</a>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('联盟')">联盟</a>. <a class="link" @click="handleLink('盟战')">盟战</a>. <a class="link" @click="goMap">地图</a>. <span class="link readonly">天赋</span>. <a class="link" @click="handleLink('化仙')">化仙</a>
    </div>
    <div class="section">
      <a class="link" @click="router.push('/spar/report')">切磋</a>. <a class="link" @click="goTower">闯塔</a>. <a class="link" @click="handleLink('战场')">战场</a>. <a class="link" @click="handleLink('擂台')">擂台</a>. <span class="link readonly">坐骑</span>
    </div>
    <div class="section">
      <a class="link" @click="router.push('/tree')">古树</a>. <a class="link" @click="handleLink('排行')">排行</a>. <span class="link readonly">成就</span>. <a class="link" @click="handleLink('图鉴')">图鉴</a>. <span class="link readonly">攻略</span>
    </div>
    <div class="section">
      <a class="link" @click="handleLink('兑换')">兑换</a>. <a class="link" @click="router.push('/signin')">签到</a>. <span class="link readonly">论坛</span>. <a class="link" @click="handleLink('VIP')">VIP</a>. <span class="link readonly">安全锁</span>
    </div>

    <!-- 退出登录（按需求放到底部） -->
    <div class="section" v-if="isLoggedIn">
      <a class="link red" @click="doLogout">退出登录</a>
    </div>

    <!-- 底部信息 -->


    <!-- 版权 -->

  </div>
</template>

<style scoped>
.main-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 18px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.activity-time {
  padding-bottom: 6px;
  border-bottom: 1px dashed #CCCCCC;
  margin-bottom: 6px;
}

.announcement-list {
  margin-bottom: 8px;
  border-bottom: 1px dashed #CCCCCC;
  padding-bottom: 6px;
}

.announcement-item {
  margin: 2px 0;
  cursor: pointer;
}

.announcement-item:hover {
  background: #F5F5F5;
}

.ann-new {
  color: #CC0000;
  font-weight: bold;
  margin-right: 4px;
}

.ann-title {
  color: #0066CC;
  cursor: pointer;
}

.ann-title:hover {
  text-decoration: underline;
}

.section {
  margin: 2px 0;
}

.title {
  margin-top: 12px;
}

.indent {
  padding-left: 8px;
}

.announce {
  margin-bottom: 8px;
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

.link.red {
  color: #CC3300;
}

.link.purple {
  color: #9933FF;
}

.link.blue {
  color: #0066CC;
}

.new {
  color: #FF6600;
  font-weight: bold;
}

.username {
  color: #CC3300;
  font-weight: bold;
}

.red {
  color: #CC0000;
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

.message {
  padding: 8px 12px;
  margin: 8px 0;
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

.chat-box {
  border: 1px solid #CCCCCC;
  background: #FFFFFF;
  padding: 6px;
  margin: 6px 0;
}

.chat-msg {
  margin: 2px 0;
  font-size: 20px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.cultivation-options {
  background: #ffffff;
  border: 1px solid #DDD;
  padding: 4px 8px;
  margin: 4px 0;
}
</style>

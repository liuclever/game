<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const errorMsg = ref('')
const announcement = ref(null)
const allAnnouncements = ref([])

// 各活动的状态数据
const powerRankingData = ref({
  currentBracket: 29,
  rankings: [],
  myRank: 0,
  totalPages: 1,
  currentPage: 1,
  isFinalized: false,
  isActivityEnded: false,
  loading: false,
})

const lotteryData = ref({
  drawCount: 0,
  fragmentCount: 0,
  roundCount: 0,
  yuanbao: 0,
  rewards: [],
  drawing: false,
})

const copperBookData = ref({
  boughtToday: 0,
  dailyLimit: 4,
  canBuy: true,
  yuanbao: 0,
  buying: false,
})

const prestigeData = ref({
  freeClaimed: false,
  canClaimFree: false,
  boughtToday: 0,
  canBuy: true,
  yuanbao: 0,
  level: 0,
  claiming: false,
})

const tyrannosaurusData = ref({
  claimed: false,
  canClaim: false,
  totalGems: 0,
  requiredGems: 300,
  level: 0,
  selectedBall: 0,
  claiming: false,
})

const rebateData = ref({
  totalGems: 0,
  tiers: [],
  claiming: false,
})

// 获取公告ID
const announcementId = computed(() => route.params.id)

// 加载公告配置
const loadAnnouncements = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const response = await fetch('/configs/announcements.json')
    if (!response.ok) {
      throw new Error('加载公告配置失败')
    }
    const data = await response.json()
    allAnnouncements.value = data.announcements || []
    
    // 找到当前公告
    const current = allAnnouncements.value.find(a => a.id === announcementId.value)
    if (current) {
      announcement.value = current
      // 根据公告类型加载对应数据
      await loadActivityData()
    } else {
      errorMsg.value = '公告不存在'
    }
  } catch (e) {
    console.error('加载公告失败', e)
    errorMsg.value = '加载公告失败'
  } finally {
    loading.value = false
  }
}

// 根据活动类型加载数据
const loadActivityData = async () => {
  const id = announcementId.value
  try {
    if (id === 'power_ranking') {
      await loadPowerRanking(powerRankingData.value.currentBracket)
    } else if (id === 'wheel_lottery') {
      await loadLotteryStatus()
    } else if (id === 'copper_book') {
      await loadCopperBookStatus()
    } else if (id === 'prestige_boost') {
      await loadPrestigeStatus()
    } else if (id === 'tyrannosaurus_preview') {
      await loadTyrannosaurusStatus()
    } else if (id === 'yuanbao_rebate') {
      await loadRebateStatus()
    }
  } catch (e) {
    console.error('加载活动数据失败', e)
  }
}

// ==================== 新人战力榜排行 ====================

const loadPowerRanking = async (bracket) => {
  powerRankingData.value.loading = true
  try {
    const res = await http.get(`/announcement/power-ranking/${bracket}?page=${powerRankingData.value.currentPage}`)
    if (res.data.ok) {
      powerRankingData.value.rankings = res.data.rankings || []
      powerRankingData.value.myRank = res.data.my_rank || 0
      powerRankingData.value.totalPages = res.data.totalPages || 1
      powerRankingData.value.isFinalized = res.data.is_finalized || false
      powerRankingData.value.isActivityEnded = res.data.is_activity_ended || false
    }
  } catch (e) {
    console.error('加载战力榜失败', e)
  } finally {
    powerRankingData.value.loading = false
  }
}

const switchBracket = (bracket) => {
  powerRankingData.value.currentBracket = bracket
  powerRankingData.value.currentPage = 1
  loadPowerRanking(bracket)
}

const goToRankingPage = (page) => {
  if (page < 1 || page > powerRankingData.value.totalPages) return
  powerRankingData.value.currentPage = page
  loadPowerRanking(powerRankingData.value.currentBracket)
}

// ==================== 轮盘抽奖 ====================

const loadLotteryStatus = async () => {
  try {
    const res = await http.get('/announcement/lottery/status')
    if (res.data.ok) {
      lotteryData.value.drawCount = res.data.draw_count || 0
      lotteryData.value.fragmentCount = res.data.fragment_count || 0
      lotteryData.value.roundCount = res.data.round_count || 0
      lotteryData.value.yuanbao = res.data.yuanbao || 0
    }
  } catch (e) {
    console.error('加载抽奖状态失败', e)
  }
}

const doLottery = async (drawType) => {
  if (lotteryData.value.drawing) return
  
  lotteryData.value.drawing = true
  lotteryData.value.rewards = []
  try {
    console.log('开始抽奖:', drawType)
    const res = await http.post('/announcement/lottery/draw', { draw_type: drawType })
    console.log('抽奖响应:', res)
    console.log('抽奖响应data:', res.data)
    
    if (res && res.data && res.data.ok) {
      lotteryData.value.rewards = res.data.rewards || []
      lotteryData.value.fragmentCount = res.data.fragment_count || 0
      lotteryData.value.drawCount = res.data.draw_count || 0
      lotteryData.value.yuanbao = res.data.yuanbao || 0
      
      // 保存结果到sessionStorage，跳转到结果页面
      sessionStorage.setItem('lottery_result', JSON.stringify({
        rewards: lotteryData.value.rewards,
        drawType: drawType
      }))
      router.push('/announcement/lottery-result')
    } else {
      console.log('抽奖失败:', res?.data)
      console.error(res?.data?.error || '抽奖失败')
    }
  } catch (e) {
    console.error('抽奖异常:', e)
    console.error('异常响应:', e.response)
    console.error(e.response?.data?.error || '抽奖失败，请重试')
  } finally {
    lotteryData.value.drawing = false
  }
}

const exchangeFragment = async (type) => {
  try {
    const res = await http.post('/announcement/lottery/exchange', { exchange_type: type })
    if (res.data.ok) {
      console.error(res.data.message)
      lotteryData.value.fragmentCount = res.data.fragment_count || 0
    } else {
      console.error(res.data.error || '兑换失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '兑换失败')
  }
}

// ==================== 铜钱圣典 ====================

const loadCopperBookStatus = async () => {
  try {
    const res = await http.get('/announcement/copper-book/status')
    if (res.data.ok) {
      copperBookData.value.boughtToday = res.data.bought_today || 0
      copperBookData.value.dailyLimit = res.data.daily_limit || 4
      copperBookData.value.canBuy = res.data.can_buy
      copperBookData.value.yuanbao = res.data.yuanbao || 0
    }
  } catch (e) {
    console.error('加载铜钱圣典状态失败', e)
  }
}

const buyCopperBook = async () => {
  if (copperBookData.value.buying) return
  if (!copperBookData.value.canBuy) {
    console.error('今日购买次数已达上限')
    return
  }
  
  copperBookData.value.buying = true
  try {
    const res = await http.post('/announcement/copper-book/buy')
    if (res.data.ok) {
      // 移除弹窗：console.error(res.data.message)
      copperBookData.value.boughtToday = res.data.bought_today || copperBookData.value.boughtToday + 1
      copperBookData.value.yuanbao = res.data.yuanbao || 0
      copperBookData.value.canBuy = copperBookData.value.boughtToday < copperBookData.value.dailyLimit
    } else {
      console.error(res.data.error || '购买失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '购买失败')
  } finally {
    copperBookData.value.buying = false
  }
}

// ==================== 声望助力庆典 ====================

const loadPrestigeStatus = async () => {
  try {
    const res = await http.get('/announcement/prestige/status')
    if (res.data.ok) {
      prestigeData.value.freeClaimed = res.data.free_claimed
      prestigeData.value.canClaimFree = res.data.can_claim_free
      prestigeData.value.boughtToday = res.data.bought_today || 0
      prestigeData.value.canBuy = res.data.can_buy
      prestigeData.value.yuanbao = res.data.yuanbao || 0
      prestigeData.value.level = res.data.level || 0
    }
  } catch (e) {
    console.error('加载声望助力状态失败', e)
  }
}

const claimPrestigeFree = async () => {
  if (prestigeData.value.claiming) return
  
  prestigeData.value.claiming = true
  try {
    const res = await http.post('/announcement/prestige/claim-free')
    if (res.data.ok) {
      // 移除弹窗：console.error(res.data.message)
      prestigeData.value.freeClaimed = true
      prestigeData.value.canClaimFree = false
    } else {
      console.error(res.data.error || '领取失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '领取失败')
  } finally {
    prestigeData.value.claiming = false
  }
}

const buyPrestigeBox = async () => {
  if (prestigeData.value.claiming) return
  if (!prestigeData.value.canBuy) {
    console.error('无法购买')
    return
  }
  
  prestigeData.value.claiming = true
  try {
    const res = await http.post('/announcement/prestige/buy-box')
    if (res.data.ok) {
      console.error(res.data.message)
      prestigeData.value.boughtToday = res.data.bought_today || prestigeData.value.boughtToday + 1
      prestigeData.value.yuanbao = res.data.yuanbao || 0
      prestigeData.value.canBuy = prestigeData.value.boughtToday < 4 && prestigeData.value.level <= 50
    } else {
      console.error(res.data.error || '购买失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '购买失败')
  } finally {
    prestigeData.value.claiming = false
  }
}

// ==================== 霸王龙预登场 ====================

const loadTyrannosaurusStatus = async () => {
  try {
    const res = await http.get('/announcement/tyrannosaurus/status')
    if (res.data.ok) {
      tyrannosaurusData.value.claimed = res.data.claimed
      tyrannosaurusData.value.canClaim = res.data.can_claim
      tyrannosaurusData.value.totalGems = res.data.total_gems || 0
      tyrannosaurusData.value.requiredGems = res.data.required_gems || 300
      tyrannosaurusData.value.level = res.data.level || 0
    }
  } catch (e) {
    console.error('加载霸王龙状态失败', e)
  }
}

const claimTyrannosaurusBall = async (ballLevel) => {
  if (tyrannosaurusData.value.claiming) return
  if (!ballLevel) {
    console.error('请选择召唤球等级')
    return
  }
  
  tyrannosaurusData.value.claiming = true
  try {
    const res = await http.post('/announcement/tyrannosaurus/claim', {
      ball_level: ballLevel
    })
    if (res.data.ok) {
      console.error(res.data.message)
      tyrannosaurusData.value.claimed = true
      tyrannosaurusData.value.canClaim = false
    } else {
      console.error(res.data.error || '领取失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '领取失败')
  } finally {
    tyrannosaurusData.value.claiming = false
  }
}

// ==================== 元宝返利 ====================

const loadRebateStatus = async () => {
  try {
    const res = await http.get('/announcement/rebate/status')
    if (res.data.ok) {
      rebateData.value.totalGems = res.data.total_gems || 0
      rebateData.value.tiers = res.data.tiers || []
    }
  } catch (e) {
    console.error('加载返利状态失败', e)
  }
}

const claimRebate = async (tierGems) => {
  if (rebateData.value.claiming) return
  
  rebateData.value.claiming = true
  try {
    const res = await http.post('/announcement/rebate/claim', { tier_gems: tierGems })
    if (res.data.ok) {
      console.error(res.data.message)
      // 刷新状态
      await loadRebateStatus()
    } else {
      console.error(res.data.error || '领取失败')
    }
  } catch (e) {
    console.error(e.response?.data?.error || '领取失败')
  } finally {
    rebateData.value.claiming = false
  }
}

// ==================== 通用方法 ====================

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}年${m}月${d}日`
}

// 返回首页
const goHome = () => router.push('/')

// 返回上一页
const goBack = () => router.back()

// 查看玩家
const viewPlayer = (userId) => {
  if (!userId) return
  router.push({ path: '/player/detail', query: { id: userId } })
}

onMounted(() => {
  loadAnnouncements()
})

// 监听路由变化
watch(() => route.params.id, () => {
  loadAnnouncements()
})
</script>

<template>
  <div class="announcement-detail-page">
    <!-- 加载中 -->
    <div class="section" v-if="loading">加载中...</div>
    
    <!-- 错误提示 -->
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>
    
    <!-- 公告内容 -->
    <template v-else-if="announcement">
      <!-- 标题 -->
      <div class="section title">【{{ announcement.title }}】</div>
      
      <!-- 活动时间 -->
      <div class="section time">
        活动时间：{{ formatDate(announcement.start_time) }} - {{ formatDate(announcement.end_time) }}
        <span v-if="announcement.duration_days">（{{ announcement.duration_days }}天时效）</span>
      </div>
      
      <!-- 活动简介 -->
      <div class="section intro">
        <span class="bold">活动简介：</span>{{ announcement.intro }}
      </div>
      
      <!-- 分隔线 -->
      <div class="divider"></div>
      
      <!-- 1. 新人战力榜排行 -->
      <template v-if="announcement.id === 'power_ranking'">
        <div class="section content">{{ announcement.content }}</div>
        
        <!-- 等级段切换 -->
        <div class="section bracket-tabs">
          <span v-for="bracket in [29, 39, 49, 59]" :key="bracket">
            <a 
              class="link" 
              :class="{ active: powerRankingData.currentBracket === bracket }"
              @click="switchBracket(bracket)"
            >{{ bracket }}级榜</a>
            <span v-if="bracket < 59"> | </span>
          </span>
        </div>
        
        <!-- 我的排名 -->
        <div class="section">
          我的排名：<span class="bold">{{ powerRankingData.myRank > 0 ? powerRankingData.myRank : '未上榜' }}</span>
        </div>
        
        <!-- 实时排行榜 -->
        <div class="section subtitle">{{ powerRankingData.currentBracket }}级战力排行榜（实时更新）</div>
        <div v-if="powerRankingData.loading" class="section">加载中...</div>
        <template v-else>
          <div v-if="!powerRankingData.rankings.length" class="section gray">暂无数据</div>
          <div v-for="player in powerRankingData.rankings" :key="player.rank" class="section rank-item">
            <span class="rank">{{ player.rank }}.</span>
            <a class="link username" @click="viewPlayer(player.userId)">{{ player.nickname }}</a>
            <span>（{{ player.level }}级）战力：<span class="gold">{{ player.power }}</span></span>
          </div>
          
          <!-- 分页 -->
          <div class="section pager" v-if="powerRankingData.totalPages > 1">
            <a class="link" @click="goToRankingPage(powerRankingData.currentPage - 1)" v-if="powerRankingData.currentPage > 1">上页</a>
            <span>{{ powerRankingData.currentPage }}/{{ powerRankingData.totalPages }}页</span>
            <a class="link" @click="goToRankingPage(powerRankingData.currentPage + 1)" v-if="powerRankingData.currentPage < powerRankingData.totalPages">下页</a>
          </div>
        </template>
        
        <!-- 奖励说明 -->
        <div class="divider"></div>
        <div class="section subtitle">奖励说明</div>
        <div v-for="ranking in announcement.rankings" :key="ranking.level" class="ranking-section">
          <div class="section">{{ ranking.name }}：</div>
          <div v-for="reward in ranking.rewards" :key="reward.rank" class="section indent reward-item">
            <span class="rank-label">{{ reward.rank }}：</span>{{ reward.items }}
          </div>
        </div>
        
        <!-- 活动结束状态提示 -->
        <div v-if="powerRankingData.isActivityEnded" class="section note-text">
          活动已结束，榜单已确定{{ powerRankingData.isFinalized ? '，奖励已发放' : '' }}
        </div>
      </template>
      
      <!-- 2. 开服轮盘抽奖 -->
      <template v-else-if="announcement.id === 'wheel_lottery'">
        <div class="section content">{{ announcement.content }}</div>
        
        <!-- 抽奖状态 -->
        <div class="section">
          当前元宝：<span class="gold">{{ lotteryData.yuanbao }}</span>
        </div>
        <div class="section">
          累计抽奖：<span class="bold">{{ lotteryData.drawCount }}</span>次，碎片数量：<span class="purple bold">{{ lotteryData.fragmentCount }}</span>
        </div>
        
        <!-- 抽奖操作 -->
        <div class="section">
          抽奖方式：
          <a class="link" @click="doLottery('single')" v-if="!lotteryData.drawing">单抽（600元宝）</a>
          <span class="gray" v-else>单抽（600元宝）</span>
          ｜
          <a class="link" @click="doLottery('ten')" v-if="!lotteryData.drawing">十连（5000元宝）</a>
          <span class="gray" v-else>十连（5000元宝）</span>
        </div>
        
        <!-- 碎片兑换 -->
        <div class="section subtitle">碎片兑换（当前碎片：{{ lotteryData.fragmentCount }}）：</div>
        <div v-for="(ex, idx) in announcement.exchange" :key="idx" class="section indent">
          {{ ex.cost }} → {{ ex.reward }} 
          <a class="link" @click="exchangeFragment(['earth','fire','water','wood','gold','god'][idx])">兑换</a>
        </div>
      </template>
      
      <!-- 3. 开服铜钱圣典 -->
      <template v-else-if="announcement.id === 'copper_book'">
        <div class="section content">
          <span class="bold">活动内容：</span>{{ announcement.content }}
        </div>
        
        <div class="section">
          当前元宝：<span class="gold">{{ copperBookData.yuanbao }}</span>
        </div>
        <div class="section">
          今日已购买：<span class="bold">{{ copperBookData.boughtToday }}/{{ copperBookData.dailyLimit }}</span>
        </div>
        <div class="section">
          价格：<span class="orange">{{ announcement.price }}{{ announcement.price_unit }}</span>，
          奖励：铜钱 <span class="gold">+{{ (announcement.reward_copper / 10000).toFixed(0) }}w</span>
        </div>
        
        <!-- 购买操作 -->
        <div class="section">
          铜钱圣典礼盒×1 
          <a class="link" @click="buyCopperBook" v-if="copperBookData.canBuy && !copperBookData.buying">购买</a>
          <span class="gray" v-else>{{ copperBookData.buying ? '购买中...' : '今日已达上限' }}</span>
        </div>
      </template>
      
      <!-- 4. 开服声望助力庆典 -->
      <template v-else-if="announcement.id === 'prestige_boost'">
        <div class="section">
          当前元宝：<span class="gold">{{ prestigeData.yuanbao }}</span>
        </div>

        <!-- 免费声望石 -->
        <div class="section">
          ①<a class="link" @click="claimPrestigeFree" v-if="!prestigeData.freeClaimed && !prestigeData.claiming">任务</a><span class="gray" v-else>{{ prestigeData.freeClaimed ? '已领取' : '领取中...' }}</span>
        </div>
        
        <!-- 购买声望礼盒 -->
        <div class="section">
          ②购买声望礼盒（50级及以下每天限购4个）：打开一个礼盒获得5000声望，一个礼盒2588元宝
        </div>
        <div class="section indent">
          今日已购买：{{ prestigeData.boughtToday }}/4 
          <a class="link" @click="buyPrestigeBox" v-if="prestigeData.canBuy && !prestigeData.claiming">购买</a>
          <span class="gray" v-else>{{ prestigeData.claiming ? '购买中...' : (prestigeData.level > 50 ? '等级超过50级' : '今日已达上限') }}</span>
        </div>
      </template>
      
      <!-- 5. 霸王龙（绝版）预登场助力开服 -->
      <template v-else-if="announcement.id === 'tyrannosaurus_preview'">
        <div class="section content">{{ announcement.content }}</div>
        
        <div class="section">
          累计赞助宝石：<span class="bold">{{ tyrannosaurusData.totalGems }}</span>，
          需要赞助：<span class="red bold">≥{{ tyrannosaurusData.requiredGems }}宝石</span>
        </div>
        <div class="section">
          当前等级：<span class="bold">{{ tyrannosaurusData.level }}级</span>
        </div>
        
        <div class="section subtitle">可选召唤球（只能选择领取其中一个）：</div>
        
        <div v-for="ball in announcement.balls" :key="ball.name" class="section indent">
          （玩家{{ ball.level_required }}级及以上才能打开使用）{{ ball.name }}×1 
          <template v-if="tyrannosaurusData.claimedBalls && tyrannosaurusData.claimedBalls[ball.level_required]">
            <span class="gray">已领取</span>
          </template>
          <template v-else-if="tyrannosaurusData.claimed">
            <span class="gray">已领取</span>
          </template>
          <template v-else>
            <a 
              class="link" 
              @click="claimTyrannosaurusBall(ball.level_required)" 
              v-if="tyrannosaurusData.totalGems >= tyrannosaurusData.requiredGems && !tyrannosaurusData.claiming"
            >领取</a>
            <span class="gray" v-else>{{ tyrannosaurusData.claiming ? '领取中...' : '赞助宝石不足' }}</span>
          </template>
        </div>
        
        <div class="section note-text">
          注意：转生功能未开启，玩家谨慎选择对应的等级段的霸王龙（绝版）召唤球
        </div>
      </template>
      
      <!-- 6. 开服元宝50%返利 -->
      <template v-else-if="announcement.id === 'yuanbao_rebate'">
        <div class="section content">{{ announcement.content }}</div>
        
        <div class="section">
          累计赞助宝石：<span class="bold">{{ rebateData.totalGems }}</span>
        </div>
        
        <div class="section subtitle">返利档位（每天刷新）：</div>
        <div v-for="tier in rebateData.tiers" :key="tier.gems_required" class="section indent">
          赞助满 <span class="red bold">{{ tier.gems_required }}宝石</span>：<span class="gold">{{ tier.yuanbao_reward }}元宝</span> 
          <a class="link" @click="claimRebate(tier.gems_required)" v-if="tier.can_claim && !rebateData.claiming">领取</a>
          <span class="gray" v-else>{{ tier.claimed ? '已领取' : (rebateData.claiming ? '领取中...' : '未达成') }}</span>
        </div>
      </template>
      
      <!-- 通用内容展示（兜底） -->
      <template v-else>
        <div class="section content">{{ announcement.content }}</div>
      </template>
      
      <!-- 分隔线 -->
      <div class="divider"></div>
      
      <!-- 导航 -->
      <div class="section nav-links">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section nav-links">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.announcement-detail-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.title {
  font-size: 15px;
  font-weight: bold;
  color: #CC3300;
  margin-bottom: 8px;
}

.time {
  color: #666666;
  font-size: 12px;
}

.intro {
  margin-top: 8px;
  color: #333333;
}

.divider {
  border-top: 1px dashed #CCCCCC;
  margin: 12px 0;
}

.subtitle {
  font-weight: bold;
  color: #0066CC;
  margin-top: 10px;
}

.content {
  margin-top: 8px;
}

.indent {
  padding-left: 12px;
}

.bracket-tabs {
  margin: 10px 0;
}

.bracket-tabs .link {
  padding: 2px 8px;
}

.bracket-tabs .link.active {
  color: #CC3300;
  font-weight: bold;
}

.ranking-section {
  margin-top: 10px;
}

.reward-item {
  margin: 2px 0;
}

.rank-item {
  margin: 4px 0;
}

.rank {
  display: inline-block;
  min-width: 25px;
  font-weight: bold;
  color: #CC6600;
}

.rank-label {
  font-weight: bold;
  color: #CC6600;
}

.reward-block {
  margin: 6px 0;
}

.reward-desc {
  color: #008800;
  padding-left: 12px;
}

.note {
  color: #999999;
  font-size: 11px;
  padding-left: 12px;
}

.price {
  padding-left: 12px;
}

.ball-item {
  margin: 4px 0;
}

.ball-name {
  color: #9933FF;
  font-weight: bold;
}

.level-req {
  color: #666666;
  font-size: 11px;
}

.tier-item {
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.note-text {
  color: #CC0000;
  font-size: 11px;
  margin-top: 8px;
}

.status-box {
  background: #ffffff;
  border: 1px solid #DDD;
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 4px;
}

.status-box div {
  margin: 2px 0;
}

.action-buttons {
  margin: 10px 0;
  display: flex;
  gap: 10px;
}

.exchange-list {
  margin: 8px 0;
}

.exchange-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 12px;
  border-bottom: 1px dashed #eee;
}

.reward-result {
  background: #ffffff;
  border: 1px solid #DDD;
  padding: 8px 12px;
  margin: 10px 0;
  border-radius: 4px;
}

.pager {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.bold {
  font-weight: bold;
}

.red {
  color: #CC0000;
}

.orange {
  color: #FF6600;
}

.gold {
  color: #CC9900;
  font-weight: bold;
}

.purple {
  color: #9933FF;
}

.gray {
  color: #999999;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.username {
  color: #CC0000;
}

.nav-links {
  margin-top: 8px;
}

.btn {
  padding: 6px 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-primary {
  background: #1E90FF;
  color: white;
  border-color: #1E90FF;
}

.btn-primary:hover {
  background: #1873CC;
}

.btn-gold {
  background: #FFD700;
  color: #333;
  border-color: #DAA520;
}

.btn-gold:hover {
  background: #FFC700;
}

.btn-disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
}

.btn-small {
  padding: 2px 10px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

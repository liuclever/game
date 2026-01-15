<script setup>
import { ref, onMounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const allianceData = ref(null)
const creationMode = ref(false)
const allianceName = ref('')
const activities = ref([])
const activityLoading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const ROLE_LABELS = {
  1: '盟主',
  2: '副盟主',
  3: '长老',
  0: '盟众',
}

const roleLabel = (role) => ROLE_LABELS[role] || '盟众'

const fetchActivities = async () => {
  if (!allianceData.value) {
    activities.value = []
    return
  }
  activityLoading.value = true
  try {
    const res = await http.get('/alliance/activities', { params: { limit: 6 } })
    if (res.data.ok) {
      activities.value = res.data.activities || []
    } else {
      activities.value = []
    }
  } catch (err) {
    console.error('获取联盟动态失败', err)
    activities.value = []
  } finally {
    activityLoading.value = false
  }
}

const fetchAllianceInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/my')
    if (res.data.ok) {
      allianceData.value = res.data
      await fetchActivities()
    } else {
      allianceData.value = null
      activities.value = []
      // 如果错误是"未加入联盟"，不显示为错误，而是显示创建/加入选项
      const error = res.data.error || '获取联盟信息失败'
      if (error === '未加入联盟') {
        errorMsg.value = ''  // 清空错误信息，让页面显示创建/加入选项
      } else {
        errorMsg.value = error
      }
    }
  } catch (e) {
    console.error('获取联盟信息失败', e)
    allianceData.value = null
    activities.value = []
    const error = e.response?.data?.error || '网络错误，请稍后重试'
    // 如果错误是"未加入联盟"，不显示为错误
    if (error === '未加入联盟') {
      errorMsg.value = ''
    } else {
      errorMsg.value = error
    }
  } finally {
    loading.value = false
  }
}

const createAlliance = async () => {
    if (!allianceName.value.trim()) {
        errorMsg.value = '请输入联盟名称'
        setTimeout(() => { errorMsg.value = '' }, 3000)
        return
    }
    try {
        const res = await http.post('/alliance/create', { name: allianceName.value })
        if (res.data.ok) {
            successMsg.value = '联盟创建成功！'
            creationMode.value = false
            allianceName.value = ''
            // 3秒后清除成功消息并刷新数据
            setTimeout(() => {
                successMsg.value = ''
                fetchAllianceInfo()
            }, 2000)
        } else {
            errorMsg.value = res.data.error || '创建失败'
            setTimeout(() => { errorMsg.value = '' }, 3000)
        }
    } catch (e) {
        errorMsg.value = e.response?.data?.error || '创建失败'
        setTimeout(() => { errorMsg.value = '' }, 3000)
    }
}

const goBack = () => {
  router.push('/')
}

const goToChat = () => {
  router.push('/alliance/chat')
}

const goToRename = () => {
  router.push('/alliance/rename')
}

const goToCouncil = () => {
  router.push('/alliance/council')
}

const goToNotice = () => {
  router.push('/alliance/notice')
}

const goToMembers = () => {
  router.push('/alliance/members')
}

const goToWar = () => {
  router.push('/alliance/war')
}

const goToWarHonor = () => {
  router.push('/alliance/war/honor')
}

const goToTalent = () => {
  // 功能已禁用，仅保留文字显示
  // router.push('/alliance/talent')
}

const goToHall = () => {
  router.push('/alliance/hall')
}

const goToTrainingGround = () => {
  router.push('/alliance/training-ground')
}

const goToTrainingIntro = () => {
  router.push('/alliance/training-intro')
}

const goToWarehouse = () => {
  // 物资库点击直接跳转到捐献页面
  router.push('/alliance/donate')
}

const goToItemStorage = () => {
  router.push('/alliance/item-storage')
}

const goToBeastStorage = () => {
  router.push('/alliance/beast-storage')
}

const goToBarracks = () => {
  router.push('/alliance/barracks')
}

const goToTeam = () => {
  // 功能已禁用，仅保留文字显示
  // router.push('/alliance/team')
}

const goToSacredBeast = () => {
  // 功能已禁用，仅保留文字显示
  // router.push('/alliance/sacred-beast')
}

const goToCompetition = () => {
  // 功能已禁用，仅保留文字显示
  // router.push('/alliance/competition')
}

const claimFireOre = async () => {
  // 如果已领取，不允许再次领取
  if (allianceData.value?.fire_ore_claimed_today) {
    return
  }
  
  try {
    const res = await http.post('/alliance/fire-ore/claim')
    if (res.data.ok) {
      // 跳转到成功页面，返回时会自动刷新数据
      router.push({
        path: '/alliance/fire-ore/success',
        query: {
          itemName: res.data.item_name || '火能原石'
        }
      })
    } else {
      // 错误也跳转到提示页面（可以创建错误提示页面，或使用当前页面显示错误）
      router.push({
        path: '/alliance/fire-ore/success',
        query: {
          error: res.data.error || '领取失败'
        }
      })
    }
  } catch (e) {
    console.error('领取火能原石失败', e)
    router.push({
      path: '/alliance/fire-ore/success',
      query: {
        error: e.response?.data?.error || '领取失败，请稍后再试'
      }
    })
  }
}

const activityText = (activity) => {
  const actor = activity.actorName || (activity.actorUserId ? `玩家${activity.actorUserId}` : '')
  const target = activity.targetName || (activity.targetUserId ? `玩家${activity.targetUserId}` : '')
  switch (activity.type) {
    case 'create':
      return `${actor} 创建联盟`
    case 'join':
      return `${actor} 加入联盟`
    case 'kick':
      return target ? `${target} 被踢出联盟` : `${actor} 管理员执行了踢出操作`
    case 'leave':
      return `${actor} 退出联盟`
    case 'donate':
      const itemName = activity.itemName || ''
      const quantity = activity.itemQuantity || 0
      if (itemName && quantity > 0) {
        return `${actor} 捐献 ${quantity}x ${itemName}`
      }
      return `${actor} 进行了捐献`
    default:
      return `${actor} 进行了 ${activity.type} 操作`
  }
}

onMounted(() => {
  fetchAllianceInfo()
  // 检查路由参数
  if (route.query.refresh === '1') {
    // 如果已经有刷新参数，立即刷新
    setTimeout(() => {
      fetchAllianceInfo()
      router.replace({ path: '/alliance' })
    }, 200)
  }
})

// 监听路由变化，当从成功页面返回时刷新数据
watch(() => route.query.refresh, (newVal, oldVal) => {
  if (newVal === '1' && oldVal !== '1') {
    // 当刷新参数变为 '1' 时，刷新数据
    fetchAllianceInfo()
    // 清除refresh参数，避免重复刷新
    router.replace({ path: '/alliance' })
  }
})

// 监听路由路径变化，确保从其他页面返回时刷新数据
watch(() => route.path, (newPath, oldPath) => {
  // 当路由路径变为 /alliance 时，检查是否需要刷新
  if (newPath === '/alliance' && oldPath !== '/alliance') {
    // 如果是从成功页面返回（有refresh参数），刷新数据
    if (route.query.refresh === '1') {
      fetchAllianceInfo()
      router.replace({ path: '/alliance' })
    } else {
      // 即使没有refresh参数，也刷新一次，确保数据是最新的
      fetchAllianceInfo()
    }
  }
})

// 当从其他页面返回时，刷新数据（用于 keep-alive 的情况）
onActivated(() => {
  // 每次激活页面时都刷新数据，确保状态是最新的
  fetchAllianceInfo()
  // 如果有refresh参数，清除它
  if (route.query.refresh === '1') {
    router.replace({ path: '/alliance' })
  }
})
</script>

<template>
  <div class="alliance-page">
    <div v-if="loading" class="section">加载中...</div>
    <template v-else>
      <div v-if="successMsg" class="section success-message">{{ successMsg }}</div>
      <div v-if="errorMsg" class="section error">{{ errorMsg }}</div>
      
      <template v-if="allianceData">
      <!-- 联盟主界面 -->
      <div class="section nav">
        <span class="active">我的联盟</span> | <span class="link" @click="goToHall">联盟大厅</span> | <span class="link" @click="goToWar">盟战</span>
      </div>
      
      <div class="section alliance-header">
        <span class="alliance-icon">♆</span> 
        <span class="alliance-name">{{ allianceData.alliance.name }}</span>
        <span class="alliance-level">({{ allianceData.alliance.level }}/10级)</span>
        <a class="link small" @click.prevent="goToRename">修改</a>
      </div>

      <div class="section info">
        <div>成员:{{ allianceData.member_count }}/{{ allianceData.member_capacity || 10 }}</div>
        <div>职位: {{ roleLabel(allianceData.member_info.role) }}</div>
        <div>贡献: {{ allianceData.member_info.contribution }}/57</div>
      </div>

      <div class="section notice" @click="goToNotice">
        <div class="label link">公告:</div>
        <div class="content link">{{ allianceData.alliance.notice || '点击设置公告' }}</div>
      </div>

        <div class="section quick-links">
          <span class="disabled-text">联盟争霸赛: 签到激活阶段</span><br>
          <a class="link" @click="goToWarHonor">战功兑换</a>. <a class="link" @click="goToChat">进入聊天室</a>
        </div>


      <div class="section-group">
        <div class="group-title">【火能修行】 <a class="link small" @click.prevent="goToTrainingIntro">简介</a></div>
        <div class="group-content">
          火能原石: 
          <span v-if="allianceData && allianceData.fire_ore_claimed_today" class="claimed-text">已领取</span>
          <a v-else-if="allianceData" class="link" @click="claimFireOre">领取</a>
          <span v-else>加载中...</span><br>
          修行广场: <a class="link" @click="goToTrainingGround">进入</a>
        </div>
      </div>

      <div class="section-group">
        <div class="group-title">【联盟建筑】</div>
        <div class="group-content building-links">
          <div><a class="link" @click="goToCouncil">议事厅</a>. <a class="link" @click="goToBeastStorage">幻兽室</a>. <span class="disabled-text">天赋池</span></div>
          <div><a class="link" @click="goToWarehouse">物资库</a>. <a class="link" @click="goToBarracks">兵营</a>. <span class="disabled-text">圣兽山</span></div>
          <div><span class="disabled-text">精英战队</span>. <a class="link" @click="goToItemStorage">寄存仓库</a></div>
        </div>
      </div>

      <div class="section-group">
        <div class="group-title">【联盟动态】 <a class="link small">更多</a></div>
        <div class="group-content dynamic-list">
          <div v-if="activityLoading" class="dynamic-item">加载动态中...</div>
          <template v-else-if="activities.length">
            <div
              v-for="(activity, index) in activities"
              :key="activity.id || index"
              class="dynamic-item"
            >
              {{ index + 1 }}.({{ activity.timeText }})
              <span class="blue">{{ activityText(activity) }}</span>
            </div>
          </template>
          <div v-else class="dynamic-item">暂无联盟动态</div>
        </div>
      </div>

      <div class="section bottom-nav">
        <a class="link" @click="goBack">返回游戏首页</a>
      </div>
      </template>

      <template v-else-if="!errorMsg">
        <div v-if="!creationMode">
          <div class="section">你还没有加入任何联盟</div>
          <div class="section">
            <button class="btn" @click="creationMode = true">创建联盟</button>
            <button class="btn" @click="goToHall">寻找联盟</button>
          </div>
          <div class="section requirement">
              创建条件：玩家拥有1个盟主证明，玩家等级达到30级或以上
          </div>
          <div class="section">
              <a class="link" @click="goBack">返回首页</a>
          </div>
        </div>

        <div v-else>
          <div class="section title">【创建联盟】</div>
          <div class="section">
            请输入联盟名称：
            <input v-model="allianceName" type="text" class="input" placeholder="最多6个汉字" maxlength="12" />
          </div>
          <div class="section">
            <button class="btn confirm" @click="createAlliance">确认创建</button>
            <button class="btn cancel" @click="creationMode = false">取消</button>
          </div>
          <div class="section cost">
            创建将消耗 1x 盟主证明
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.alliance-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 6px 0;
}

.nav {
  border-bottom: 1px solid #CCC;
  padding-bottom: 4px;
}

.nav .active {
  font-weight: bold;
  color: #000;
}

.alliance-header {
  color: #8B4513;
  font-weight: bold;
  font-size: 17px;
}

.alliance-name {
    margin: 0 4px;
}

.alliance-level {
    color: #666;
    font-weight: normal;
    font-size: 18px;
}

.info {
  border-bottom: 1px dashed #CCC;
  padding-bottom: 6px;
}

.notice .label {
  color: #0066CC;
}

.section-group {
    margin-top: 15px;
}

.group-title {
    font-weight: bold;
}

.claimed-text {
  color: #666;
  font-style: italic;
}

.group-content {
    padding-left: 8px;
}

.link {
  color: #0066CC;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.small {
  font-size: 17px;
}

.blue { color: #0066CC; }

.disabled-text {
  color: #999;
  cursor: default;
}

.btn {
  padding: 4px 12px;
  margin-right: 8px;
  cursor: pointer;
}

.input {
  padding: 4px;
  border: 1px solid #CCC;
  margin-top: 4px;
}

.requirement, .cost {
    font-size: 18px;
    color: #CC3300;
}

.error {
    color: #CC0000;
    font-weight: bold;
    padding: 12px;
    background: #FFEEEE;
    border: 1px solid #CC0000;
    border-radius: 4px;
}

.success-message {
    color: #155724;
    font-weight: bold;
    padding: 12px;
    background: #D4EDDA;
    border: 1px solid #28A745;
    border-radius: 4px;
    margin-bottom: 12px;
}

.footer-nav {
    margin-top: 20px;
}
</style>

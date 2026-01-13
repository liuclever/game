<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const allianceData = ref(null)
const creationMode = ref(false)
const allianceName = ref('')
const activities = ref([])
const activityLoading = ref(false)

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
  try {
    const res = await http.get('/alliance/my')
    if (res.data.ok) {
      allianceData.value = res.data
      await fetchActivities()
    } else {
      allianceData.value = null
      activities.value = []
    }
  } catch (e) {
    console.error('获取联盟信息失败', e)
    allianceData.value = null
    activities.value = []
  } finally {
    loading.value = false
  }
}

const createAlliance = async () => {
    if (!allianceName.value.trim()) {
        showMessage('请输入联盟名称', 'info')
        return
    }
    try {
        const res = await http.post('/alliance/create', { name: allianceName.value })
        if (res.data.ok) {
            showMessage('联盟创建成功！', 'success')
            creationMode.value = false
            fetchAllianceInfo()
        } else {
            showMessage(res.data.error || '创建失败', 'error')
        }
    } catch (e) {
        showMessage(e.response?.data?.error || '创建失败', 'error')
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

const goToTalent = () => {
  router.push('/alliance/talent')
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
  router.push('/alliance/warehouse')
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
  router.push('/alliance/team')
}

const goToSacredBeast = () => {
  router.push('/alliance/sacred-beast')
}

const activityText = (activity) => {
  const actor = activity.actorName || `玩家${activity.actorUserId || ''}`
  const target = activity.targetName || (activity.targetUserId ? `玩家${activity.targetUserId}` : '')
  switch (activity.type) {
    case 'join':
      return `${actor} 加入联盟`
    case 'kick':
      return target ? `${target} 被踢出联盟` : `${actor} 管理员执行了踢出操作`
    case 'leave':
      return `${actor} 退出联盟`
    case 'donate':
      return `${actor} 捐献 ${activity.itemQuantity || 0}x ${activity.itemName || ''}`
    default:
      return `${actor} 进行了 ${activity.type} 操作`
  }
}

onMounted(() => {
  fetchAllianceInfo()
})
</script>

<template>
  <div class="alliance-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading" class="section">加载中...</div>
    
    <template v-else-if="allianceData">
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
        <div>成员:{{ allianceData.member_count }}/30 </div>
        <div>职位: {{ roleLabel(allianceData.member_info.role) }}</div>
        <div>贡献: {{ allianceData.member_info.contribution }}/57</div>
      </div>

      <div class="section notice" @click="goToNotice">
        <div class="label link">公告:</div>
        <div class="content link">{{ allianceData.alliance.notice || '点击设置公告' }}</div>
      </div>

        <div class="section quick-links">
          <a class="link">联盟争霸赛: 签到激活阶段</a><br>
          <a class="link">战功兑换</a>. <a class="link" @click="goToChat">进入聊天室</a>
        </div>


      <div class="section-group">
        <div class="group-title">【火能修行】 <a class="link small" @click.prevent="goToTrainingIntro">简介</a></div>
        <div class="group-content">
          火能原石: <a class="link">领取</a> (消耗5贡献) (今天周日火修效果翻倍)<br>
          修行广场: <a class="link" @click="goToTrainingGround">进入</a>
        </div>
      </div>

      <div class="section-group">
        <div class="group-title">【联盟建筑】</div>
        <div class="group-content building-links">
          <a class="link" @click="goToCouncil">议事厅</a>. <a class="link" @click="goToBeastStorage">幻兽室</a>. <a class="link" @click="goToTalent">天赋池</a><br>
          <a class="link" @click="goToWarehouse">物资库</a>. <a class="link" @click="goToBarracks">兵营</a>. <a class="link" @click="goToSacredBeast">圣兽山</a><br>
          <a class="link" @click="goToTeam">精英战队</a>. <a class="link" @click="goToItemStorage">寄存仓库</a>
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

    <template v-else>
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
  </div>
</template>

<style scoped>
.alliance-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
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
  font-size: 14px;
}

.alliance-name {
    margin: 0 4px;
}

.alliance-level {
    color: #666;
    font-weight: normal;
    font-size: 12px;
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
  font-size: 11px;
}

.blue { color: #0066CC; }

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
    font-size: 12px;
    color: #CC3300;
}

.footer-nav {
    margin-top: 20px;
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

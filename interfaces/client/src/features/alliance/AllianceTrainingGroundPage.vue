<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const info = ref(null)
const errorMsg = ref('')

const fetchTrainingInfo = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await http.get('/alliance/training-ground')
    if (res.data?.ok) {
      info.value = res.data
    } else {
      info.value = null
      errorMsg.value = res.data?.error || '获取修行信息失败'
    }
  } catch (err) {
    console.error('获取修行信息失败', err)
    info.value = null
    errorMsg.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

const canCreateRoom = computed(() => {
  if (!info.value) return false
  return !info.value.hasJoinedToday && info.value.hasFireOre
})

const practiceStatus = computed(() => {
  if (!info.value) return '未修行'
  return info.value.practiceStatus || '未修行'
})

const claimFireOre = async () => {
  if (saving.value) return
  saving.value = true
  try {
    const res = await http.post('/alliance/fire-ore/claim')
    if (res.data?.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/fire-ore/success',
        query: {
          itemName: res.data.item_name || '火能原石'
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/fire-ore/success',
        query: {
          error: res.data?.error || '领取失败'
        }
      })
    }
  } catch (err) {
    // 跳转到失败页面
    router.push({
      path: '/alliance/fire-ore/success',
      query: {
        error: err.response?.data?.error || '领取失败，请稍后再试'
      }
    })
  } finally {
    saving.value = false
  }
}

const goToCreateRoom = () => {
  if (!canCreateRoom.value) {
    if (!info.value.hasFireOre) {
      alert('需要火能原石才能进行修行，请先领取火能原石')
    }
    return
  }
  router.push('/alliance/training-ground/create')
}

const joinRoom = async (roomId) => {
  if (saving.value) return
  saving.value = true
  try {
    const res = await http.post('/alliance/training-ground/rooms/join', { roomId })
    if (!res.data?.ok) {
      alert(res.data?.error || '加入失败')
    } else {
      await fetchTrainingInfo()
    }
  } catch (err) {
    alert(err.response?.data?.error || '加入失败')
  } finally {
    saving.value = false
  }
}

const endTraining = async (roomId) => {
  if (saving.value) return
  saving.value = true
  try {
    const res = await http.post('/alliance/training-ground/end', { roomId })
    if (!res.data?.ok) {
      alert(res.data?.error || '结束修行失败')
    } else {
      alert(res.data?.message || '修行已结束')
      await fetchTrainingInfo()
    }
  } catch (err) {
    alert(err.response?.data?.error || '结束修行失败')
  } finally {
    saving.value = false
  }
}

const claimReward = async (participantId) => {
  if (saving.value) return
  saving.value = true
  try {
    const res = await http.post('/alliance/training-ground/claim', { participantId })
    if (!res.data?.ok) {
      alert(res.data?.error || '领取失败')
    } else {
      alert(`成功领取焚火晶 ${res.data.reward} 个（焚火炉${res.data.furnaceLevel}级）`)
      await fetchTrainingInfo()
    }
  } catch (err) {
    alert(err.response?.data?.error || '领取失败')
  } finally {
    saving.value = false
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const getRoomStatus = (room) => {
  return room.statusLabel || '未知'
}

const viewPlayerProfile = (userId) => {
  if (!userId) return
  router.push(`/player/profile?id=${userId}`)
}

onMounted(() => {
  fetchTrainingInfo()
})
</script>

<template>
  <div class="training-ground-page">
    <div v-if="loading">加载中...</div>
    <div v-else-if="errorMsg">{{ errorMsg }}</div>
    <template v-else-if="info">
      <div class="title">【修行广场】</div>
      
      <!-- 火能原石状态 -->
      <div class="section">
        <div>火能原石: {{ info.hasFireOre ? `有(${info.fireOreCount}个)` : '无' }}</div>
        <div v-if="!info.hasClaimedFireOreToday && !info.hasFireOre">
          <a class="link" @click="claimFireOre">领取火能原石（消耗{{ info.contributionCost }}贡献值）</a>
        </div>
        <div v-else-if="info.hasClaimedFireOreToday && !info.hasFireOre">
          <span class="hint">今日已领取，但已消耗</span>
        </div>
        <div v-else-if="info.hasClaimedFireOreToday">
          <span class="hint">今日已领取</span>
        </div>
      </div>
      
      <!-- 修行信息 -->
      <div class="section">
        <div>修行状态: {{ practiceStatus }}</div>
        <div>焚火炉等级: {{ info.furnaceLevel }}级</div>
        <div>预期奖励: {{ info.expectedReward }}个焚火晶</div>
        <div>开始条件: 至少{{ info.minParticipants }}人</div>
      </div>
      
      <!-- 创建房间 -->
      <div class="section">
        <template v-if="canCreateRoom">
          <a class="link" @click="goToCreateRoom">创建修行房间</a>
        </template>
        <div v-else-if="info.hasJoinedToday" class="hint">今日已修行</div>
        <div v-else-if="!info.hasFireOre" class="hint">需要火能原石才能创建房间</div>
      </div>
      
      <!-- 房间列表 -->
      <div v-if="info.rooms && info.rooms.length > 0" class="section">
        <div v-for="(room, idx) in info.rooms" :key="room.roomId" class="room-item">
          <div class="room-header">
            {{ idx + 1 }}. {{ room.title }} 
            <span class="status-badge" :class="room.status">{{ room.statusLabel }}</span>
            ({{ room.participantCount }}/{{ room.maxParticipants }})
            <span class="duration-info">【2小时，消耗1个火能原石】</span>
          </div>
          
          <!-- 参与者列表 -->
          <div v-if="room.participants && room.participants.length > 0" class="participants">
            <template v-for="(p, pIdx) in room.participants" :key="p.participantId">
              <a v-if="p.userId" class="link" @click="viewPlayerProfile(p.userId)">{{ p.nickname }}</a>
              <span v-else>{{ p.nickname }}</span>
              <span v-if="p.isSelf">（我）</span>
              <span v-if="p.claimed" class="claimed">[已领取]</span>
              <span v-if="pIdx < room.participants.length - 1">, </span>
            </template>
          </div>
          
          <!-- 操作按钮 -->
          <div class="room-actions">
            <template v-if="room.canJoin">
              <a class="link" @click="joinRoom(room.roomId)">加入房间</a>
            </template>
            <template v-if="room.canEnd">
              <a class="link" @click="endTraining(room.roomId)">结束修行</a>
            </template>
            <template v-for="p in room.participants" :key="p.participantId">
              <template v-if="p.isSelf && p.canClaim">
                <a class="link" @click="claimReward(p.participantId)">领取奖励</a>
              </template>
            </template>
          </div>
          
          <!-- 结束时间 -->
          <div v-if="room.endsAt" class="room-time">
            结束时间: {{ room.endsAt }}
          </div>
        </div>
      </div>
      
      <div class="section spacer">
        <a class="link" @click="goBackAlliance">返回联盟</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    <div v-else>尚未加入联盟，无法进入修行广场</div>
  </div>
</template>

<style scoped>
.training-ground-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 8px;
}

.section {
  margin: 12px 0;
}

.spacer {
  margin-top: 20px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.hint {
  color: #666;
  font-size: 18px;
}

.room-item {
  margin: 12px 0;
  padding: 8px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.room-header {
  font-weight: bold;
  margin-bottom: 4px;
}

.status-badge {
  display: inline-block;
  padding: 2px 6px;
  margin-left: 8px;
  border-radius: 3px;
  font-size: 18px;
  font-weight: normal;
}

.status-badge.waiting {
  background: #ffffff;
  color: #856404;
}

.status-badge.ongoing {
  background: #ffffff;
  color: #0c5460;
}

.status-badge.completed {
  background: #ffffff;
  color: #155724;
}

.participants {
  margin: 4px 0;
  color: #333;
}

.claimed {
  color: #28a745;
  font-weight: bold;
}

.room-actions {
  margin: 8px 0;
}

.room-time {
  margin-top: 4px;
  font-size: 18px;
  color: #666;
}

.duration-info {
  margin-left: 8px;
  font-size: 18px;
  color: #FF6600;
  font-weight: bold;
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const info = ref(null)
const errorMsg = ref('')
const joinLoadingRoom = ref(null)
const claimLoadingId = ref(null)

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
  return !info.value.hasJoinedToday
})

const practiceStatus = computed(() => info.value?.practiceStatus || '已结束')

const createRoom = async () => {
  if (!canCreateRoom.value || saving.value) return
  const title = prompt('请输入修行房间名称（可选）', '焚天炉')
  saving.value = true
  try {
    const res = await http.post('/alliance/training-ground/rooms', { title })
    if (!res.data?.ok) {
      alert(res.data?.error || '创建修行房间失败')
    } else {
      await fetchTrainingInfo()
    }
  } catch (err) {
    alert(err.response?.data?.error || '创建修行房间失败')
  } finally {
    saving.value = false
  }
}

const joinRoom = async (roomId) => {
  joinLoadingRoom.value = roomId
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
    joinLoadingRoom.value = null
  }
}

const claimReward = async (participantId) => {
  claimLoadingId.value = participantId
  try {
    const res = await http.post('/alliance/training-ground/claim', { participantId })
    if (!res.data?.ok) {
      alert(res.data?.error || '领取失败')
    } else {
      alert(`成功领取焚火晶 ${res.data.reward} 个`)
      await fetchTrainingInfo()
    }
  } catch (err) {
    alert(err.response?.data?.error || '领取失败')
  } finally {
    claimLoadingId.value = null
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchTrainingInfo()
})
</script>

<template>
  <div class="training-ground-page">
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    <template v-else-if="info">
      <div class="section title">【修行广场】</div>
      <div class="section status">
        修行状态：<strong>{{ practiceStatus }}</strong>
        <span class="inline-tip">（每次修行需 {{ info.trainingDurationMinutes }} 分钟，1日限 {{ info.dailyLimit }} 次）</span>
      </div>
      <div class="section summary">
        联盟等级：{{ info.allianceLevel }} 级 ｜ 当前焚火晶：{{ info.allianceCrystals }}<br>
        今日修行次数：{{ info.hasJoinedToday ? '已达上限' : '尚可参与' }}
      </div>
      <div class="section actions">
        <button class="btn" :disabled="saving || !canCreateRoom" @click="createRoom">
          {{ canCreateRoom ? '创建修行房间' : '今日已修行' }}
        </button>
        <button class="btn secondary" @click="fetchTrainingInfo">刷新</button>
      </div>

      <div class="section rooms">
        <div class="rooms-title">修行房间列表</div>
        <template v-if="info.rooms?.length">
          <div v-for="room in info.rooms" :key="room.roomId" class="room-item">
            <div class="room-header">
              <div>
                {{ room.index }}、{{ room.title }}
                <span class="status-tag" :class="room.status">{{ room.statusLabel }}</span>
              </div>
              <div class="room-meta">
                {{ room.participantCount }}/{{ room.maxParticipants }} 人 ｜ 创建：{{ room.createdAt || '未知' }} ｜ 结束：{{ room.endsAt || '计算中' }}
              </div>
            </div>
            <div class="participants">
              <div class="participant-row" v-for="p in room.participants" :key="p.participantId">
                <span :class="{ self: p.isSelf }">
                  {{ p.nickname }}<span v-if="p.isSelf">（我）</span>
                </span>
                <span class="light-text">{{ p.joinedAt || '' }}</span>
                <span class="reward" v-if="p.rewardAmount">焚火晶：{{ p.rewardAmount }}</span>
                <button
                  v-if="p.canClaim"
                  class="btn small"
                  :disabled="claimLoadingId === p.participantId"
                  @click="claimReward(p.participantId)"
                >
                  {{ claimLoadingId === p.participantId ? '领取中...' : '领取奖励' }}
                </button>
                <span v-else class="light-text" v-if="p.claimed">已领取</span>
              </div>
            </div>
            <div class="room-actions">
              <button
                v-if="room.canJoin"
                class="btn primary"
                :disabled="joinLoadingRoom === room.roomId"
                @click="joinRoom(room.roomId)"
              >
                {{ joinLoadingRoom === room.roomId ? '加入中...' : '加入修行' }}
              </button>
              <span v-else class="light-text">
                <template v-if="room.isFull">房间已满</template>
                <template v-else-if="room.status === 'completed'">修行已结束</template>
                <template v-else>已加入</template>
              </span>
            </div>
          </div>
        </template>
        <div v-else class="empty">暂未有修行房间，快来创建第一间吧！</div>
      </div>

      <div class="section tip-box">
        提示：修行奖励随联盟等级提升，每升一级额外 +2 个焚火晶；若同时修行人数 ≥ 2，则额外再 +2。
      </div>

      <div class="section nav">
        <a class="link" @click="goBackAlliance">返回联盟</a><br />
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>

    </template>
    <div v-else class="section">尚未加入联盟，无法进入修行广场</div>
  </div>
</template>

<style scoped>
.training-ground-page {
  background: #fffef6;
  min-height: 100vh;
  padding: 12px 18px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #4a2b05;
}

.status {
  color: #5c330a;
}

.summary {
  background: #fff5da;
  border: 1px dashed #e4c38a;
  padding: 8px 10px;
  border-radius: 4px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.rooms {
  border: 1px solid #e2d3aa;
  background: #fffaf0;
  padding: 12px 12px;
  border-radius: 6px;
}

.rooms-title {
  font-weight: bold;
  margin-bottom: 6px;
}

.room-item {
  border: 1px solid #ead9b6;
  border-radius: 6px;
  padding: 10px;
  background: #fff;
  margin-bottom: 10px;
}

.room-header {
  font-weight: bold;
  color: #4a2b05;
}

.room-meta {
  font-weight: normal;
  color: #7a643c;
  font-size: 12px;
  margin-top: 4px;
}

.status-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  margin-left: 6px;
}

.status-tag.ongoing {
  background: #fff4d6;
  color: #b45a00;
  border: 1px solid #f4c985;
}

.status-tag.completed {
  background: #e3f7d4;
  color: #2c7a2c;
  border: 1px solid #b1d8a4;
}

.participants {
  margin-top: 8px;
  border-top: 1px dashed #ead9b6;
  padding-top: 8px;
}

.participant-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  flex-wrap: wrap;
}

.participant-row .self {
  color: #c0392b;
}

.reward {
  color: #a65c00;
  font-size: 12px;
}

.room-actions {
  margin-top: 8px;
  text-align: right;
}

.btn {
  background: #c57900;
  border: none;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.secondary {
  background: #7f8c8d;
}

.btn.primary {
  background: #c45f00;
}

.btn.small {
  font-size: 12px;
  padding: 3px 8px;
}

.tip-box {
  font-size: 12px;
  color: #8a4a12;
  background: #fff1dd;
  border-left: 3px solid #d07900;
  padding: 6px 8px;
}

.empty {
  color: #777;
  text-align: center;
  padding: 16px 0;
}

.nav {
  margin-top: 12px;
}

.footer-info {
  margin-top: 18px;
  font-size: 11px;
  color: #777;
  border-top: 1px solid #ddd;
  padding-top: 8px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.inline-tip {
  font-size: 12px;
  color: #7a7a7a;
  margin-left: 6px;
}

.light-text {
  color: #999;
  font-size: 12px;
}

.error {
  color: #c0392b;
}
</style>

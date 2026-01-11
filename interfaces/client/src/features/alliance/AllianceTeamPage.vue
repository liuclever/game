<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const info = ref(null)
const activeFilter = ref('未分配')
const currentPage = ref(1)
const pageSize = ref(10)

const filters = ['未分配', '犊虎队', '白虎队', '青龙队', '朱雀队', '玄武队', '战神队']

const teamMap = {
  '犊虎队': 1,
  '白虎队': 2,
  '青龙队': 3,
  '朱雀队': 4,
  '玄武队': 5,
  '战神队': 6,
}

const fetchTeam = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/members')
    if (res.data?.ok) {
      info.value = res.data
      currentPage.value = 1
    }
  } catch (err) {
    console.error('load team failed', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchTeam)

const myTeam = computed(() => {
  if (!info.value?.members) return '未分配'
  const member = info.value.members.find(m => m.is_self)
  if (!member) return '未分配'
  const teamType = member.team_type || 0
  if (teamType === 0) return '未分配'
  const teamName = Object.keys(teamMap).find(name => teamMap[name] === teamType)
  return teamName || '未分配'
})

const filteredMembers = computed(() => {
  const members = info.value?.members || []
  if (activeFilter.value === '未分配') {
    return members.filter(m => !m.team_type || m.team_type === 0)
  }
  const teamType = teamMap[activeFilter.value]
  if (teamType) {
    return members.filter(m => m.team_type === teamType)
  }
  return members
})

const paginatedMembers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredMembers.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredMembers.value.length / pageSize.value))
})

const goToPage = (page) => {
  const pageNum = parseInt(page) || 1
  if (pageNum >= 1 && pageNum <= totalPages.value) {
    currentPage.value = pageNum
  }
}

const goAlliance = () => router.push('/alliance')
const goHome = () => router.push('/')
</script>

<template>
  <div>
    <div>
      <h1>【联盟战队】</h1>
    </div>
    
    <div v-if="loading" style="padding: 20px;">加载中...</div>
    <template v-else-if="info">
      <div style="padding: 10px;">
        所属军队:{{ myTeam }}
      </div>
      
      <div style="padding: 10px;">
        [管理名单]
      </div>
      
      <div style="padding: 10px;">
        <span
          v-for="(filter, index) in filters"
          :key="filter"
        >
          <a
            v-if="activeFilter !== filter"
            href="#"
            @click.prevent="activeFilter = filter; currentPage = 1"
            style="color: #0066cc; text-decoration: underline;"
          >{{ filter }}</a>
          <span v-else style="color: #0066cc; font-weight: bold;">{{ filter }}</span>
          <span v-if="index < filters.length - 1"> | </span>
        </span>
      </div>
      
      <div style="padding: 10px;">
        昵称.等级.战力.加入军队
      </div>
      
      <div style="padding: 10px;">
        <div v-if="paginatedMembers.length > 0">
          <div v-for="member in paginatedMembers" :key="member.user_id" style="padding: 5px 0; color: #cc0000;">
            {{ member.nickname || `玩家${member.user_id}` }} /{{ member.level || 1 }}/{{ member.battle_power || 0 }}
          </div>
        </div>
        <div v-else style="padding: 20px; color: #999;">暂无成员</div>
      </div>
      
      <div v-if="totalPages > 1" style="padding: 10px;">
        <a
          href="#"
          @click.prevent="goToPage(currentPage + 1)"
          style="color: #0066cc; text-decoration: underline;"
        >下页</a>
        <span> </span>
        <a
          href="#"
          @click.prevent="goToPage(totalPages)"
          style="color: #0066cc; text-decoration: underline;"
        >末页</a>
        <span> </span>
        <span>{{ currentPage }}/{{ totalPages }}页 </span>
        <input
          type="number"
          :min="1"
          :max="totalPages"
          :value="currentPage"
          @change="goToPage($event.target.value)"
          style="width: 40px;"
        />
        <span> 跳转</span>
      </div>
      
      <div style="padding: 10px;">
        <a
          href="#"
          @click.prevent="goAlliance"
          style="color: #0066cc; text-decoration: underline;"
        >返回联盟</a>
        <span> </span>
        <a
          href="#"
          @click.prevent="goHome"
          style="color: #0066cc; text-decoration: underline;"
        >返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
div {
  font-family: SimSun, "宋体", serif;
  font-size: 13px;
  line-height: 1.6;
}

h1 {
  margin: 10px 0;
  font-size: 13px;
  font-weight: bold;
}
</style>

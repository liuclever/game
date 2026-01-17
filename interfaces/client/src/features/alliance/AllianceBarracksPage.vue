<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const info = ref(null)
const activeFilter = ref('未分配')
const currentPage = ref(1)
const pageSize = ref(10)

const filters = ['未分配', '飞龙军', '伏虎军']

const fetchBarracks = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/members')
    if (res.data?.ok) {
      info.value = res.data
      currentPage.value = 1
    }
  } catch (err) {
    console.error('load barracks failed', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchBarracks)

const myArmy = computed(() => {
  const member = info.value?.members?.find(m => m.is_self)
  if (!member) return ''
  const armyType = member.army_type || 0
  if (armyType === 1) return '飞龙军'
  if (armyType === 2) return '伏虎军'
  return '未分配'
})

const filteredMembers = computed(() => {
  const members = info.value?.members || []
  if (activeFilter.value === '未分配') {
    return members.filter(m => !m.army_type || m.army_type === 0)
  }
  if (activeFilter.value === '飞龙军') {
    return members.filter(m => m.army_type === 1)
  }
  if (activeFilter.value === '伏虎军') {
    return members.filter(m => m.army_type === 2)
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

// 检查是否是盟主
const isLeader = computed(() => {
  return info.value?.current_role === 1  // ROLE_LEADER = 1
})

// 跳转到踢出确认页面
const kickMember = (member) => {
  router.push({
    path: '/alliance/barracks/manage-confirm',
    query: {
      action: 'kick',
      target_user_id: member.user_id,
      target_nickname: member.nickname || `玩家${member.user_id}`
    }
  })
}

// 跳转到分配确认页面（系统根据等级自动决定分配到哪个军队）
const assignMember = (member) => {
  // 根据等级判断会分配到哪个军队：40级及以下伏虎军，40级以上飞龙军
  const level = member.level || 0
  const armyName = level <= 40 ? '伏虎军' : '飞龙军'
  
  router.push({
    path: '/alliance/barracks/manage-confirm',
    query: {
      action: 'assign',
      target_user_id: member.user_id,
      target_nickname: member.nickname || `玩家${member.user_id}`,
      army_name: armyName
    }
  })
}

// 监听路由变化，如果有error参数，显示错误信息并刷新列表
watch(() => route.query.error, (error) => {
  if (error) {
    console.error(error)
    fetchBarracks()
  }
}, { immediate: true })

// 从确认页面返回时刷新列表
watch(() => route.path, (newPath) => {
  if (newPath === '/alliance/barracks') {
    fetchBarracks()
  }
})
</script>

<template>
  <div>
    <div>
      <h1>【联盟兵营】</h1>
    </div>
    
    <div v-if="loading" style="padding: 20px;">加载中...</div>
    <template v-else-if="info">
      <div style="padding: 10px;">
        所属军队:{{ myArmy }}
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
        昵称/等级/加入军队
      </div>
      
      <div style="padding: 10px;">
        <div v-if="paginatedMembers.length > 0">
          <div v-for="member in paginatedMembers" :key="member.user_id" style="padding: 5px 0; color: #cc0000;">
            <span>{{ member.nickname || `玩家${member.user_id}` }}/{{ member.level || 1 }}</span>
            <span v-if="isLeader && !member.is_self" style="margin-left: 10px;">
              <!-- 未分配列表：显示分配按钮（系统根据等级自动决定） -->
              <template v-if="activeFilter === '未分配'">
                <a href="#" @click.prevent="assignMember(member)" style="color: #0066cc; text-decoration: underline;">[分配]</a>
              </template>
              <!-- 飞龙军或伏虎军列表：显示踢出按钮 -->
              <template v-else>
                <a href="#" @click.prevent="kickMember(member)" style="color: #cc0000; text-decoration: underline;">[踢出]</a>
              </template>
            </span>
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
  font-size: 16px;
  line-height: 1.6;
}

h1 {
  margin: 10px 0;
  font-size: 16px;
  font-weight: bold;
}
</style>

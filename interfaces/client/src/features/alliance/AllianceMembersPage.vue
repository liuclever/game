<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const sortType = ref('role')
const membersData = ref(null)
const roleSelections = ref({})
const listLoading = ref(false)

const ROLE_LABELS = {
  1: '盟主',
  2: '副盟主',
  3: '长老',
  0: '盟众',
}

const roleLabel = (role) => ROLE_LABELS[role] || '盟众'

const fetchMembers = async (sort = sortType.value) => {
  listLoading.value = true
  try {
    const res = await http.get('/alliance/members', { params: { sort } })
    if (res.data.ok) {
      membersData.value = res.data
      roleSelections.value = {}
      res.data.members.forEach(member => {
        roleSelections.value[member.user_id] = member.role
      })
    } else {
      alert(res.data.error || '获取成员信息失败')
    }
  } catch (e) {
    alert(e.response?.data?.error || '获取成员信息失败')
  } finally {
    loading.value = false
    listLoading.value = false
  }
}

const changeSort = (type) => {
  if (sortType.value === type || listLoading.value) return
  sortType.value = type
  fetchMembers(type)
}

const assignRole = async (member) => {
  const selectedRole = Number(roleSelections.value[member.user_id])
  if (Number.isNaN(selectedRole)) {
    alert('请选择有效职位')
    return
  }
  if (selectedRole === member.role) {
    alert('该成员已是此职位')
    return
  }
  try {
    const res = await http.post('/alliance/members/role', {
      target_user_id: member.user_id,
      role: selectedRole,
    })
    if (res.data.ok) {
      alert('职位调整成功')
      fetchMembers()
    } else {
      alert(res.data.error || '调整失败')
    }
  } catch (e) {
    alert(e.response?.data?.error || '调整失败')
  }
}

const kickMember = async (member) => {
  if (!confirm(`确定将 ${member.nickname} 踢出联盟吗？`)) {
    return
  }
  try {
    const res = await http.post('/alliance/members/kick', {
      target_user_id: member.user_id,
    })
    if (res.data.ok) {
      alert('已踢出该成员')
      fetchMembers()
    } else {
      alert(res.data.error || '操作失败')
    }
  } catch (e) {
    alert(e.response?.data?.error || '操作失败')
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchMembers()
})
</script>

<template>
  <div class="alliance-members-page">
    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="membersData">
      <div class="section title">【联盟人员】</div>
      <div class="section leaders">
        <div>盟主: {{ membersData.leader_name || '暂无' }}</div>
        <div>副盟主: {{ membersData.vice_leaders?.join('、') || '暂无' }}</div>
        <div>长老: {{ membersData.elders?.join('、') || '暂无' }}</div>
      </div>

      <div class="section sort-options">
        排序：
        <a
          v-for="type in [
            { key: 'role', label: '职位排列' },
            { key: 'contribution', label: '贡献排列' },
            { key: 'level', label: '等级排列' },
          ]"
          :key="type.key"
          class="link"
          :class="{ active: sortType === type.key }"
          @click="changeSort(type.key)"
        >
          {{ type.label }}
        </a>
      </div>

      <div class="section table">
        <div class="table-header">
          <span class="col index">#</span>
          <span class="col name">成员</span>
          <span class="col level">等级</span>
          <span class="col role">职位</span>
          <span class="col contrib">贡献</span>
          <span class="col actions">操作</span>
        </div>
        <div
          v-for="member in membersData.members"
          :key="member.user_id"
          class="table-row"
        >
          <span class="col index">{{ member.index }}.</span>
          <span class="col name">
            {{ member.nickname }}
            <template v-if="member.can_kick">
              <a class="link small" @click="kickMember(member)">[踢出]</a>
            </template>
          </span>
          <span class="col level">{{ member.level }}</span>
          <span class="col role">{{ member.role_label }}</span>
          <span class="col contrib">{{ member.contribution }}</span>
          <span class="col actions">
            <template v-if="member.can_assign_role && membersData.can_manage_roles">
              <select
                v-model="roleSelections[member.user_id]"
                class="role-select"
              >
                <option
                  v-for="option in membersData.role_options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
              <button class="btn small" @click="assignRole(member)">调整</button>
            </template>
            <span v-else class="muted">-</span>
          </span>
        </div>
      </div>

      <div class="section nav-links">
        <a class="link" @click="goBackAlliance">返回联盟</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    <div v-else class="section">未加入联盟</div>
  </div>
</template>

<style scoped>
.alliance-members-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 16px;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
  font-size: 18px;
}

.leaders div {
  margin: 4px 0;
}

.sort-options .link {
  margin-right: 8px;
}

.sort-options .active {
  font-weight: bold;
  text-decoration: underline;
}

.table {
  border: 1px solid #d8c9a3;
  border-radius: 4px;
}

.table-header,
.table-row {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  border-bottom: 1px solid #f0e4c5;
}

.table-header {
  background: #f5e4bd;
  font-weight: bold;
}

.table-row:last-child {
  border-bottom: none;
}

.col {
  flex-shrink: 0;
}

.col.index {
  width: 36px;
}

.col.name {
  flex: 1;
}

.col.level,
.col.role,
.col.contrib {
  width: 70px;
  text-align: center;
}

.col.actions {
  width: 150px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.role-select {
  flex: 1;
  border: 1px solid #c6b38d;
  padding: 2px 4px;
  font-family: inherit;
}

.btn {
  background: #f5deb3;
  border: 1px solid #c49c48;
  padding: 4px 8px;
  cursor: pointer;
  font-family: inherit;
}

.btn.small {
  padding: 2px 6px;
  font-size: 18px;
}

.muted {
  color: #999;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.small {
  font-size: 18px;
  margin-left: 4px;
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const membersData = ref(null)
const selectedMemberId = ref(null)
const showConfirm = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const fetchMembers = async () => {
    loading.value = true
    try {
        const res = await http.get('/alliance/members', { params: { sort: 'role' } })
        if (res.data.ok) {
            membersData.value = res.data
        } else {
            errorMsg.value = res.data.error || '获取成员列表失败'
        }
    } catch (e) {
        errorMsg.value = e.response?.data?.error || '获取成员列表失败'
    } finally {
        loading.value = false
    }
}

const transferableMembers = computed(() => {
    if (!membersData.value?.members) return []
    return membersData.value.members.filter(m => m.role !== 1)
})

const selectedMember = computed(() => {
    if (!selectedMemberId.value) return null
    return transferableMembers.value.find(m => m.user_id === selectedMemberId.value)
})

const selectMember = (memberId) => {
    selectedMemberId.value = memberId
    errorMsg.value = ''
    showConfirm.value = false
}

const showConfirmStep = () => {
    if (!selectedMemberId.value) {
        errorMsg.value = '请选择要转让的成员'
        return
    }
    
    const selectedMember = transferableMembers.value.find(m => m.user_id === selectedMemberId.value)
    if (!selectedMember) {
        errorMsg.value = '请选择有效的成员'
        return
    }
    
    showConfirm.value = true
    errorMsg.value = ''
}

const cancelConfirm = () => {
    showConfirm.value = false
}

const confirmTransfer = async () => {
    try {
        const res = await http.post('/alliance/transfer', {
            target_user_id: selectedMemberId.value
        })
        if (res.data.ok) {
            successMsg.value = res.data.message || '转让成功'
            setTimeout(() => {
                router.push('/alliance')
            }, 2000)
        } else {
            errorMsg.value = res.data.error || '转让失败'
            showConfirm.value = false
        }
    } catch (e) {
        errorMsg.value = e.response?.data?.error || '转让失败'
        showConfirm.value = false
    }
}

const goBack = () => {
    router.push('/alliance/council')
}

onMounted(() => {
    fetchMembers()
})
</script>

<template>
    <div class="alliance-transfer-page">
        <div class="section title">【转让联盟】</div>
        
        <div v-if="loading" class="section">加载中...</div>
        
        <template v-else>
            <div v-if="errorMsg" class="section error">{{ errorMsg }}</div>
            <div v-if="successMsg" class="section success">{{ successMsg }}</div>
            
            <div class="section">
                <div>请选择要转让的成员：</div>
                <div class="member-list">
                    <div 
                        v-for="member in transferableMembers" 
                        :key="member.user_id"
                        class="member-item"
                        :class="{ selected: selectedMemberId === member.user_id }"
                        @click="selectMember(member.user_id)"
                    >
                        {{ member.nickname || `玩家${member.user_id}` }} - 等级: {{ member.level || 0 }} | 职位: {{ member.role_label || '盟众' }}
                    </div>
                    <div v-if="transferableMembers.length === 0" class="section">暂无可转让的成员</div>
                </div>
            </div>
            
            <div class="section hint">
                被转让者需要：等级30级及以上，拥有1个盟主证明
            </div>
            
            <div v-if="showConfirm && selectedMember" class="section confirm-box">
                <div>确定要将联盟转让给【{{ selectedMember.nickname || `玩家${selectedMember.user_id}` }}】吗？</div>
                <div class="section">
                    <a class="link" @click="confirmTransfer">确定</a> | 
                    <a class="link" @click="cancelConfirm">取消</a>
                </div>
            </div>
            
            <div v-else class="section">
                <a class="link" @click="showConfirmStep">确认转让</a> | 
                <a class="link" @click="goBack">返回议事厅</a>
            </div>
        </template>
    </div>
</template>

<style scoped>
.alliance-transfer-page {
    background: #ffffff;
    min-height: 100vh;
    padding: 8px 12px;
    font-size: 16px;
    line-height: 1.6;
    font-family: SimSun, "宋体", serif;
}

.section {
    margin: 8px 0;
}

.title {
    font-weight: bold;
}

.error {
    color: #dc3545;
}

.success {
    color: #155724;
}

.member-list {
    margin: 10px 0;
}

.member-item {
    padding: 8px;
    margin: 4px 0;
    border: 1px solid #ddd;
    cursor: pointer;
}

.member-item:hover {
    background-color: #f5f5f5;
}

.member-item.selected {
    background-color: #e3f2fd;
}

.hint {
    color: #666;
    font-size: 14px;
}

.link {
    color: #0066CC;
    cursor: pointer;
    text-decoration: none;
}

.link:hover {
    text-decoration: underline;
}

.confirm-box {
    border: 1px solid #ddd;
    padding: 10px;
    margin: 10px 0;
}
</style>

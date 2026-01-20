<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const allianceData = ref(null)
const showConfirm = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const fetchAllianceInfo = async () => {
    loading.value = true
    try {
        const res = await http.get('/alliance/my')
        if (res.data.ok) {
            allianceData.value = res.data
        } else {
            errorMsg.value = res.data.error || '获取联盟信息失败'
        }
    } catch (e) {
        errorMsg.value = e.response?.data?.error || '获取联盟信息失败'
    } finally {
        loading.value = false
    }
}

const showConfirmStep = () => {
    showConfirm.value = true
    errorMsg.value = ''
}

const cancelConfirm = () => {
    showConfirm.value = false
}

const confirmDissolve = async () => {
    try {
        const res = await http.post('/alliance/dissolve')
        if (res.data.ok) {
            successMsg.value = res.data.message || '联盟已解散'
            setTimeout(() => {
                router.push('/alliance/hall')
            }, 2000)
        } else {
            errorMsg.value = res.data.error || '解散失败'
            showConfirm.value = false
        }
    } catch (e) {
        errorMsg.value = e.response?.data?.error || '解散失败'
        showConfirm.value = false
    }
}

const goBack = () => {
    router.push('/alliance/council')
}

onMounted(() => {
    fetchAllianceInfo()
})
</script>

<template>
    <div class="alliance-dissolve-page">
        <div class="section title">【解散联盟】</div>
        
        <div v-if="loading" class="section">加载中...</div>
        
        <template v-else>
            <div v-if="errorMsg" class="section error">{{ errorMsg }}</div>
            <div v-if="successMsg" class="section success">{{ successMsg }}</div>
            
            <div v-if="allianceData" class="section">
                <div>联盟名称：{{ allianceData.alliance.name }}</div>
                <div>成员数量：{{ allianceData.member_count }}</div>
            </div>
            
            <div class="section warning">
                警告：解散联盟后，所有成员将退出联盟，此操作不可恢复！
            </div>
            
            <div v-if="showConfirm" class="section confirm-box">
                <div>再次确认：确定要解散联盟吗？</div>
                <div class="section">
                    <a class="link" @click="confirmDissolve">确定解散</a> | 
                    <a class="link" @click="cancelConfirm">取消</a>
                </div>
            </div>
            
            <div v-else class="section">
                <a class="link" @click="showConfirmStep">确定解散</a> | 
                <a class="link" @click="goBack">返回议事厅</a>
            </div>
        </template>
    </div>
</template>

<style scoped>
.alliance-dissolve-page {
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

.warning {
    color: #dc3545;
    font-weight: bold;
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

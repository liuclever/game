<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const allianceData = ref(null)
const errorMsg = ref('')

const isLeader = computed(() => {
    return allianceData.value?.member_info?.role === 1
})

const fetchAllianceInfo = async () => {
    loading.value = true
    try {
        const res = await http.get('/alliance/my')
        if (res.data.ok) {
            allianceData.value = res.data
        }
    } catch (e) {
        console.error('获取联盟信息失败', e)
    } finally {
        loading.value = false
    }
}

const goToBuildingUpgrade = () => {
  router.push('/alliance/buildings') // 或者实际的升级页面路由
}
const goToNotice = () => {
    router.push('/alliance/notice')
}

const goBack = () => {
    router.push('/alliance')
}

const goToHome = () => {
    router.push('/')
}
const goToMembers =() => {
    router.push('/alliance/members')
}
const goToTalent = () => {
    router.push('/alliance/talent')
}

const goToQuitConfirm = () => {
    router.push('/alliance/quit-confirm')
}

const goToTransfer = () => {
    router.push('/alliance/transfer')
}

const goToDisbandConfirm = () => {
    router.push('/alliance/disband-confirm')
}

onMounted(() => {
    // 检查是否有错误信息
    if (route.query.error) {
        errorMsg.value = route.query.error
        // 清除URL中的error参数
        router.replace({ path: route.path, query: {} })
    }
    fetchAllianceInfo()
})
</script>

<template>
    <div class="alliance-council-page">
        <div v-if="loading" class="section">加载中...</div>
        <template v-else-if="allianceData">
            <div v-if="errorMsg" class="section error-message">{{ errorMsg }}</div>
            <div class="section title">【议事厅】</div>
            <div class="section description">
                盟主管理联盟的场所，议事厅的建筑等级决定联盟等级。
            </div>
            <div class="section stats">
                <div>建筑等级：{{ allianceData.alliance.level }}级</div>
                <div>资金：{{ allianceData.alliance.funds }}</div>
                <div>焚火晶：{{ allianceData.alliance.crystals }}</div>
                <div>繁荣值：{{ allianceData.alliance.prosperity }}</div>
            </div>

            <div class="section links">
                <a class="link" @click="goToNotice">公告栏</a>. <a class="link" @click="goToMembers">成员管理</a><br>
                <a class="link" @click="goToBuildingUpgrade">建筑升级</a><br>
                <a v-if="isLeader" class="link" @click="goToTransfer">转让联盟</a><span v-if="isLeader">. </span><a v-if="isLeader" class="link" @click="goToDisbandConfirm">解散联盟</a><br>
                <a v-if="!isLeader" class="link" @click="goToQuitConfirm">退出联盟</a>
            </div>

            <div class="section nav-links">
                <a class="link" @click="goBack">返回联盟</a><br>
                <a class="link" @click="goToHome">返回游戏首页</a>
            </div>

        </template>
    </div>
</template>

<style scoped>
.alliance-council-page {
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

.description {
    color: #333;
}

.link {
    color: #0066CC;
    cursor: pointer;
    text-decoration: none;
}

.link:hover {
    text-decoration: underline;
}

.error-message {
    color: #CC0000;
    font-weight: bold;
    margin-bottom: 8px;
}

.footer-info {
    margin-top: 20px;
    color: #999;
    font-size: 17px;
    border-top: 1px solid #EEE;
    padding-top: 8px;
}
</style>

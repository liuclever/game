<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()

const { message, messageType, showMessage } = useMessage()

const upgradeInfo = ref(null)
const loading = ref(true)
const upgrading = ref(false)

const loadUpgradeInfo = async () => {
  try {
    const res = await http.get('/inventory/upgrade_info')
    if (res.data.ok) {
      upgradeInfo.value = res.data
    }
  } catch (e) {
    console.error('加载升级信息失败', e)
  } finally {
    loading.value = false
  }
}

const doUpgrade = async () => {
  if (upgrading.value) return
  if (!upgradeInfo.value?.can_upgrade) return
  
  upgrading.value = true
  try {
    const res = await http.post('/inventory/upgrade')
    if (res.data.ok) {
      showMessage(res.data.message, 'success')
      loadUpgradeInfo()
    } else {
      showMessage(res.data.error, 'error')
    }
  } catch (e) {
    console.error('升级失败', e)
    showMessage('升级失败', 'error')
  } finally {
    upgrading.value = false
  }
}

const goBack = () => router.push('/inventory')
const goHome = () => router.push('/')

onMounted(() => {
  loadUpgradeInfo()
})
</script>

<template>
  <div class="upgrade-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading">加载中...</div>
    <template v-else-if="upgradeInfo">
      <!-- 已达最高等级 -->
      <template v-if="upgradeInfo.reason">
        <div class="info">{{ upgradeInfo.current_bag_name }}</div>
        <div class="info">容量：{{ upgradeInfo.current_capacity }}</div>
        <div class="info gray">{{ upgradeInfo.reason }}</div>
      </template>
      <!-- 可升级 -->
      <template v-else>
        <div class="info">{{ upgradeInfo.current_bag_name }}→{{ upgradeInfo.next_bag_name }}</div>
        <div class="info">{{ upgradeInfo.current_capacity }}→{{ upgradeInfo.next_capacity }}</div>
        <div v-for="mat in upgradeInfo.materials" :key="mat.item_id" class="info">
          {{ mat.name }}:{{ mat.owned }}/{{ mat.required }}
        </div>
        <div class="info">人物等级：{{ upgradeInfo.player_level }}</div>
        
        <!-- 条件不满足 -->
        <div v-if="!upgradeInfo.can_upgrade" class="info">
          您的条件不满足，无法升级
        </div>
        <!-- 条件满足，显示升级链接 -->
        <div v-else class="info">
          <a class="link" @click="doUpgrade">{{ upgrading ? '升级中...' : '升级' }}</a>
        </div>
      </template>
    </template>
    
    <!-- 主页菜单（严格复刻主页内容与UI） -->
    <MainMenuLinks />

    <div class="nav-links">
      <div><a class="link" @click="goBack">返回背包</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>

  </div>
</template>

<style scoped>
.upgrade-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 15px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.info {
  margin: 4px 0;
}

.gray {
  color: #666;
}

.nav-links {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.footer {
  margin-top: 20px;
}

.small {
  font-size: 11px;
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

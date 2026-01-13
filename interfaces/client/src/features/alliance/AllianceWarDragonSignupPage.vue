<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(false)
const targets = ref([])

const loadTargets = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/war/dragon/targets')
    if (res.data.ok) {
      targets.value = res.data.targets || []
    }
  } catch (e) {
    console.error('加载失败', e)
  } finally {
    loading.value = false
  }
}

const handleAttack = async (target) => {
  // 已移除确认提示
  
  try {
    const res = await http.post('/alliance/war/dragon/signup', { target_id: target.id })
    if (res.data.ok) {
      showMessage(res.data.message || '报名成功', 'success')
      await loadTargets()
    } else {
      showMessage(res.data.error || '报名失败', 'error')
    }
  } catch (e) {
    console.error('报名失败', e)
    showMessage(e?.response?.data?.error || '报名失败', 'error')
  }
}

const goBack = () => {
  router.push('/alliance/war')
}

onMounted(() => {
  loadTargets()
})
</script>

<template>
  <div class="page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div class="section title">【盟战·天龙报名】</div>
    
    <div v-if="loading" class="section">加载中...</div>
    
    <template v-else>
      <div v-if="targets.length === 0" class="section">
        暂无可攻打的目标
      </div>
      
      <div v-for="target in targets" :key="target.id" class="section">
        <div>{{ target.name }} (等级: {{ target.level }})</div>
        <div>
          <a class="link" @click="handleAttack(target)">报名攻打</a>
        </div>
      </div>
    </template>
    
    <div class="section">
      <a class="link" @click="goBack">返回盟战</a>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 10px;
  background: #f5f5dc;
  min-height: 100vh;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
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

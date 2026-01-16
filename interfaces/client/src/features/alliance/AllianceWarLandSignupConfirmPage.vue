<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const landName = route.query.land_name || ''
const landId = route.query.land_id || ''
const submitting = ref(false)

const confirmSignup = async () => {
  if (submitting.value) return
  submitting.value = true
  try {
    const res = await http.post('/alliance/war/target-signup', {
      target_id: parseInt(landId),
      army: 'dragon',
    })
    if (res.data?.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/war/land-signup-result',
        query: {
          success: 'true',
          message: '报名成功，等待盟主确认。',
          land_name: landName
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/war/land-signup-result',
        query: {
          success: 'false',
          message: res.data?.error || '报名失败',
          land_name: landName
        }
      })
    }
  } catch (err) {
    console.error('攻打报名失败', err)
    // 跳转到失败页面
    router.push({
      path: '/alliance/war/land-signup-result',
      query: {
        success: 'false',
        message: err.response?.data?.error || '报名失败',
        land_name: landName
      }
    })
  } finally {
    submitting.value = false
  }
}

const cancel = () => {
  router.back()
}

const goWar = () => {
  router.push('/alliance/war')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="confirm-page">
    <div class="message">确认报名攻打 {{ landName }} 吗？</div>

    <div class="actions">
      <button class="btn confirm" :disabled="submitting" @click="confirmSignup">
        {{ submitting ? '提交中...' : '确定' }}
      </button>
      <button class="btn cancel" :disabled="submitting" @click="cancel">取消</button>
    </div>

    <div class="nav-links">
      <div><a class="link" @click="goWar">返回盟战</a></div>
      <div><a class="link" @click="goHome">返回游戏首页</a></div>
    </div>
  </div>
</template>

<style scoped>
.confirm-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.message {
  color: #000;
  margin-bottom: 20px;
  font-size: 16px;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.btn {
  padding: 8px 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-family: inherit;
  font-size: 17px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.confirm {
  background: #0066CC;
  color: #fff;
  border-color: #0066CC;
}

.btn.confirm:hover:not(:disabled) {
  background: #0052a3;
}

.btn.cancel {
  background: #fff;
  color: #333;
  border-color: #ccc;
}

.btn.cancel:hover:not(:disabled) {
  background: #ffffff;
}

.nav-links {
  margin-top: 16px;
}

.nav-links div {
  margin: 4px 0;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>

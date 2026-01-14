<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(true)
const noticeData = ref(null)
const noticeInput = ref('')
const submitting = ref(false)

const fetchNotice = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/notice')
    if (res.data.ok) {
      noticeData.value = res.data
      noticeInput.value = res.data.notice || ''
    } else {
      alert(res.data.error || '获取公告失败')
      noticeData.value = null
    }
  } catch (e) {
    alert(e.response?.data?.error || '获取公告失败')
    noticeData.value = null
  } finally {
    loading.value = false
  }
}

const confirmUpdate = async () => {
  if (!noticeData.value?.can_edit || submitting.value) return
  const content = (noticeInput.value || '').trim()
  if (!content) {
    alert('公告不能为空')
    return
  }
  if (content.length > 35) {
    alert('公告限制为35个字以内')
    return
  }

  submitting.value = true
  try {
    const res = await http.post('/alliance/notice', { notice: content })
    if (res.data.ok) {
      // 跳转到成功页面
      router.push({
        path: '/alliance/notice/update-result',
        query: {
          success: 'true',
          message: res.data.message || '公告更新成功'
        }
      })
    } else {
      // 跳转到失败页面
      router.push({
        path: '/alliance/notice/update-result',
        query: {
          success: 'false',
          message: res.data.error || '修改失败'
        }
      })
    }
  } catch (e) {
    // 跳转到失败页面
    router.push({
      path: '/alliance/notice/update-result',
      query: {
        success: 'false',
        message: e.response?.data?.error || '修改失败，请稍后再试'
      }
    })
  } finally {
    submitting.value = false
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  fetchNotice()
})
</script>

<template>
  <div class="alliance-notice-page">
    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="noticeData">
      <div class="section title">【联盟公告】</div>
      <div class="section current-notice">
        <span class="label">公告:</span>
        <span class="content">{{ noticeData.notice || '点击设置公告' }}</span>
      </div>

      <div v-if="noticeData.can_edit" class="section edit-box">
        <div class="label">修改公告:</div>
        <div class="form-row">
          <input
            v-model="noticeInput"
            type="text"
            class="input"
            maxlength="35"
            placeholder="请输入公告内容"
          />
          <button class="btn" :disabled="submitting" @click="confirmUpdate">确认修改</button>
        </div>
      </div>
      <div v-else class="section tip">仅盟主可以修改公告</div>

      <div class="section tip">提示:公告限制为35个字以内</div>

      <div class="section links">
        <a class="link" @click="goBackAlliance">返回联盟</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
    <div v-else class="section">未加入联盟</div>
  </div>
</template>

<style scoped>
.alliance-notice-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
  font-size: 16px;
}

.current-notice .label {
  font-weight: bold;
  margin-right: 6px;
}

.current-notice .content {
  color: #333;
}

.edit-box .form-row {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.input {
  flex: 1;
  border: 1px solid #ccc;
  padding: 6px 8px;
  font-size: 17px;
  font-family: inherit;
}

.btn {
  background: #f5deb3;
  border: 1px solid #c49c48;
  padding: 6px 12px;
  cursor: pointer;
  font-family: inherit;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tip {
  color: #666;
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
</style>

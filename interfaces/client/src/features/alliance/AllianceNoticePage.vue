<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

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
      showMessage(res.data.error || '获取公告失败', 'error')
      noticeData.value = null
    }
  } catch (e) {
    showMessage(e.response?.data?.error || '获取公告失败', 'error')
    noticeData.value = null
  } finally {
    loading.value = false
  }
}

const confirmUpdate = async () => {
  if (!noticeData.value?.can_edit || submitting.value) return
  const content = (noticeInput.value || '').trim()
  if (!content) {
    showMessage('公告不能为空', 'info')
    return
  }
  if (content.length > 35) {
    showMessage('公告限制为35个字以内', 'info')
    return
  }

  submitting.value = true
  try {
    const res = await http.post('/alliance/notice', { notice: content })
    if (res.data.ok) {
      noticeData.value.notice = content
      showMessage('公告更新成功', 'success')
      router.push('/alliance')
    } else {
      showMessage(res.data.error || '修改失败', 'error')
    }
  } catch (e) {
    showMessage(e.response?.data?.error || '修改失败', 'error')
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
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

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
  background: #fff8dc;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 14px;
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
  font-size: 14px;
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
  font-size: 13px;
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

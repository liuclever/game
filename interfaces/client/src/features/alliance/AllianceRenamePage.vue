<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const newName = ref('')
const submitting = ref(false)
const message = ref('')

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const submitRename = async () => {
  const trimmed = newName.value.trim()
  if (!trimmed) {
    message.value = '请输入联盟新名字'
    return
  }
  submitting.value = true
  message.value = ''
  try {
    const res = await http.post('/alliance/rename', { name: trimmed })
    if (res.data?.ok) {
      message.value = res.data.message || '修改成功'
      newName.value = ''
      setTimeout(() => {
        goAlliance()
      }, 800)
    } else {
      message.value = res.data?.error || '修改失败'
    }
  } catch (err) {
    message.value = err.response?.data?.error || '修改失败'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="rename-page">
    <div class="section title">【修改联盟名字】 每修改1次需要花费1000元宝</div>
    <div class="section">请输入联盟新名字，2至13个字</div>
    <div class="section form-row">
      <input
        v-model="newName"
        type="text"
        class="input"
        maxlength="13"
        placeholder="请输入新名字"
        :disabled="submitting"
      />
      <button class="btn" :disabled="submitting" @click="submitRename">确定修改</button>
    </div>
    <div class="section message" v-if="message">{{ message }}</div>
    <div class="section links">
      <a class="link" @click.prevent="goAlliance">返回联盟</a><br />
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.rename-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-family: SimSun, '宋体', serif;
  color: #333;
}

.section {
  margin-bottom: 12px;
  line-height: 1.8;
}

.title {
  font-weight: bold;
  color: #8b4513;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input {
  flex: 1;
  padding: 4px 6px;
  border: 1px solid #ccc;
  font-family: inherit;
}

.btn {
  padding: 4px 10px;
  border: 1px solid #999;
  background: #fff;
  cursor: pointer;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.message {
  color: #c00;
}
</style>

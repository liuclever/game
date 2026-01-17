<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const loading = ref(false)
const roomTitle = ref('焚天炉')
const errorMsg = ref('')

const createRoom = async () => {
  if (loading.value) return
  
  if (!roomTitle.value.trim()) {
    errorMsg.value = '请输入房间名称'
    return
  }
  
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.post('/alliance/training-ground/rooms', { 
      title: roomTitle.value.trim(),
      duration_hours: 2  // 固定2小时
    })
    
    if (res.data?.ok) {
      // 创建成功，返回修行广场
      router.push('/alliance/training-ground')
    } else {
      errorMsg.value = res.data?.error || '创建修行房间失败'
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 不再需要加载时长选项，固定2小时
})

const goBack = () => {
  router.push('/alliance/training-ground')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="create-room-page">
    <div class="title">【创建修行房间】</div>
    
    <div class="section">
      <div class="form-row">
        <label>房间名称：</label>
        <input 
          type="text" 
          v-model="roomTitle" 
          class="form-input"
          placeholder="请输入修行房间名称（可选）"
          maxlength="20"
          @keyup.enter="createRoom"
        />
      </div>
      <div class="hint">提示：房间名称可选，默认为"焚天炉"</div>
    </div>
    
    <div class="section">
      <div class="form-row">
        <label>修行时长：</label>
        <span class="form-input" style="display: inline-block; border: none; padding: 0;">2小时（固定）</span>
      </div>
      <div class="hint">提示：修行需要消耗1个火能原石，请确保有足够的火能原石</div>
    </div>
    
    <div v-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <div class="section">
      <button 
        class="btn confirm" 
        @click="createRoom"
        :disabled="loading"
      >
        {{ loading ? '创建中...' : '确认创建' }}
      </button>
      <button 
        class="btn cancel" 
        @click="goBack"
        :disabled="loading"
      >
        取消
      </button>
    </div>
    
    <div class="section spacer">
      <a class="link" @click="goBack">返回修行广场</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.create-room-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 16px;
}

.section {
  margin: 12px 0;
}

.spacer {
  margin-top: 20px;
}

.form-row {
  margin: 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-row label {
  min-width: 80px;
}

.form-input {
  flex: 1;
  max-width: 300px;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 17px;
  font-family: SimSun, "宋体", serif;
}

.form-input:focus {
  outline: none;
  border-color: #0066cc;
}

.hint {
  font-size: 18px;
  color: #666;
  margin-top: 4px;
  padding-left: 88px;
}

.error {
  color: #CC0000;
  font-weight: bold;
}

.btn {
  padding: 6px 16px;
  margin-right: 8px;
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 17px;
  font-family: SimSun, "宋体", serif;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.confirm {
  background: #0066cc;
  color: #fff;
  border-color: #0066cc;
}

.btn.confirm:hover:not(:disabled) {
  background: #0052a3;
}

.btn.cancel {
  background: #fff;
  color: #333;
}

.btn.cancel:hover:not(:disabled) {
  background: #ffffff;
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

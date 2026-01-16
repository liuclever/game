<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 表单模式：login / register
const mode = ref('login')

// 表单数据
const username = ref('')
const password = ref('')
const nickname = ref('')

// 状态
const loading = ref(false)
const error = ref('')

// 检查登录状态
const checkAuth = async () => {
  try {
    const res = await http.get('/auth/status')
    if (res.data.logged_in) {
      router.push('/')
    }
  } catch (e) {
    console.error('检查登录状态失败', e)
  }
}

onMounted(() => {
  checkAuth()
})

// 登录
const doLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const loginData = {
      username: username.value.trim(),  // 去除首尾空格
      password: password.value.trim(),  // 去除首尾空格
    }
    console.log('发送登录请求:', { username: loginData.username, password: '***' })
    
    const res = await http.post('/auth/login', loginData)
    console.log('登录响应:', res.data)
    
    if (res.data.ok) {
      // 保存到localStorage
      localStorage.setItem('user_id', res.data.user_id)
      localStorage.setItem('nickname', res.data.nickname)
      localStorage.setItem('level', res.data.level)
      router.push('/')
    } else {
      error.value = res.data.error || '登录失败，请重试'
      console.error('登录失败:', res.data.error)
    }
  } catch (e) {
    console.error('登录异常:', e)
    console.error('错误详情:', e.response?.data || e.message)
    error.value = e.response?.data?.error || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

// 注册
const doRegister = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入账号和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const res = await http.post('/auth/register', {
      username: username.value,
      password: password.value,
      nickname: nickname.value || username.value,
    })
    
    if (res.data.ok) {
      // 保存到localStorage
      localStorage.setItem('user_id', res.data.user_id)
      localStorage.setItem('nickname', res.data.nickname)
      localStorage.setItem('level', res.data.level)
      router.push('/')
    } else {
      error.value = res.data.error
    }
  } catch (e) {
    console.error('注册失败', e)
    error.value = '注册失败，请重试'
  } finally {
    loading.value = false
  }
}

// 切换模式
const switchMode = (newMode) => {
  mode.value = newMode
  error.value = ''
}

// 提交
const submit = () => {
  if (mode.value === 'login') {
    doLogin()
  } else {
    doRegister()
  }
}
</script>

<template>
  <div class="login-page">
    <div class="section title">
      【{{ mode === 'login' ? '登录' : '注册' }}】
    </div>

    <!-- 切换模式 -->
    <div class="section">
      <a 
        class="link" 
        :class="{ active: mode === 'login' }"
        @click="switchMode('login')"
      >登录</a> | 
      <a 
        class="link"
        :class="{ active: mode === 'register' }"
        @click="switchMode('register')"
      >注册</a>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="section red">{{ error }}</div>

    <!-- 表单 -->
    <div class="form-section">
      <div class="form-row">
        <label>账号：</label>
        <input 
          type="text" 
          v-model="username" 
          class="form-input"
          placeholder="请输入账号"
          @keyup.enter="submit"
        />
      </div>
      <div class="form-row">
        <label>密码：</label>
        <input 
          type="password" 
          v-model="password" 
          class="form-input"
          placeholder="请输入密码"
          @keyup.enter="submit"
        />
      </div>
      <div v-if="mode === 'register'" class="form-row">
        <label>昵称：</label>
        <input 
          type="text" 
          v-model="nickname" 
          class="form-input"
          placeholder="可选，默认与账号相同"
          @keyup.enter="submit"
        />
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="section">
      <button 
        class="submit-btn" 
        @click="submit"
        :disabled="loading"
      >
        {{ loading ? '请稍候...' : (mode === 'login' ? '登录' : '注册') }}
      </button>
    </div>



  </div>
</template>

<style scoped>
.login-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.title {
  margin-bottom: 12px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.active {
  color: #CC3300;
  font-weight: bold;
}

.red {
  color: #CC0000;
}

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.form-section {
  margin: 16px 0;
}

.form-row {
  margin: 8px 0;
}

.form-row label {
  display: inline-block;
  width: 50px;
}

.form-input {
  width: 180px;
  padding: 6px 10px;
  font-size: 16px;
  border: 1px solid #CCCCCC;
}

.submit-btn {
  padding: 8px 28px;
  font-size: 16px;
  background: #0066CC;
  color: white;
  border: none;
  cursor: pointer;
}

.submit-btn:hover {
  background: #0055AA;
}

.submit-btn:disabled {
  background: #999999;
  cursor: not-allowed;
}

.footer {
  margin-top: 40px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

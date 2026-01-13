<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

// 加载状态
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const errorMsg = ref('')
const actionMsg = ref('')

// 幻兽信息
const beastId = ref(0)
const beastName = ref('')
const beastRealm = ref('')

// 技能书列表
const skillBooks = ref([])

// 加载幻兽信息
const loadBeastInfo = async () => {
  beastId.value = route.params.id
  if (!beastId.value) {
    errorMsg.value = '无效的幻兽ID'
    return
  }
  
  try {
    const res = await http.get(`/beast/${beastId.value}`)
    if (res.data.ok) {
      beastName.value = res.data.beast.name
      beastRealm.value = res.data.beast.realm
    }
  } catch (err) {
    console.error('加载幻兽信息失败:', err)
  }
}

// 加载技能书列表
const loadSkillBooks = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    const res = await http.get('/inventory/skill-books')
    if (res.data.ok) {
      skillBooks.value = res.data.skillBooks
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载技能书失败:', err)
  } finally {
    loading.value = false
  }
}

// 使用技能书
const useSkillBook = async (book) => {
  // 已移除确认提示
  
  actionMsg.value = ''
  
  try {
    const res = await http.post('/beast/use-skill-book', {
      beastId: parseInt(beastId.value),
      itemId: book.item_id,
    })
    
    if (res.data.ok) {
      // 成功
      let msg = res.data.message
      if (res.data.action === 'add') {
        msg = `成功学会【${res.data.newSkill}】！`
      } else if (res.data.action === 'replace') {
        msg = `【${res.data.replacedSkill}】被替换为【${res.data.newSkill}】！`
      }
      actionMsg.value = msg
      showMessage(msg, 'info')
      
      // 重新加载技能书列表
      await loadSkillBooks()
    } else {
      actionMsg.value = res.data.error || '使用失败'
      showMessage(res.data.error || '使用失败', 'error')
    }
  } catch (err) {
    actionMsg.value = '网络错误'
    showMessage('网络错误，请稍后重试', 'error')
    console.error('使用技能书失败:', err)
  }
}

// 返回幻兽详情
const goBack = () => {
  router.push(`/beast/${beastId.value}`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(async () => {
  await loadBeastInfo()
  await loadSkillBooks()
})

// 页面标题
const pageTitle = computed(() => {
  if (beastName.value && beastRealm.value) {
    return `【${beastName.value}-${beastRealm.value}-使用技能书】`
  }
  return '【使用技能书】'
})
</script>

<template>
  <div class="skill-book-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- 标题 -->
    <div class="section title">{{ pageTitle }}</div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section error">{{ errorMsg }}</div>
    
    <!-- 技能书列表 -->
    <template v-else>
      <div v-if="skillBooks.length === 0" class="section">
        背包中没有技能书
      </div>
      
      <div v-for="book in skillBooks" :key="book.id" class="section book-item">
        技能书:<a class="link skill-name">{{ book.name }}</a>×{{ book.quantity }}
        <a class="link use-btn" @click="useSkillBook(book)">使用</a>
      </div>
    </template>
    
    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回幻兽</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
    <!-- 版权 -->
  </div>
</template>

<style scoped>
.skill-book-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.spacer {
  margin-top: 16px;
}

.error {
  color: red;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.book-item {
  display: flex;
  align-items: center;
}

.skill-name {
  margin-right: 4px;
}

.use-btn {
  margin-left: 8px;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
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

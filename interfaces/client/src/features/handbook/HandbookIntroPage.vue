<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchHandbookDoc } from '@/services/handbookService'

const router = useRouter()

const loading = ref(false)
const errorMsg = ref('')
const title = ref('【图鉴说明】')
const docText = ref('')

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await fetchHandbookDoc()
    if (res.data?.ok) {
      title.value = res.data?.title || title.value
      const lines = res.data?.lines || []
      docText.value = Array.isArray(lines) ? lines.join('\n') : String(lines || '')
    } else {
      errorMsg.value = res.data?.error || '加载失败'
    }
  } catch (e) {
    console.error('加载图鉴说明失败', e)
    errorMsg.value = '加载失败'
  } finally {
    loading.value = false
  }
}

// 图鉴说明页：展示 doc 原文（1:1 同步），不依赖任何外站 URL/数据。
const goBack = () => router.back()
const goHome = () => router.push('/')

onMounted(() => load())
</script>

<template>
  <div class="handbook-intro">
    <div class="section title">{{ title }}</div>

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>
    <div class="section doc" v-else>{{ docText }}</div>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.handbook-intro {
  background: #ffffff;
  min-height: 100vh;
  padding: 14px 14px;
  font-size: 20px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
}

.spacer {
  margin-top: 16px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.doc {
  white-space: pre-wrap;
  word-break: break-word;
  color: #000;
}

.red {
  color: #CC3300;
}
</style>



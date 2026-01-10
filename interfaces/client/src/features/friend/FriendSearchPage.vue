<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const router = useRouter()
const route = useRoute()

const userId = ref(String(route.query.id || ''))

const doSearch = () => {
  const id = String(userId.value || '').trim()
  if (!id) {
    alert('请输入要查找的用户id')
    return
  }
  router.push({ path: '/player/detail', query: { id } })
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="friend-search-page">
    <div class="section">
      请输入要查找的用户id:
      <input class="id-input" v-model="userId" />
      <button class="btn" @click="doSearch">查找</button>
    </div>

    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.friend-search-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 6px 0;
}

.id-input {
  width: 220px;
  height: 22px;
  padding: 0 6px;
  border: 1px solid #aaa;
  margin: 0 6px;
}

.btn {
  height: 22px;
  padding: 0 8px;
  border: 1px solid #aaa;
  background: #f7f7f7;
  cursor: pointer;
}

.btn:hover {
  background: #eeeeee;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 16px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

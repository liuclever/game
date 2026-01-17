<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const msg = ref('领取成功，获得龙宫之谜探索礼包')

onMounted(() => {
  // 允许从上一页带入更具体的文案（例如后端返回的 item_name）
  const saved = sessionStorage.getItem('dragonpalaceLastClaimMsg')
  if (saved) {
    msg.value = saved
    sessionStorage.removeItem('dragonpalaceLastClaimMsg')
  }
})

const goBack = () => router.back()
const goInventory = () => router.push({ path: '/inventory', query: { tab: 'temp' } })
const goHome = () => router.push('/')
</script>

<template>
  <div class="dragonpalace-reward">
    <div class="section">{{ msg }}</div>

    <div class="section spacer">
      <a class="link" @click="goInventory">返回背包</a>
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
.dragonpalace-reward {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 18px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
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
</style>



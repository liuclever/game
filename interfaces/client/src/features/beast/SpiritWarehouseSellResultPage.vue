<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()
const route = useRoute()

const gained = computed(() => Number(route.query.gained || 0) || 0)

const goWarehouse = () => router.push('/spirit/warehouse')
const goHome = () => router.push('/')
</script>

<template>
  <div class="page">
    <div class="section title">【灵件室】</div>

    <div class="section">出售成功，获得{{ gained }}灵力</div>

    <div class="section spacer">
      <a class="link" @click="goWarehouse">返回战灵室</a>
    </div>
    <!-- 底部菜单（同款） -->
    <MainMenuLinks />
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 19.8px; /* +10% */
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}
.section {
  margin: 4px 0;
}
.title {
  font-weight: bold;
}
.spacer {
  margin-top: 16px;
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



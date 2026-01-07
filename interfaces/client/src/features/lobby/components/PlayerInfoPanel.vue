<script setup>
import { ref, onMounted } from 'vue'
import { fetchUser } from '../../../services/userService'

// 简单的本地 state
const user = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    loading.value = true
    // 这里先写死 userId=1，后面再做登录 / 切换用户
    user.value = await fetchUser(1)
  } catch (e) {
    console.error(e)
    error.value = '加载玩家信息失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="panel">
    <div class="title">【个人信息】</div>

    <!-- 加载中 / 错误提示 -->
    <div v-if="loading">正在加载...</div>
    <div v-else-if="error">{{ error }}</div>
    <template v-else>
      <div>等级：{{ user.level_text || `${user.level}级` }}</div>
      <div>经验：{{ user.exp }}/{{ user.next_exp || '??' }}</div>
      <div>活力：{{ user.energy }}/{{ user.max_energy }}</div>
      <div>水晶塔：{{ user.crystal || 0 }}/100</div>
      <div>战力：{{ user.power || 0 }}</div>
      <div>铜钱：{{ user.gold }}</div>
      <div>元宝：{{ user.diamond || 0 }}</div>
    </template>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
}

.title {
  margin-bottom: 4px;
}

div + div {
  margin-top: 2px;
}
</style>

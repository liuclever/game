<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchHandbookSkillDetail } from '@/services/handbookService'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const errorMsg = ref('')
const skill = ref(null)

const skillKey = computed(() => String(route.params.key || '').trim())

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    // 技能详情仅展示“技能名称 + 描述文案”，不展示任何外站链接。
    const res = await fetchHandbookSkillDetail(skillKey.value)
    if (res.data && res.data.ok) {
      skill.value = res.data.skill
    } else {
      errorMsg.value = (res.data && res.data.error) || '加载失败'
    }
  } catch (e) {
    console.error('加载技能详情失败', e)
    errorMsg.value = '加载失败'
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()
const goHome = () => router.push('/')

onMounted(() => load())
</script>

<template>
  <div class="handbook-skill">


    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else-if="skill">
      <div class="section skill-name">{{ skill.name }}</div>
      <div class="section indent">{{ skill.desc }}</div>

      <div class="section">
        <a class="link" @click="goBack">返回前页</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>
    </template>
  </div>
</template>

<style scoped>
.handbook-skill {
  background: #ffffff;
  min-height: 100vh;
  padding: 14px 14px;
  font-size: 18px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 10px 0;
}

.title {
  font-weight: bold;
}

.skill-name {
  font-weight: bold;
  font-size: 20px;
}

.indent {
  padding-left: 10px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.red {
  color: #CC3300;
}
</style>



<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchHandbookPetDetail } from '@/services/handbookService'
import { resolveHandbookImage } from './handbookImage'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const errorMsg = ref('')
const pet = ref(null)
const meta = ref({ realms: ['地界', '灵界', '神界'], realm_multipliers: { 地界: 1.0, 灵界: 1.1, 神界: 1.2 } })

const petId = computed(() => Number(route.params.id || 0))
const evolution = computed(() => Number(route.query.evolution || 0))
const realmFromRoute = computed(() => String(route.query.realm || '').trim())

const imageSrc = computed(() => {
  const p = pet.value
  return resolveHandbookImage(p && p.image)
})

const onImgError = (e) => {
  const img = e?.target
  if (!img) return
  // 兜底：错误时回退到默认图
  img.src = resolveHandbookImage(null)
}

const starText = (stars) => {
  const s = Number(stars || 0)
  if (s <= 0) return ''
  return '★'.repeat(Math.min(s, 5)) + '☆'.repeat(Math.max(0, 5 - Math.min(s, 5)))
}

const realms = computed(() => {
  const p = pet.value
  const chain = (p && p.evolution_chain) || []
  if (Array.isArray(chain) && chain.length) return chain
  const m = meta.value || {}
  const rs = m.realms || []
  return rs.length ? rs : ['地界', '灵界', '神界']
})

const realmMultipliers = computed(() => {
  const m = meta.value || {}
  const mp = m.realm_multipliers || {}
  return Object.keys(mp).length ? mp : { 地界: 1.0, 灵界: 1.1, 神界: 1.2 }
})

const selectedRealm = computed(() => {
  if (realmFromRoute.value && realms.value.includes(realmFromRoute.value)) return realmFromRoute.value
  const idx = Number.isFinite(evolution.value) ? evolution.value : 0
  return realms.value[idx] || realms.value[0] || '地界'
})

// 资质展示：后端已按“境界”返回一比一的精确值；这里仅做字段兼容（displayValue）即可。
const displayAptitudes = computed(() => {
  const p = pet.value
  const list = (p && p.max_initial_aptitudes) || []
  return list.map((a) => ({
    ...a,
    displayValue: Number(a.value || 0),
  }))
})

const displayMinAptitudes = computed(() => {
  const p = pet.value
  const list = (p && p.min_initial_aptitudes) || []
  return list.map((a) => ({
    ...a,
    displayValue: Number(a.value || 0),
  }))
})

const selectRealm = (realm, idx) => {
  const q = { ...(route.query || {}) }
  q.realm = realm
  q.evolution = Number.isFinite(idx) ? idx : 0
  router.replace({ path: route.path, query: q })
}

const goSkill = (skillKey) => {
  const key = String(skillKey || '').trim()
  if (!key) return
  router.push({ path: `/handbook/skill/${key}` })
}

const load = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await fetchHandbookPetDetail(petId.value, { evolution: evolution.value })
    if (res.data && res.data.ok) {
      pet.value = res.data.pet
      meta.value = res.data.meta || meta.value
    } else {
      errorMsg.value = (res.data && res.data.error) || '加载失败'
    }
  } catch (e) {
    console.error('加载图鉴详情失败', e)
    errorMsg.value = '加载失败'
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()
const goHome = () => router.push('/')

watch(
  () => [petId.value, evolution.value],
  () => load(),
)

onMounted(() => load())
</script>

<template>
  <div class="handbook-detail">

    <div class="section" v-if="loading">加载中...</div>
    <div class="section red" v-else-if="errorMsg">{{ errorMsg }}</div>

    <template v-else-if="pet">
      <div class="section">
        <img class="pet-image" :src="imageSrc" alt="pet" @error="onImgError" />
<!--        <template v-else>-->
<!--          <span class="gray">（暂无图片）</span>-->
<!--        </template>-->
      </div>

      <div class="section">
        本体:{{ pet.body || (pet.name + '(未知)') }}
      </div>
      <div class="section">
        进化:
        <span v-for="(r, idx) in realms" :key="r">
          <span v-if="idx > 0"> - </span>
          <template v-if="selectedRealm === r">
            <span>{{ r }}</span>
          </template>
          <template v-else>
            <a class="link" @click="selectRealm(r, idx)">{{ r }}</a>
          </template>
        </span>
      </div>
      <div class="section">特性:{{ pet.nature || '' }}</div>
      <div class="section">稀有:{{ pet.rarity || '' }}</div>
      <div class="section">属地:{{ pet.location || '' }}</div>

      <div class="section subtitle">最高初始资质：</div>
      <div class="section indent" v-for="a in displayAptitudes" :key="a.key">
        {{ a.label }}:{{ a.displayValue }}({{ starText(a.stars) }})
      </div>

      <template v-if="displayMinAptitudes.length">
        <div class="section subtitle">最低初始资质（地界）：</div>
        <div class="section indent" v-for="a in displayMinAptitudes" :key="`min-${a.key}`">
          {{ a.label }}:{{ a.displayValue }}<span v-if="starText(a.stars)">({{ starText(a.stars) }})</span>
        </div>
      </template>

      <div class="section">
        全技能:
        <span v-for="(s, idx) in (pet.skills || [])" :key="(s && s.key) || (s && s.name) || idx">
          <a class="skill-btn" @click="goSkill(s.key)">{{ s.name || s }}</a>
          <span v-if="idx < (pet.skills || []).length - 1"> | </span>
        </span>
      </div>

      <!-- 主页菜单（严格复刻主页内容与UI） -->
      <MainMenuLinks />

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
.handbook-detail {
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

.subtitle {
  font-weight: bold;
  margin-top: 10px;
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

.link.active {
  color: #CC3300;
  font-weight: bold;
}

.skill-btn {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid #ddd;
  background: #fff;
  color: #0066CC;
  cursor: pointer;
}

.skill-btn:hover {
  text-decoration: underline;
}

.pet-image {
  width: 216px; /* 约 3x */
  height: auto;
  border: 1px solid #ddd;
  background: #fff;
}

.red {
  color: #CC3300;
}

.gray {
  color: #666;
}
</style>

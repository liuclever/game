<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

let _beastTemplateTraitById = null
const loadBeastTemplateTraitById = async () => {
  if (_beastTemplateTraitById) return _beastTemplateTraitById
  _beastTemplateTraitById = new Map()
  try {
    const res = await http.get('/beast/templates')
    if (res.data?.ok && Array.isArray(res.data.templates)) {
      for (const t of res.data.templates) {
        if (!t) continue
        const id = Number(t.id)
        if (!Number.isFinite(id)) continue
        _beastTemplateTraitById.set(id, t.trait || '')
      }
    }
  } catch (e) {
    console.error('加载幻兽模板失败:', e)
  }
  return _beastTemplateTraitById
}

const resolveFullTrait = async (beastData) => {
  const fallback = beastData?.nature || ''
  const templateId = Number(beastData?.template_id)
  if (!Number.isFinite(templateId)) return fallback

  const map = await loadBeastTemplateTraitById()
  const fullTrait = map.get(templateId)
  return fullTrait || fallback
}

const router = useRouter()
const route = useRoute()

// 幻兽类型: guardian(守塔) 或 player(玩家)
const beastType = computed(() => route.query.beastType || 'guardian')
const beastId = computed(() => route.query.beastId || 1)
const towerType = computed(() => route.query.towerType || 'longwen')
const floor = computed(() => parseInt(route.query.floor) || 1)

// 幻兽数据
const beast = ref(null)
const loading = ref(true)
const error = ref('')

const renderStars = (solidStars, hollowStars = 0) => {
  return '★'.repeat(Number(solidStars || 0)) + '☆'.repeat(Number(hollowStars || 0))
}

const getAptStars = (key) => {
  const stars = beast.value?.aptitude_stars || {}
  const solid = stars?.[`${key}_solid_stars`] ?? 0
  const hollow = stars?.[`${key}_hollow_stars`] ?? 0
  return renderStars(solid, hollow)
}

const safeSkills = computed(() => {
  const s = beast.value?.skills
  return Array.isArray(s) ? s : []
})

const isPhysical = computed(() => {
  return String(beast.value?.trait || '').includes('物系')
})

const attackLabel = computed(() => (isPhysical.value ? '物攻' : '法攻'))
const attackValue = computed(() => (isPhysical.value ? beast.value?.physical_attack : beast.value?.magic_attack))

const attackAptitudeLabelKey = computed(() => (isPhysical.value ? 'physical_attack' : 'magic_attack'))
const attackAptitudeValue = computed(() => (isPhysical.value ? beast.value?.physical_attack_aptitude : beast.value?.magic_attack_aptitude))

const attackStarsKey = computed(() => 'magic_attack')

// 加载幻兽详情
const loadBeastDetail = async () => {
  loading.value = true
  error.value = ''
  
  try {
    let res
    if (beastType.value === 'guardian') {
      res = await http.get(`/tower/guardian/${towerType.value}/${floor.value}`)
      if (res.data.ok) {
        beast.value = res.data.guardian
      }
    } else {
      res = await http.get(`/tower/player-beast/${beastId.value}`)
      if (res.data.ok) {
        const data = res.data.beast
        const fullTrait = await resolveFullTrait(data)
        beast.value = { ...data, trait: fullTrait }
      }
    }
  } catch (e) {
    error.value = '加载失败'
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 返回闯塔页
const goBack = () => {
  router.back()
}

// 查看技能详情
const viewSkill = (skillName) => {
  router.push(`/handbook/skill/${encodeURIComponent(skillName)}`)
}

// 返回首页
const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadBeastDetail()
})
</script>

<template>
  <div class="beast-detail-page">
    <!-- 加载中 -->
    <div v-if="loading" class="section">加载中...</div>
    
    <!-- 错误 -->
    <div v-else-if="error" class="section red">{{ error }}</div>
    
    <!-- 守塔幻兽详情 -->
    <template v-else-if="beastType === 'guardian' && beast">
      <div class="section title">【{{ beast.name }}】</div>
      <div class="section">{{ beast.description }}</div>
      <div class="section">等级:{{ beast.level }}级</div>
      <div class="section">特性:{{ beast.nature }}</div>
      <div class="section">气血:{{ beast.hp }} | 法攻:{{ beast.magic_attack }}</div>
      <div class="section">物防:{{ beast.physical_defense }} | 法防:{{ beast.magic_defense }}</div>
      <div class="section">速度:{{ beast.speed }} | 综合战力:{{ beast.combat_power }}</div>
    </template>
    
    <!-- 玩家幻兽详情 -->
    <template v-else-if="beastType === 'player' && beast">
      <div class="section title">【{{ beast.name }}-{{ beast.realm }}】</div>
      <div class="section">本体:{{ beast.name }}-{{ beast.realm }}({{ beast.race }})</div>
      <div class="section">等级:{{ beast.level }}级</div>
      <div class="section">特性:{{ beast.trait }} | 性格:{{ beast.personality }}</div>
      <div class="section">气血:{{ beast.hp }} | {{ attackLabel }}:{{ attackValue }}</div>
      <div class="section">物防:{{ beast.physical_defense }} | 法防:{{ beast.magic_defense }}</div>
      <div class="section">速度:{{ beast.speed }} | 综合战力:{{ beast.combat_power }}</div>
      <div class="section">成长率:{{ beast.growth_rate }}(★★★★★)</div>
      <div class="section">气血资质:{{ beast.hp_aptitude }}({{ getAptStars('hp') }})</div>
      <div class="section">速度资质:{{ beast.speed_aptitude }}({{ getAptStars('speed') }})</div>
      <div class="section">{{ attackLabel }}资质:{{ attackAptitudeValue }}({{ getAptStars(attackStarsKey) }})</div>
      <div class="section">物防资质:{{ beast.physical_defense_aptitude }}({{ getAptStars('physical_defense') }})</div>
      <div class="section">法防资质:{{ beast.magic_defense_aptitude }}({{ getAptStars('magic_defense') }})</div>
      <div class="section">寿命:{{ beast.lifespan }}</div>
      <div class="section">
        技能: 
        <template v-for="(skill, idx) in safeSkills" :key="idx">
          <a class="link" @click="viewSkill(skill)">{{ skill }}</a>
          <template v-if="idx < safeSkills.length - 1"> | </template>
        </template>
      </div>
    </template>
    
    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回闯塔页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
    
  </div>
</template>

<style scoped>
.beast-detail-page {
  padding: 10px;
  font-size: 14px;
  line-height: 1.8;
}

.section {
  margin: 5px 0;
}

.title {
  font-weight: bold;
  color: #333;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.red {
  color: #cc0000;
}

.green {
  color: #009900;
}

.gray {
  color: #666;
}

.small {
  font-size: 12px;
}

.spacer {
  margin-top: 20px;
}

.footer {
  margin-top: 30px;
  border-top: 1px solid #ccc;
  padding-top: 10px;
}
</style>

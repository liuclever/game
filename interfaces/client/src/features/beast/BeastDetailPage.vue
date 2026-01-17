<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

// ========== 幻兽模板（用于展示完整特性） ==========
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

// ========== 加载状态 ==========
const loading = ref(true)
const errorMsg = ref('')

// ========== 幻兽基础信息 ==========
const beast = ref({})

// ========== 动态导入图片 ==========
const beastImageModules = {
  ...import.meta.glob('@/assets/images/image*.png', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.gif', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.jpg', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.jpeg', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.webp', { eager: true }),
}
const getBeastImage = (templateId) => {
  const id = Number(templateId)
  if (!Number.isFinite(id)) return ''
  const base = `/src/assets/images/image${id}`
  for (const ext of ['png', 'gif', 'jpg', 'jpeg', 'webp']) {
    const mod = beastImageModules[`${base}.${ext}`]
    if (!mod) continue
    return mod.default || mod || ''
  }
  return ''
}

// ========== 加载幻兽详情 ==========
const loadBeastDetail = async () => {
  loading.value = true
  errorMsg.value = ''
  
  const beastId = route.params.id
  if (!beastId) {
    errorMsg.value = '无效的幻兽ID'
    loading.value = false
    return
  }
  
  try {
    const res = await http.get(`/beast/${beastId}`)
    if (res.data.ok) {
      const data = res.data.beast
      const fullTrait = await resolveFullTrait(data)
      beast.value = {
        id: data.id,
        name: data.name,
        realm: data.realm,
        race: data.race,
        templateId: data.template_id,
        level: data.level,
        status: '出战中',  // TODO: 从后端获取
        
        // 经验
        exp: data.exp || 0,
        expMax: data.exp_max || 0,
        
        // 特性和性格
        trait: fullTrait,
        personality: data.personality,
        
        // 攻击类型（根据特性判断）
        isPhysical: fullTrait.includes('物系'),
        
        // 基础属性
        hp: data.hp,
        physicalAttack: data.physical_attack,
        magicAttack: data.magic_attack,
        physicalDefense: data.physical_defense,
        magicDefense: data.magic_defense,
        speed: data.speed,
        power: data.combat_power,
        
        // 成长率
        growthRate: data.growth_rate,
        growthStars: 5,  // 成长率固定显示5颗星
        
        // 资质（使用后端计算的星级）
        hpQuality: data.hp_aptitude,
        hpSolidStars: data.aptitude_stars?.hp_solid_stars ?? 0,
        hpHollowStars: data.aptitude_stars?.hp_hollow_stars ?? 0,
        speedQuality: data.speed_aptitude,
        speedSolidStars: data.aptitude_stars?.speed_solid_stars ?? 0,
        speedHollowStars: data.aptitude_stars?.speed_hollow_stars ?? 0,
        // 攻击资质（数据库统一存储在 magic_attack_aptitude）
        attackQuality: fullTrait.includes('物系') ? data.physical_attack_aptitude : data.magic_attack_aptitude,
        attackSolidStars: data.aptitude_stars?.magic_attack_solid_stars ?? 0,
        attackHollowStars: data.aptitude_stars?.magic_attack_hollow_stars ?? 0,
        physicalDefenseQuality: data.physical_defense_aptitude,
        physicalDefenseSolidStars: data.aptitude_stars?.physical_defense_solid_stars ?? 0,
        physicalDefenseHollowStars: data.aptitude_stars?.physical_defense_hollow_stars ?? 0,
        magicDefenseQuality: data.magic_defense_aptitude,
        magicDefenseSolidStars: data.aptitude_stars?.magic_defense_solid_stars ?? 0,
        magicDefenseHollowStars: data.aptitude_stars?.magic_defense_hollow_stars ?? 0,
        
        // 寿命
        life: parseLifespan(data.lifespan).current,
        lifeMax: parseLifespan(data.lifespan).max,
        
        // 技能
        skills: data.skills || [],
        
        // 强化系统
        battleBone: data.bone_count || 0,
        battleBoneMax: 7,
        battleSpirit: data.spirit_count || 0,
        battleSpiritMax: 6,
        magicSoul: data.mosoul_count || 0,
        magicSoulMax: data.max_mosoul_slots || 8,
      }
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载幻兽详情失败:', err)
  } finally {
    loading.value = false
  }
}


// 解析寿命字符串 "10000/10000"
const parseLifespan = (lifespan) => {
  if (!lifespan) return { current: 10000, max: 10000 }
  const parts = lifespan.split('/')
  return {
    current: parseInt(parts[0]) || 10000,
    max: parseInt(parts[1]) || 10000,
  }
}

onMounted(() => {
  loadBeastDetail()
})

// ========== 星级显示 ==========
const renderStars = (solidStars, hollowStars = 0) => {
  // 实心星 + 空心星
  return '★'.repeat(solidStars) + '☆'.repeat(hollowStars)
}

// ========== 操作 ==========
const evolve = () => {
  router.push(`/beast/${beast.value.id}/evolve`)
}

const rebirth = () => {
  const input = prompt('选择重生方式：\n1=重生丹（重置资质/性格/技能，等级1，境界地界）\n2=神奇重生丹（仅重置资质/性格，不改技能/等级/境界）', '1')
  if (!input) return
  const mode = String(input).trim() === '2' ? 'magic' : 'normal'

  ;(async () => {
    try {
      const res = await http.post('/beast/rebirth', { beastId: beast.value.id, mode })
      if (res.data?.ok) {
        console.error('重生成功')
        await loadBeastDetail()
      } else {
        console.error(res.data?.error || '重生失败')
      }
    } catch (e) {
      console.error('重生失败:', e)
      console.error(e?.response?.data?.error || '重生失败')
    }
  })()
}

const release = async () => {
  if (!confirm('确定要放生这只幻兽吗？放生后将无法找回！')) {
    return
  }
  
  try {
    const res = await http.delete(`/beast/${beast.value.id}`)
    if (res.data.ok) {
      console.error(res.data.message || '放生成功')
      router.push('/beast')
    } else {
      console.error(res.data.error || '放生失败')
    }
  } catch (err) {
    console.error('网络错误，请稍后重试')
    console.error('放生幻兽失败:', err)
  }
}

const learnSkill = () => {
  router.push(`/beast/${beast.value.id}/skill-book`)
}

const viewBattleBone = () => {
  router.push(`/beast/${beast.value.id}/bone`)
}

const viewBattleSpirit = () => {
  router.push(`/beast/${beast.value.id}/spirit`)
}

const viewMagicSoul = () => {
  router.push(`/beast/${beast.value.id}/mosoul`)
}

const viewSkillDetail = (skillName) => {
  // 将技能名称转换为key（使用技能名称作为key）
  const skillKey = encodeURIComponent(skillName)
  router.push(`/handbook/skill/${skillKey}`)
}

// ========== 导航 ==========
const goBack = () => {
  router.push('/beast')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>
    
    <!-- 幻兽详情 -->
    <template v-else>
      <!-- 幻兽图片 -->
      <div class="beast-icon">
        <img v-if="getBeastImage(beast.templateId)" :src="getBeastImage(beast.templateId)" alt="幻兽" class="beast-image" />
        <span v-else>🐉</span>
      </div>

      <!-- 基础信息 -->
      <div class="section">
      本体:<a class="link">{{ beast.name }}-{{ beast.realm }}</a>({{ beast.race }})
    </div>
    <div class="section">
      等级:{{ beast.level }}级
    </div>
    <div class="section">
      状态: {{ beast.status }}
    </div>
    <div class="section">
      经验:{{ beast.exp }}/{{ beast.expMax }}
    </div>
    <div class="section">
      特性:{{ beast.trait }} | 性格:{{ beast.personality }}
    </div>

    <!-- 战斗属性 -->
    <div class="section">
      气血:{{ beast.hp }} | {{ beast.isPhysical ? '物攻' : '法攻' }} :{{ beast.isPhysical ? beast.physicalAttack : beast.magicAttack }}
    </div>
    <div class="section">
      物防:{{ beast.physicalDefense }} | 法防 :{{ beast.magicDefense }}
    </div>
    <div class="section">
      速度:{{ beast.speed }} | 综合战力:{{ beast.power }}
    </div>

    <!-- 成长率 -->
    <div class="section">
      成长率: {{ beast.growthRate }}({{ renderStars(beast.growthStars, 0) }})
    </div>

    <!-- 资质 -->
    <div class="section">
      气血资质:{{ beast.hpQuality }}({{ renderStars(beast.hpSolidStars, beast.hpHollowStars) }})
    </div>
    <div class="section">
      速度资质:{{ beast.speedQuality }}({{ renderStars(beast.speedSolidStars, beast.speedHollowStars) }})
    </div>
    <div class="section">
      {{ beast.isPhysical ? '物攻' : '法攻' }}资质:{{ beast.attackQuality }}({{ renderStars(beast.attackSolidStars, beast.attackHollowStars) }})
    </div>
    <div class="section">
      物防资质:{{ beast.physicalDefenseQuality }}({{ renderStars(beast.physicalDefenseSolidStars, beast.physicalDefenseHollowStars) }})
    </div>
    <div class="section">
      法防资质:{{ beast.magicDefenseQuality }}({{ renderStars(beast.magicDefenseSolidStars, beast.magicDefenseHollowStars) }})
    </div>

    <!-- 寿命 -->
    <div class="section">
      寿命:{{ beast.life }}/{{ beast.lifeMax }}
    </div>

    <!-- 技能 -->
    <div class="section">
      技能:
      <template v-for="(skill, index) in beast.skills" :key="index">
        <a class="link" @click="viewSkillDetail(skill)">{{ skill }}</a>
        <template v-if="index < beast.skills.length - 1"> | </template>
      </template>
      | <a class="link" @click="learnSkill">打书</a>
    </div>

    <!-- 强化系统 -->
    <div class="section">
      战骨:{{ beast.battleBone }}/{{ beast.battleBoneMax }}<a class="link" @click="viewBattleBone">查看</a>
    </div>
    <div class="section">
      战灵:{{ beast.battleSpirit }}/{{ beast.battleSpiritMax }}<a class="link" @click="viewBattleSpirit">查看</a>
    </div>
    <div class="section">
      魔魂:{{ beast.magicSoul }}/{{ beast.magicSoulMax }}<a class="link" @click="viewMagicSoul">查看</a>
    </div>

    <!-- 操作 -->
    <div class="section">
      <a class="link" @click="evolve">进化</a>  
      <a class="link" @click="rebirth">重生</a>  
      <a class="link" @click="release">放生</a>
    </div>

    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回幻兽栏</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

    </template>
  </div>
</template>

<style scoped>
.detail-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.beast-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.beast-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
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

.gray {
  color: #666666;
}

.small {
  font-size: 17px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()
// ========== 幻兽模板数据（来自根目录 configs/templates.json） ==========
const beastTemplates = ref([])
const loadBeastTemplates = async () => {
  try {
    // ⚠️ 关键点：configs 在项目根目录，需要后端或 nginx 静态暴露
    const res = await fetch('/configs/beast_templates.json')
    const data = await res.json()
    beastTemplates.value = data.templates || []  // 取 templates 数组
  } catch (e) {
    beastTemplates.value = []
    console.error('加载 beast_templates.json 失败', e)
  }
}
const currentTemplate = computed(() => {
  const tid = beast.value?.templateId
  if (!tid) return null
  return beastTemplates.value.find(t => Number(t.id) === Number(tid)) || null
})
const templateMaxRealm = computed(() => {
  const realms = currentTemplate.value?.realms
  if (!realms) return ''

  const realmKeys = Object.keys(realms)
  if (!realmKeys.length) return ''

  let maxIdx = -1
  let maxRealm = ''

  for (const r of realmKeys) {
    const idx = REALM_ORDER_LOW_TO_HIGH.indexOf(r)
    if (idx > maxIdx) {
      maxIdx = idx
      maxRealm = r
    }
  }
  return maxRealm
})
const isMaxRealm = computed(() => {
  const cur = beast.value?.realm
  const max = templateMaxRealm.value
  if (!cur || !max) return false
  return cur === max
})
const loading = ref(true)
const errorMsg = ref('')

const beast = ref({
  id: null,
  name: '',
  level: 0,
  realm: '',
  templateId: null,
})

// ========== 玩家信息 ==========
// 用于计算“等级段”进化条件
const playerLevel = ref(null)
// 铜钱（后端字段名为 gold）
const playerGold = ref(null)

// ========== 战骨装备信息 ==========
// /api/bone/beast/:id/equipped 返回的 slots 对象
const equippedBoneSlots = ref({})

// ========== 背包物品信息 ==========
// /api/inventory/list 返回的 items 数组
const bagItems = ref([])

const SHEN_NI_LIN_ITEM_ID = 3010

const SHEN_NI_LIN_NAME = '神逆鳞'
const EVOLVE_GOD_HERB_NAME = '进化神草'
const EVOLVE_CRYSTAL_NAME = '进化水晶'

const formatNumber = (n) => {
  if (n === null || n === undefined) return '-'
  const num = Number(n)
  if (!Number.isFinite(num)) return '-'
  return num.toLocaleString('zh-CN')
}

const normalizeName = (s) => String(s || '').replace(/[·\s]/g, '')


const FULL_BONE_SLOT_COUNT = 7
const BONE_STAGE_NAMES = {
  1: '原始',
  2: '碎空',
  3: '猎魔',
  4: '龙炎',
  5: '奔雷',
  6: '凌霄',
  7: '麒麟',
  8: '武神',
  9: '弑天',
  10: '毁灭',
}

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

// ========== 进化结果：下一个境界 ==========
const REALM_ORDER_LOW_TO_HIGH = ['地界', '灵界', '神界', '天界']

const nextRealm = computed(() => {
  if (isMaxRealm.value) return ''
  const current = beast.value?.realm
  const idx = REALM_ORDER_LOW_TO_HIGH.indexOf(current)
  if (idx < 0) return ''
  return REALM_ORDER_LOW_TO_HIGH[idx + 1] || ''
})

// ========== 进化条件1：幻兽等级要求与玩家等级段相关 ==========
// 例：玩家20-29 => 幻兽>=20；玩家30-39 => 幻兽>=30；依此类推
const requiredBeastLevel = computed(() => {
  if (playerLevel.value === null || playerLevel.value === undefined) return null
  const lvl = Number(playerLevel.value) || 0
  return Math.floor(lvl / 10) * 10
})

const playerLevelBracketText = computed(() => {
  const required = requiredBeastLevel.value
  if (required === null) return '未知'
  return `${required}-${required + 9}`
})

// ========== 进化条件2：战骨套装 & 等级段要求 ==========
// 战骨阶段与玩家等级段关联：
// 0-9 => 1(原始), 10-19 => 2(碎空), ... 70-79 => 8(武神), 80-89 => 9(弑天), 90-99 => 10(毁灭)
const requiredBoneStage = computed(() => {
  if (playerLevel.value === null || playerLevel.value === undefined) return null
  const lvl = Number(playerLevel.value) || 0
  const stage = Math.floor(lvl / 10) + 1
  return Math.min(10, Math.max(1, stage))
})

const requiredBoneStageName = computed(() => {
  const st = requiredBoneStage.value
  if (!st) return ''
  return BONE_STAGE_NAMES[st] || ''
})

const equippedBoneList = computed(() => Object.values(equippedBoneSlots.value || {}))
const equippedBoneCount = computed(() => equippedBoneList.value.length)

const hasFullBoneSet = computed(() => equippedBoneCount.value >= FULL_BONE_SLOT_COUNT)

const minEquippedBoneStage = computed(() => {
  if (!equippedBoneCount.value) return null
  let min = Infinity
  for (const b of equippedBoneList.value) {
    const st = Number(b?.stage || 0)
    if (st > 0) min = Math.min(min, st)
  }
  return min === Infinity ? null : min
})

const minEquippedBoneStageName = computed(() => {
  const st = minEquippedBoneStage.value
  if (!st) return ''
  return BONE_STAGE_NAMES[st] || ''
})

const minEquippedBoneLevel = computed(() => {
  if (!equippedBoneCount.value) return null
  let min = Infinity
  for (const b of equippedBoneList.value) {
    const lv = Number(b?.level || 0)
    if (lv > 0) min = Math.min(min, lv)
  }
  return min === Infinity ? null : min
})

// 阶段要求：必须装备“对应玩家等级段”的战骨或更高阶段
const bonesMeetStage = computed(() => {
  if (!hasFullBoneSet.value) return false
  const requiredStage = requiredBoneStage.value
  const minStage = minEquippedBoneStage.value
  if (!requiredStage || !minStage) return false
  return minStage >= requiredStage
})

// 等级要求：战骨等级必须 >= 玩家等级段起点（同等级段或更高）
const bonesMeetLevel = computed(() => {
  if (!hasFullBoneSet.value) return false
  const required = requiredBeastLevel.value
  const minLevel = minEquippedBoneLevel.value
  if (required === null || minLevel === null) return false
  return minLevel >= required
})

// ========== 进化条件3：材料（按境界进化段不同而变化） ==========
const bagQtyMap = computed(() => {
  const map = {}
  for (const it of bagItems.value || []) {
    const itemId = Number(it?.item_id)
    if (!Number.isFinite(itemId)) continue
    map[itemId] = (map[itemId] || 0) + Number(it?.quantity || 0)
  }
  return map
})

const bagQtyByNameMap = computed(() => {
  const map = {}
  for (const it of bagItems.value || []) {
    const nameKey = normalizeName(it?.name)
    if (!nameKey) continue
    map[nameKey] = (map[nameKey] || 0) + Number(it?.quantity || 0)
  }
  return map
})

const getBagQty = (itemId, itemName) => {
  const byId = itemId ? Number(bagQtyMap.value[itemId] || 0) : 0
  if (byId > 0) return byId

  const key = normalizeName(itemName)
  if (!key) return 0
  return Number(bagQtyByNameMap.value[key] || 0)
}

const shenNiLinQty = computed(() => getBagQty(SHEN_NI_LIN_ITEM_ID, SHEN_NI_LIN_NAME))
const evolveGodHerbQty = computed(() => getBagQty(null, EVOLVE_GOD_HERB_NAME))
const evolveCrystalQty = computed(() => getBagQty(null, EVOLVE_CRYSTAL_NAME))

const evolveTransition = computed(() => {
  const cur = beast.value?.realm || ''
  const nxt = nextRealm.value || ''
  if (!cur || !nxt) return ''
  return `${cur}->${nxt}`
})

const requiredShenNiLinCost = computed(() => {
  if (evolveTransition.value === '地界->灵界') return 1
  if (evolveTransition.value === '灵界->神界') return 4
  if (evolveTransition.value === '神界->天界') return 10
  return null
})

const requiredGoldCost = computed(() => {
  if (evolveTransition.value === '灵界->神界') return 2000000
  if (evolveTransition.value === '神界->天界') return 5000000
  return 0
})

const shenNiLinOk = computed(() => {
  const cost = requiredShenNiLinCost.value
  if (cost === null) return false
  return shenNiLinQty.value >= cost
})

const evolveGodHerbOk = computed(() => {
  if (evolveTransition.value !== '灵界->神界') return true
  return evolveGodHerbQty.value >= 90
})

const evolveCrystalOk = computed(() => {
  if (evolveTransition.value !== '神界->天界') return true
  return evolveCrystalQty.value >= 60
})

const goldOk = computed(() => {
  const cost = Number(requiredGoldCost.value || 0)
  if (cost <= 0) return true
  if (playerGold.value === null || playerGold.value === undefined) return false
  return Number(playerGold.value || 0) >= cost
})

// ========== 总进化判定 ==========
const canEvolve = computed(() => {
  if (isMaxRealm.value) return false
  if (!nextRealm.value) return false

  const required = requiredBeastLevel.value
  if (required === null) return false
  if (Number(beast.value?.level || 0) < required) return false

  if (!hasFullBoneSet.value) return false
  if (!bonesMeetStage.value) return false
  if (!bonesMeetLevel.value) return false

  // 材料条件（按境界段）
  if (evolveTransition.value === '地界->灵界') {
    if (!shenNiLinOk.value) return false
    return true
  }

  if (evolveTransition.value === '灵界->神界') {
    if (!evolveGodHerbOk.value) return false
    if (!shenNiLinOk.value) return false
    if (!goldOk.value) return false
    return true
  }

  if (evolveTransition.value === '神界->天界') {
    if (!evolveCrystalOk.value) return false
    if (!shenNiLinOk.value) return false
    if (!goldOk.value) return false
    return true
  }

  // 未配置的进化路径
  return false
})

const evolveConditions = computed(() => {
  const required = requiredBeastLevel.value
  const beastLvOk = required !== null && Number(beast.value?.level || 0) >= required

  const requiredStage = requiredBoneStage.value
  const requiredStageName = requiredBoneStageName.value

  const stageOk = bonesMeetStage.value
  const boneLevelOk = bonesMeetLevel.value

  const base = [
    {
      ok: beastLvOk,
      text:
        required === null
          ? '幻兽等级要求：需要达到玩家等级段起点（玩家等级未加载）'
          : `幻兽等级要求：玩家等级段 ${playerLevelBracketText.value}，幻兽需≥${required}（当前：${beast.value?.level || 0}）`,
    },
    {
      ok: hasFullBoneSet.value,
      text: `战骨套装要求：需装备一套战骨（当前：${equippedBoneCount.value}/${FULL_BONE_SLOT_COUNT}）`,
    },
    {
      ok: stageOk,
      text:
        requiredStage === null
          ? '战骨阶段要求：需装备对应等级段战骨或更高（玩家等级未加载）'
          : `战骨阶段要求：战骨等级段需≥${requiredStageName}阶段（${requiredStageName}战骨）以上（当前最低：${minEquippedBoneStageName.value || '-'}）`,
    },
    
  ]

  // 材料条件（按境界段）
  const mats = []

  if (evolveTransition.value === '地界->灵界') {
    mats.push({
      ok: shenNiLinOk.value,
      text: `进化材料要求：消耗${SHEN_NI_LIN_NAME}×${requiredShenNiLinCost.value}（当前：${shenNiLinQty.value}）`,
    })
  } else if (evolveTransition.value === '灵界->神界') {
    mats.push({
      ok: evolveGodHerbOk.value,
      text: `进化材料要求：消耗${EVOLVE_GOD_HERB_NAME}×90（当前：${evolveGodHerbQty.value}）`,
    })
    mats.push({
      ok: shenNiLinOk.value,
      text: `进化材料要求：消耗${SHEN_NI_LIN_NAME}×${requiredShenNiLinCost.value}（当前：${shenNiLinQty.value}）`,
    })
    mats.push({
      ok: goldOk.value,
      text: `铜钱要求：消耗${formatNumber(requiredGoldCost.value)}铜钱（当前：${formatNumber(playerGold.value)}）`,
    })
  } else if (evolveTransition.value === '神界->天界') {
    mats.push({
      ok: evolveCrystalOk.value,
      text: `进化材料要求：消耗${EVOLVE_CRYSTAL_NAME}×60（当前：${evolveCrystalQty.value}）`,
    })
    mats.push({
      ok: shenNiLinOk.value,
      text: `进化材料要求：消耗${SHEN_NI_LIN_NAME}×${requiredShenNiLinCost.value}（当前：${shenNiLinQty.value}）`,
    })
    mats.push({
      ok: goldOk.value,
      text: `铜钱要求：消耗${formatNumber(requiredGoldCost.value)}铜钱（当前：${formatNumber(playerGold.value)}）`,
    })
  } else if (nextRealm.value) {
    mats.push({
      ok: false,
      text: `进化材料要求：未配置（${beast.value?.realm || '-'} → ${nextRealm.value}）`,
    })
  }

  return [...base, ...mats]
})

const loadPlayerInfo = async () => {
  try {
    const playerRes = await http.get('/player/info')
    if (playerRes.data?.ok) {
      playerLevel.value = playerRes.data.player?.level ?? null
      playerGold.value = playerRes.data.player?.gold ?? null
    } else {
      playerLevel.value = null
      playerGold.value = null
    }
  } catch (e) {
    playerLevel.value = null
    playerGold.value = null
    console.error('加载玩家信息失败:', e)
  }
}

const loadEquippedBones = async (beastId) => {
  try {
    const boneRes = await http.get(`/bone/beast/${beastId}/equipped`)
    if (boneRes.data?.ok) {
      equippedBoneSlots.value = boneRes.data.slots || {}
    } else {
      equippedBoneSlots.value = {}
    }
  } catch (e) {
    equippedBoneSlots.value = {}
    console.error('加载幻兽战骨信息失败:', e)
  }
}

const loadBagItems = async () => {
  try {
    const invRes = await http.get('/inventory/list')
    if (invRes.data?.ok) {
      bagItems.value = invRes.data.items || []
    } else {
      bagItems.value = []
    }
  } catch (e) {
    bagItems.value = []
    console.error('加载背包信息失败:', e)
  }
}

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
      beast.value = {
        id: data.id,
        name: data.name,
        level: data.level,
        realm: data.realm,
        templateId: data.template_id,
      }

      // 进化条件需要玩家等级 + 战骨装备信息 + 背包材料
      await Promise.all([loadPlayerInfo(), loadEquippedBones(beastId), loadBagItems()])
    } else {
      errorMsg.value = res.data.error || '加载失败'
    }
  } catch (err) {
    errorMsg.value = '网络错误，请稍后重试'
    console.error('加载进化页面数据失败:', err)
  } finally {
    loading.value = false
  }
}

const confirmEvolve = async () => {
  if (!canEvolve.value) {
    console.error('条件不满足，无法进化')
    return
  }

  const beastId = route.params.id
  const targetRealm = nextRealm.value

  try {
    const res = await http.post('/beast/evolve', {
      beastId: Number(beastId),
      nextRealm: targetRealm,
      realmMultiplier: 1.0,
    })

    if (res.data.ok) {
      console.error(`进化成功！【${beast.value.name}】已进化至${res.data.newRealm}`)
      // 直接跳转回幻兽详情页，让详情页重新加载最新数据
      router.push(`/beast/${beastId}`)
    } else {
      console.error(res.data.error || '进化失败')
    }
  } catch (err) {
    console.error('进化失败:', err)
    console.error('进化失败，请稍后重试')
  }
}

const goBack = () => {
  router.push(`/beast/${route.params.id}`)
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  loadBeastTemplates()
  loadBeastDetail()
})
</script>

<template>
  <div class="evolve-page">
    <div v-if="loading" class="section">加载中...</div>
    <div v-else-if="errorMsg" class="section" style="color: red;">{{ errorMsg }}</div>

    <template v-else>
      <div class="section title">【幻兽进化】简介</div>

      <div class="beast-row">
        <div class="beast-icon">
          <img
            v-if="getBeastImage(beast.templateId)"
            :src="getBeastImage(beast.templateId)"
            alt="幻兽"
            class="beast-image"
          />
          <span v-else>🐉</span>
        </div>

        <div class="beast-info">
          <div class="section">您选择进化的幻兽：{{ beast.name }}</div>
          <div class="section">等级：{{ beast.level }}级</div>
        </div>
      </div>

        <div v-if="isMaxRealm" class="section max-realm-notice">
          幻兽已到达最高境界
        </div>

        <template v-else>
          <div class="section">进化条件：</div>
          <div v-for="(c, idx) in evolveConditions" :key="idx" class="section">
            {{ idx + 1 }}. {{ c.text }}（{{ c.ok ? '满足' : '不满足' }}）
          </div>

          <div class="section">进化结果：{{ nextRealm }}</div>

          <div class="section" v-if="!canEvolve">条件不满足无法进化</div>
          <div class="section" v-else>
            <button class="page-btn" @click="confirmEvolve">确认进化</button>
          </div>
        </template>

      <div class="section spacer">
        <a class="link" @click="goBack">返回幻兽详情</a>
      </div>
      <div class="section">
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>

    </template>
  </div>
</template>

<style scoped>
.evolve-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  margin-bottom: 8px;
}

.beast-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 6px;
}

.beast-icon {
  font-size: 48px;
}

.beast-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
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

.page-btn {
  font-size: 18px;
  padding: 1px 8px;
  background: #ffffff;
  border: 1px solid #CCCCCC;
  cursor: pointer;
}

.page-btn:hover {
  background: #ffffff;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}

.max-realm-notice {
  font-weight: bold;
  color: #CC6600;
  margin: 12px 0;
}
</style>

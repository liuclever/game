<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const route = useRoute()

const battleData = ref(null)
const showDetail = ref(false)
const expandedBattles = ref(new Set())

// 动态导入幻兽图片
const beastImageModules = import.meta.glob('@/assets/images/image*.jpeg', { eager: true })
const getBeastImage = (templateId) => {
  if (!templateId) return ''
  const key = `/src/assets/images/image${templateId}.jpeg`
  const module = beastImageModules[key]
  return module?.default || ''
}

const loadBattleData = async () => {
  // 优先从 sessionStorage 读取（挑战后直接跳转）
  const storedData = sessionStorage.getItem('king_battle_report')
  if (storedData) {
    try {
      battleData.value = JSON.parse(storedData)
      sessionStorage.removeItem('king_battle_report')
      return
    } catch (e) {
      console.error('解析战报数据失败', e)
    }
  }
  
  // 从 URL 参数读取 logId（点击动态查看）
  const logId = route.query.logId
  if (!logId) {
    console.error('缺少战报ID')
    router.push('/king')
    return
  }

  try {
    const res = await http.get(`/king/battle-report/${logId}`)
    if (res.data.ok) {
      battleData.value = res.data.battleReport
    } else {
      console.error('加载战报失败:', res.data.error)
      router.push('/king')
    }
  } catch (e) {
    console.error('加载战报失败', e)
    router.push('/king')
  }
}

const resultText = computed(() => {
  if (!battleData.value) return ''
  const result = battleData.value.result || ''
  if (result.includes('完美胜利')) return '完美胜利'
  if (result.includes('胜利')) return '胜利'
  if (result.includes('失败')) return '失败'
  return result
})

const resultSymbol = computed(() => {
  if (!battleData.value) return ''
  const result = battleData.value.result || ''
  // 从结果中提取符号，例如 (⚬⚬⚬⚬:×××)
  const match = result.match(/\([⚬×]+:[⚬×]+\)/)
  return match ? match[0] : ''
})

const goBack = () => {
  router.push('/king')
}

const goHome = () => {
  router.push('/')
}

const viewDetailReport = () => {
  showDetail.value = !showDetail.value
}

const toggleBattle = (battleNum) => {
  if (expandedBattles.value.has(battleNum)) {
    expandedBattles.value.delete(battleNum)
  } else {
    expandedBattles.value.add(battleNum)
  }
}

const isBattleExpanded = (battleNum) => {
  return expandedBattles.value.has(battleNum)
}

onMounted(() => {
  loadBattleData()
})
</script>

<template>
  <div class="report-page">
    <template v-if="battleData">
      <!-- 挑战结果标题 -->
      <div class="section">挑战结果：</div>
      
      <!-- 凝神香加成 -->
      <div class="section">凝神香加成:{{ battleData.incense_bonus || '无' }}</div>
      
      <!-- 对战双方 -->
      <div class="section">
        {{ battleData.attacker_name }} vs {{ battleData.defender_name }}
      </div>
      
      <!-- PK图标 -->
      <div class="section pk-section">
        <div class="beasts-row">
          <div v-for="(beast, idx) in battleData.attacker_beasts" :key="'a' + idx" class="beast-item">
            <img v-if="getBeastImage(beast.template_id)" :src="getBeastImage(beast.template_id)" :alt="beast.name" class="beast-image">
            <span v-else class="beast-icon">🐉</span>
            <div class="beast-name">{{ beast.name }}</div>
          </div>
        </div>
        <span class="pk-text">PK</span>
        <div class="beasts-row">
          <div v-for="(beast, idx) in battleData.defender_beasts" :key="'d' + idx" class="beast-item">
            <img v-if="getBeastImage(beast.template_id)" :src="getBeastImage(beast.template_id)" :alt="beast.name" class="beast-image">
            <span v-else class="beast-icon">🐉</span>
            <div class="beast-name">{{ beast.name }}</div>
          </div>
        </div>
      </div>
      
      <!-- 幻兽经验 -->
      <div v-for="(beast, idx) in battleData.attacker_beasts" :key="idx" class="section">
        {{ beast.name }}-{{ beast.realm }}经验+{{ beast.exp_gain || 0 }}
      </div>
      
      <!-- 战斗结果 -->
      <div class="section result-line">
        【我】{{ resultText }}{{ resultSymbol }}
      </div>
      
      <!-- 活力消耗 -->
      <div class="section">活力-{{ battleData.energy_cost || 0 }}</div>
      
      <!-- 战斗过程 -->
      <template v-for="(battle, bIdx) in battleData.battles" :key="bIdx">
        <div class="section battle-log">
          <a class="link" @click="toggleBattle(battle.battle_num)">
            [第{{ battle.battle_num }}战]{{ battle.summary }}
          </a>
        </div>
        
        <!-- 详细回合信息（展开时显示） -->
        <template v-if="isBattleExpanded(battle.battle_num)">
          <div class="section indent battle-detail">
            <div class="battle-result">{{ battle.result }}</div>
            <template v-for="(round, rIdx) in battle.rounds" :key="rIdx">
              <div class="round-info">
                第{{ round.round }}回合: {{ round.action }}
              </div>
              <div class="hp-info">
                攻方气血: {{ round.a_hp }} | 守方气血: {{ round.d_hp }}
              </div>
            </template>
          </div>
        </template>
      </template>
      
      <!-- 挑战战绩 -->
      <div class="section">
        挑战战绩:{{ battleData.spar_wins || 0 }}/{{ battleData.spar_total || 0 }} 
        (胜率{{ battleData.spar_win_rate || '0.00' }}%)
      </div>
    </template>

    <div v-else class="section">加载中...</div>

    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回召唤之王</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.report-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.section.indent {
  margin-left: 20px;
}

.pk-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 12px 0;
}

.beasts-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.beast-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.beast-image {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.beast-icon {
  font-size: 48px;
  line-height: 48px;
}

.beast-name {
  font-size: 11px;
  text-align: center;
  max-width: 60px;
  word-break: break-all;
}

.pk-text {
  font-weight: bold;
  font-size: 16px;
  margin: 0 8px;
}

.result-line {
  font-weight: bold;
}

.battle-log {
  color: #333;
}

.battle-detail {
  background: #FFF5E6;
  padding: 8px;
  margin: 4px 0;
  border-left: 2px solid #CCC;
}

.battle-result {
  font-weight: bold;
  margin-bottom: 6px;
  color: #006600;
}

.round-info {
  margin: 2px 0;
  color: #333;
}

.hp-info {
  margin: 2px 0 6px 0;
  color: #666;
  font-size: 12px;
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

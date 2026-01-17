<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBattleReportPagination } from '@/composables/useBattleReportPagination'

const router = useRouter()
const route = useRoute()

const battleData = ref(null)
const expandedBattles = ref(new Set())
const battlePaginations = ref(new Map()) // 存储每个战斗的分页状态

const loadBattleData = () => {
  try {
    const dataStr = route.query.data
    if (dataStr) {
      battleData.value = JSON.parse(dataStr)
    }
  } catch (e) {
    console.error('解析战报数据失败', e)
  }
}

const resultText = computed(() => {
  if (!battleData.value) return ''
  const result = battleData.value.result || ''
  if (result.includes('完美胜利')) return '完美胜利'
  if (result.includes('胜利')) return '胜利'
  if (result.includes('失败')) return '失败'
  return battleData.value.is_victory ? '胜利' : '失败'
})

const resultSymbol = computed(() => {
  if (!battleData.value) return ''
  const result = battleData.value.result || ''
  const match = result.match(/\([⚬×]+:[⚬×]+\)/)
  return match ? match[0] : ''
})

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}

const toggleBattle = (battleNum) => {
  if (expandedBattles.value.has(battleNum)) {
    expandedBattles.value.delete(battleNum)
  } else {
    expandedBattles.value.add(battleNum)
    // 为新展开的战斗创建分页
    if (!battlePaginations.value.has(battleNum)) {
      const battle = battleData.value.battles.find(b => b.battle_num === battleNum)
      if (battle) {
        const rounds = ref(battle.rounds || [])
        const pagination = useBattleReportPagination(rounds, 10)
        battlePaginations.value.set(battleNum, pagination)
      }
    }
  }
}

const isBattleExpanded = (battleNum) => {
  return expandedBattles.value.has(battleNum)
}

const getBattlePagination = (battleNum) => {
  return battlePaginations.value.get(battleNum)
}

onMounted(() => {
  loadBattleData()
})
</script>

<template>
  <div class="report-page">
    <template v-if="battleData">
      <!-- 切磋结果标题 -->
      <div class="section">切磋结果：</div>
      
      <!-- 凝神香加成 -->
      <div class="section">凝神香加成:{{ battleData.incense_bonus || '无' }}</div>
      
      <!-- 对战双方 -->
      <div class="section">
        {{ battleData.attacker_name }} vs {{ battleData.defender_name }}
      </div>
      
      
      <!-- 幻兽经验 -->
      <div v-for="(beast, idx) in (battleData.attacker_beasts || [])" :key="idx" class="section">
        {{ beast.name }}-{{ beast.realm }}经验+{{ beast.exp_gain || 0 }}
      </div>
      
      <!-- 战斗结果 -->
      <div class="section result-line">
        【我】{{ resultText }}{{ resultSymbol }}
      </div>
      
      <!-- 活力消耗 -->
      <div class="section">活力-{{ battleData.energy_cost || 15 }}</div>
      
      <!-- 战斗过程 -->
      <template v-for="(battle, bIdx) in battleData.battles" :key="bIdx">
        <div class="section battle-log">
          <a class="link" @click="toggleBattle(battle.battle_num)">
            [第{{ battle.battle_num }}战]{{ battle.summary || battle.result }}
          </a>
        </div>
        
        <!-- 详细回合信息（展开时显示） -->
        <template v-if="isBattleExpanded(battle.battle_num)">
          <div class="section indent battle-detail">
            <div class="battle-result">{{ battle.result }}</div>
            
            <!-- 分页导航（顶部） -->
            <template v-if="getBattlePagination(battle.battle_num)">
              <div v-if="getBattlePagination(battle.battle_num).totalPages.value > 1" class="pagination">
                <a v-if="getBattlePagination(battle.battle_num).hasPrevPage.value" class="link" @click="getBattlePagination(battle.battle_num).prevPage()">上一页</a>
                <span v-else class="gray">上一页</span>
                <span class="page-info">第{{ getBattlePagination(battle.battle_num).currentPage.value }}/{{ getBattlePagination(battle.battle_num).totalPages.value }}页</span>
                <a v-if="getBattlePagination(battle.battle_num).hasNextPage.value" class="link" @click="getBattlePagination(battle.battle_num).nextPage()">下一页</a>
                <span v-else class="gray">下一页</span>
              </div>
              
              <!-- 当前页的回合 -->
              <template v-for="(round, rIdx) in getBattlePagination(battle.battle_num).currentRounds.value" :key="rIdx">
                <div class="round-info">
                  第{{ round.round }}回合: {{ round.action }}
                </div>
                <div class="hp-info">
                  攻方气血: {{ round.a_hp }} | 守方气血: {{ round.d_hp }}
                </div>
              </template>
              
              <!-- 分页导航（底部） -->
              <div v-if="getBattlePagination(battle.battle_num).totalPages.value > 1" class="pagination">
                <a v-if="getBattlePagination(battle.battle_num).hasPrevPage.value" class="link" @click="getBattlePagination(battle.battle_num).prevPage()">上一页</a>
                <span v-else class="gray">上一页</span>
                <span class="page-info">第{{ getBattlePagination(battle.battle_num).currentPage.value }}/{{ getBattlePagination(battle.battle_num).totalPages.value }}页</span>
                <a v-if="getBattlePagination(battle.battle_num).hasNextPage.value" class="link" @click="getBattlePagination(battle.battle_num).nextPage()">下一页</a>
                <span v-else class="gray">下一页</span>
              </div>
              
              <!-- 页码快速跳转 -->
              <div v-if="getBattlePagination(battle.battle_num).totalPages.value > 1" class="page-numbers">
                跳转到：
                <template v-for="page in getBattlePagination(battle.battle_num).totalPages.value" :key="page">
                  <a 
                    v-if="page !== getBattlePagination(battle.battle_num).currentPage.value" 
                    class="link page-num" 
                    @click="getBattlePagination(battle.battle_num).goToPage(page)"
                  >{{ page }}</a>
                  <span v-else class="current-page">{{ page }}</span>
                </template>
              </div>
            </template>
          </div>
        </template>
      </template>
      
      <!-- 切磋战绩 -->
      <div class="section">
        切磋战绩:{{ battleData.spar_wins || 0 }}/{{ battleData.spar_total || 0 }} 
        (胜率{{ battleData.spar_win_rate || '0.00' }}%)
      </div>
    </template>

    <div v-else class="section">暂无战报数据</div>

    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.report-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 4px 0;
}

.result-line {
  font-weight: bold;
}

.battle-log {
  color: #333;
}

.section.indent {
  margin-left: 20px;
}

.battle-detail {
  background: #ffffff;
  padding: 8px;
  margin: 4px 0;
  border-left: 2px solid #CCC;
}

.pagination {
  margin: 12px 0;
  padding: 8px 0;
  border-top: 1px solid #EEEEEE;
  border-bottom: 1px solid #EEEEEE;
}

.page-info {
  margin: 0 12px;
  color: #333333;
}

.page-numbers {
  margin: 8px 0;
}

.page-num {
  margin: 0 4px;
}

.current-page {
  margin: 0 4px;
  color: #CC3300;
  font-weight: bold;
}

.gray {
  color: #999999;
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

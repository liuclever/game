<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const battleData = ref(null)
const dungeonName = ref('')
const floor = ref(1)
const activeBattleIndex = ref(0)

onMounted(() => {
  const state = history.state
  if (state && state.battleData) {
    battleData.value = state.battleData
    dungeonName.value = state.dungeonName || ''
    floor.value = state.floor || 1
  } else {
    // 尝试从 sessionStorage 恢复
    const savedData = sessionStorage.getItem('currentDungeonBattle')
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        battleData.value = parsed.battleData
        dungeonName.value = parsed.dungeonName
        floor.value = parsed.floor
      } catch (e) {
        console.error('解析缓存战斗数据失败:', e)
      }
    }
  }
})

const battles = computed(() => {
  if (!battleData.value || !battleData.value.battles) return []
  return battleData.value.battles
})

const currentBattle = computed(() => {
  if (battles.value.length === 0) return null
  return battles.value[activeBattleIndex.value]
})

const selectBattle = (index) => {
  activeBattleIndex.value = index
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="detail-report-page">
    <template v-if="battleData && battles.length > 0">
      <div class="section title">
        【详细战报】<a class="link" @click="goBack">返回</a>
      </div>

      <div class="section">
        <span v-for="(battle, idx) in battles" :key="idx">
          <a 
            :class="['link', { 'active': idx === activeBattleIndex }]" 
            @click="selectBattle(idx)"
          >第{{ battle.battle_num }}战</a>
          <span v-if="idx < battles.length - 1">｜</span>
        </span>
      </div>

      <template v-if="currentBattle">
        <div v-if="currentBattle.hero_talent" class="section">
          [英雄天赋]：{{ currentBattle.hero_talent }}
        </div>

        <div v-for="(round, rIdx) in currentBattle.rounds" :key="rIdx" class="section">
          [回合{{ rIdx + 1 }}]：{{ round.action }}
        </div>

        <div class="section">
          [战斗结束]: {{ currentBattle.result }}
        </div>
      </template>
    </template>

    <template v-else>
      <div class="section gray">无战斗数据</div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.detail-report-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
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

.link.active {
  font-weight: bold;
}

.gray {
  color: #666666;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const battleData = ref(null)
const loot = ref(null)
const capturableBeast = ref(null)
const dungeonName = ref('')
const floor = ref(1)
const isOpeningLoot = ref(false)
const lootRewards = ref(null)

const handleOpenLoot = async (costType = 'energy') => {
  if (isOpeningLoot.value) return
  isOpeningLoot.value = true
  try {
    const res = await fetch('/api/dungeon/loot/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonName.value,
        cost_type: costType
      })
    })
    const data = await res.json()
    if (data.ok) {
      lootRewards.value = data.rewards
      // 更新本地 loot 状态，防止重复显示开启按钮
      if (loot.value) {
        loot.value.has_loot = false
      }
    } else {
      alert(data.error || '开启战利品失败')
    }
  } catch (e) {
    console.error('开启战利品失败:', e)
    alert('网络错误')
  } finally {
    isOpeningLoot.value = false
  }
}

onMounted(() => {
  const state = history.state
    if (state && state.battleData) {
      battleData.value = state.battleData
      loot.value = state.loot
      capturableBeast.value = state.capturableBeast
      dungeonName.value = state.dungeonName || ''
      floor.value = state.floor || 1
      
      // 存入 sessionStorage 以备详细战报页面使用或刷新恢复
      sessionStorage.setItem('currentDungeonBattle', JSON.stringify({
        battleData: state.battleData,
        loot: state.loot,
        capturableBeast: state.capturableBeast,
        dungeonName: dungeonName.value,
        floor: floor.value
      }))
    } else {
      // 尝试从 sessionStorage 恢复
      const savedData = sessionStorage.getItem('currentDungeonBattle')
      if (savedData) {
        try {
          const parsed = JSON.parse(savedData)
          battleData.value = parsed.battleData
          loot.value = parsed.loot
          capturableBeast.value = parsed.capturableBeast
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

const goBack = () => {
  try {
    console.log('[DungeonBattleResult] 导航回副本页')
    router.push(`/dungeon/challenge/${encodeURIComponent(dungeonName.value)}`).catch(err => {
      console.error('[DungeonBattleResult] 导航回副本页失败:', err)
      alert(`返回副本失败: ${err.message || '未知错误'}`)
    })
  } catch (e) {
    console.error('[DungeonBattleResult] goBack 异常:', e)
    alert(`返回副本异常: ${e.message || '未知错误'}`)
  }
}

const goHome = () => {
  try {
    console.log('[DungeonBattleResult] 导航到首页')
    router.push('/').catch(err => {
      console.error('[DungeonBattleResult] 导航到首页失败:', err)
      alert(`返回首页失败: ${err.message || '未知错误'}`)
    })
  } catch (e) {
    console.error('[DungeonBattleResult] goHome 异常:', e)
    alert(`返回首页异常: ${e.message || '未知错误'}`)
  }
}

const goMap = () => {
  try {
    console.log('[DungeonBattleResult] 导航到地图')
    router.push('/map').catch(err => {
      console.error('[DungeonBattleResult] 导航到地图失败:', err)
      alert(`返回地图失败: ${err.message || '未知错误'}`)
    })
  } catch (e) {
    console.error('[DungeonBattleResult] goMap 异常:', e)
    alert(`返回地图异常: ${e.message || '未知错误'}`)
  }
}

const handleMizong = () => {
  router.push({
    path: `/dungeon/${encodeURIComponent(dungeonName.value)}/mizong`,
    state: {
      fromBattleResult: true,
      battleFailed: !battleData.value?.is_victory,
      failedBeasts: battleData.value?.beasts || [],
      floor: floor.value
    }
  })
}

const handleAdvance = () => {
  router.push(`/dungeon/challenge/${encodeURIComponent(dungeonName.value)}`)
}

const handleRetryChallenge = async () => {
  if (!battleData.value || !battleData.value.beasts || battleData.value.beasts.length === 0) {
    return
  }
  
  try {
    const res = await fetch('/api/dungeon/challenge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonName.value,
        floor: floor.value,
        beasts: battleData.value.beasts
      })
    })
    const data = await res.json()
    if (data.ok) {
      battleData.value = data.battle_data
      loot.value = data.loot
      capturableBeast.value = data.capturable_beast
      
      sessionStorage.setItem('currentDungeonBattle', JSON.stringify({
        battleData: data.battle_data,
        dungeonName: dungeonName.value,
        floor: floor.value
      }))
    } else {
      alert(data.error || '挑战失败')
    }
  } catch (e) {
    console.error('挑战失败:', e)
    alert('网络错误')
  }
}

const handleCapture = () => {
  if (!battleData.value?.is_victory) return
  const firstBeast = battleData.value?.beasts?.[0]
  router.push({
    path: `/dungeon/${encodeURIComponent(dungeonName.value)}/capture`,
    state: {
      dungeonName: dungeonName.value,
      floor: floor.value,
      beastName: capturableBeast.value || firstBeast?.name || '',
      beastLevel: firstBeast?.level || 1
    }
  })
}

const goDetailReport = () => {
  router.push({
    path: `/dungeon/${encodeURIComponent(dungeonName.value)}/detail-report`,
    state: {
      battleData: battleData.value,
      dungeonName: dungeonName.value,
      floor: floor.value
    }
  })
}
</script>

<template>
  <div class="battle-result-page">
    <template v-if="battleData">
      <div class="section">
        挑战评价: {{ battleData.rating }}
      </div>

      <div class="section">
        {{ battleData.player_name }}｜{{ battleData.player_beast }} vs {{ battleData.dungeon_name }}
      </div>

      <div class="section">
        【{{ battleData.is_victory ? '我' : '敌' }}】{{ battleData.victory_text }}
      </div>

      <div class="section">
        <a class="link" @click="goDetailReport">详细战报</a>
      </div>

     

        <div class="section" v-if="capturableBeast && battleData.is_victory">
          {{ capturableBeast }} <a class="link" @click="handleCapture">捕捉</a>
        </div>

        <!-- 战利品掉落 -->
        <template v-if="loot && loot.has_loot">
          <div class="section spacer"></div>
          <div class="section gold">
            获得了战利品！
          </div>
          <div class="section">
            操作: <a class="link" @click="handleOpenLoot('energy')">开启战利品</a>(15活力) | <a class="link" @click="handleOpenLoot('double_card')">双倍开启</a>(1双倍卡)
          </div>
        </template>

          <!-- 战利品结果 -->
          <template v-if="lootRewards">
            <div class="section spacer"></div>
            <div class="section gold">
              开启成功！获得了以下奖励：
            </div>
            <div v-if="lootRewards.crystal" class="section">
              物品: {{ lootRewards.crystal.name }} x{{ lootRewards.crystal.amount }}
            </div>
            <div v-if="lootRewards.copper" class="section">
              物品: 铜钱 x{{ lootRewards.copper.amount }}
            </div>
            <div v-if="lootRewards.bone_soul" class="section">
              物品: {{ lootRewards.bone_soul.name }} x{{ lootRewards.bone_soul.amount }}
            </div>
            <div v-if="lootRewards.beast_exp && lootRewards.beast_exp.length > 0" class="section">
              幻兽经验奖励:
              <div v-for="br in lootRewards.beast_exp" :key="br.id" class="beast-exp-item">
                - {{ br.name }}: 
                <span v-if="br.capped" class="gray">等级已达上限(+5级), 无法获得经验</span>
                <span v-else>+{{ br.exp_gained }}经验 {{ br.new_level > br.old_level ? '(升级至' + br.new_level + '级)' : '' }}</span>
              </div>
            </div>
          </template>


          <div class="section" v-if="battleData.is_victory">
            地图: <a class="link" @click="handleAdvance">前进</a> | <a class="link" @click="handleMizong">迷踪</a> (放弃操作)
          </div>

        <div class="section" v-else>
          操作: <a class="link" @click="handleRetryChallenge">继续挑战</a> | <a class="link" @click="handleMizong">迷踪</a> (放弃操作)
        </div>

      <div class="section">
        本层| {{ battleData.is_victory ? '' : 'boss' }}|
      </div>
    </template>

    <template v-else>
      <div class="section gray">无战斗数据</div>
    </template>

    <div class="section spacer">
      <a class="link" @click="goBack">返回副本</a>
    </div>

    <div class="section">
      <a class="link" @click="goMap">返回地图首页</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.battle-result-page {
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

.blue {
  color: #0066CC;
}

.gray {
  color: #666666;
}

.gold {
  color: #8B4513;
  font-weight: bold;
}

.beast-exp-item {
  margin-left: 10px;
  font-size: 18px;
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

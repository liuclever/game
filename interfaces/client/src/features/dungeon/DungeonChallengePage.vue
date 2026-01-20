<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const dungeonInfo = ref({
  name: route.params.name || '镇妖塔',
  current_floor: 1,
  total_floors: 35,
  dice: 0,
  current_event: '',
  intro: '',
  energy: '',
  map_path: '前进|迷踪|放弃操作',
  floor_status: ['怪', '怪', '精', '怪', 'boss'],
  resets_today: 0,
  reset_limit: 5
})

const handleReset = async () => {
  try {
    isLoading.value = true
    const res = await fetch('/api/dungeon/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dungeon_name: dungeonInfo.value.name })
    })
    const data = await res.json()
    if (data.ok) {
      alert(data.message)
      await fetchDungeonProgress()
    } else {
      alert(data.error || '重置失败')
    }
  } catch (e) {
    console.error('重置失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}


const showAdvanceModal = ref(false)
const isRolling = ref(false)
const currentDiceValue = ref(1)
const finalDiceValue = ref(null)
const countdown = ref(3)
const advanceResult = ref(null)
const isLoading = ref(false)
const floorBeasts = ref(null)
const isLoadingBeasts = ref(false)
const pendingChallenge = ref(null)
const pendingLoot = ref(null) // 战利品
const pendingChest = ref(null)  // 宝箱事件
const pendingEvent = ref(null)  // 随机事件 (攀登, 活力之泉, 猜拳)
const showBeastInfo = ref(false)
const selectedBeast = ref(null)
const lootRewards = ref(null)
const isOpeningLoot = ref(false)

const handleOpenLoot = async (costType = 'energy') => {
  if (isOpeningLoot.value) return
  isOpeningLoot.value = true
  try {
    const res = await fetch('/api/dungeon/loot/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonInfo.value.name,
        cost_type: costType
      })
    })
    const data = await res.json()
    if (data.ok) {
      lootRewards.value = data.rewards
      pendingLoot.value = null
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
let rollInterval = null
let countdownInterval = null

const fetchDungeonProgress = async () => {
  try {
    const dungeonName = dungeonInfo.value.name
    const res = await fetch(`/api/dungeon/progress?dungeon_name=${encodeURIComponent(dungeonName)}`)

    if (!res.ok) {
      const text = await res.text()
      console.error('进度接口HTTP错误:', res.status, text)
      return
    }

    const data = await res.json()
    if (data.ok) {
      dungeonInfo.value.current_floor = data.current_floor
      dungeonInfo.value.total_floors = data.total_floors
      dungeonInfo.value.dice = data.dice || 0
      dungeonInfo.value.energy = data.energy || ''
      dungeonInfo.value.resets_today = data.resets_today || 0
      dungeonInfo.value.reset_limit = data.reset_limit || 5
      
      const eventType = data.floor_event_type || 'beast'
      
      if (!data.floor_cleared) {
        // 宝箱事件
        if (eventType === 'giant_chest' || eventType === 'mystery_chest') {
          pendingChallenge.value = null
          pendingEvent.value = null
          pendingChest.value = {
            floor: data.current_floor,
            type: eventType,
            name: eventType === 'giant_chest' ? '巨型宝箱' : '神秘宝箱'
          }
          dungeonInfo.value.current_event = eventType === 'giant_chest' ? '巨型宝箱' : '神秘宝箱'
          dungeonInfo.value.intro = '发现了宝箱，开启它获取奖励'
        } else if (['climb', 'vitality_spring', 'rps'].includes(eventType)) {
          // 随机事件
          pendingChallenge.value = null
          pendingChest.value = null
          await fetchFloorBeasts(data.current_floor)
          pendingEvent.value = {
            floor: data.current_floor,
            type: eventType,
            description: floorBeasts.value?.description || '随机事件'
          }
          dungeonInfo.value.current_event = '随机事件'
          dungeonInfo.value.intro = floorBeasts.value?.description || '随机事件'
        } else {
          // 幻兽事件
          pendingChest.value = null
          pendingEvent.value = null
          await fetchFloorBeasts(data.current_floor)
          if (floorBeasts.value?.beasts?.length > 0) {
            pendingChallenge.value = { floor: data.current_floor, beasts: floorBeasts.value.beasts }
          }
          dungeonInfo.value.current_event = eventType === 'boss' ? 'BOSS层' : (floorBeasts.value?.floor_type === 'elite' ? '精英幻兽' : '野生幻兽')
          dungeonInfo.value.intro = floorBeasts.value?.description || '挑战幻兽'
        }
      } else {
        pendingChallenge.value = null
        pendingChest.value = null
        pendingEvent.value = null
        
        dungeonInfo.value.current_event = '本层已通关'
        dungeonInfo.value.intro = '点击前进继续探索'
        
        // 如果已通关但未领取战利品
        if (!data.loot_claimed) {
          pendingLoot.value = {
            floor: data.current_floor
          }
          dungeonInfo.value.current_event = '发现战利品'
          dungeonInfo.value.intro = '请先领取战利品'
        } else {
          pendingLoot.value = null
        }
      }

    } else {
      console.error('进度接口业务失败:', data)
    }
  } catch (e) {
    console.error('获取副本进度失败:', e)
  }
}


const fetchFloorBeasts = async (floor) => {
  try {
    isLoadingBeasts.value = true
    const res = await fetch(`/api/dungeon/floor/beasts?dungeon_name=${encodeURIComponent(dungeonInfo.value.name)}&floor=${floor}`)
    const data = await res.json()
    if (data.ok) {
      floorBeasts.value = data
    } else {
      floorBeasts.value = null
    }
  } catch (e) {
    console.error('获取幻兽失败:', e)
    floorBeasts.value = null
  } finally {
    isLoadingBeasts.value = false
  }
}

let advancePromise = null

const advanceDungeon = async (diceValue = null) => {
  advancePromise = (async () => {
    try {
      isLoading.value = true
      const body = {
        dungeon_name: dungeonInfo.value.name
      }
      if (diceValue !== null) {
        body.dice_value = diceValue
      }
      
      const res = await fetch('/api/dungeon/advance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      const data = await res.json()
      if (data.ok) {
        advanceResult.value = {
          oldFloor: data.old_floor,
          newFloor: data.new_floor,
          diceValue: data.dice_value,
          isReset: data.is_reset
        }
        dungeonInfo.value.current_floor = data.new_floor
        if (typeof data.dice === 'number') {
          dungeonInfo.value.dice = data.dice
        }
        // 如果已经定格且正在等待结果，则立即显示最终点数
        if (!isRolling.value && finalDiceValue.value === -1) {
          finalDiceValue.value = data.dice_value
        }
        await fetchFloorBeasts(data.new_floor)
        if (typeof data.dice !== 'number') {
          await fetchDungeonProgress()
        }
      } else {
        advanceResult.value = { error: data.error }
      }
    } catch (e) {
      console.error('前进失败:', e)
      advanceResult.value = { error: '网络错误' }
    } finally {
      isLoading.value = false
    }
  })()
  return advancePromise
}

const goBack = () => {
  try {
    console.log('[DungeonChallenge] 导航到首页')
    router.push('/').catch(err => {
      console.error('[DungeonChallenge] 导航到首页失败:', err)
      alert(`返回首页失败: ${err.message || '未知错误'}`)
    })
  } catch (e) {
    console.error('[DungeonChallenge] goBack 异常:', e)
    alert(`返回首页异常: ${e.message || '未知错误'}`)
  }
}

const goMap = () => {
  try {
    console.log('[DungeonChallenge] 导航到地图')
    router.push('/map').catch(err => {
      console.error('[DungeonChallenge] 导航到地图失败:', err)
      alert(`返回地图失败: ${err.message || '未知错误'}`)
    })
  } catch (e) {
    console.error('[DungeonChallenge] goMap 异常:', e)
    alert(`返回地图异常: ${e.message || '未知错误'}`)
  }
}

const openAdvanceModal = () => {
  showAdvanceModal.value = true
  isRolling.value = true
  finalDiceValue.value = null
  advanceResult.value = null
  floorBeasts.value = null
  countdown.value = 3
  startRolling()
  startCountdown()
  // 立即开始异步计算，这样用户点击停止时可能已经计算好了
  advanceDungeon()
}

const startRolling = () => {
  rollInterval = setInterval(() => {
    currentDiceValue.value = Math.floor(Math.random() * 6) + 1
  }, 100)
}

const startCountdown = () => {
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      stopRolling()
    }
  }, 1000)
}

const stopRolling = async () => {
  if (finalDiceValue.value !== null) return
  
  isRolling.value = false
  if (rollInterval) {
    clearInterval(rollInterval)
    rollInterval = null
  }
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
  
  if (advanceResult.value && advanceResult.value.diceValue) {
    finalDiceValue.value = advanceResult.value.diceValue
  } else {
    // 标记为已定格但仍在等待后端结果
    finalDiceValue.value = -1
  }
}

const closeAdvanceModal = async () => {
  showAdvanceModal.value = false
  isRolling.value = false
  
  if (rollInterval) {
    clearInterval(rollInterval)
    rollInterval = null
  }
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }

  // 确保等待前进请求完成，防止由于请求延迟导致的层数不刷新
  if (advancePromise) {
    await advancePromise
  }
  
  await fetchDungeonProgress()
  
  // 重置状态
  finalDiceValue.value = null
  advanceResult.value = null
  floorBeasts.value = null
}

const formatBeastDisplay = () => {
  if (!floorBeasts.value || !floorBeasts.value.beasts || floorBeasts.value.beasts.length === 0) {
    return ''
  }
  return floorBeasts.value.beasts.map(b => `${b.name}(${b.level}级)`).join(' | ')
}

const handleMizong = () => {
  router.push(`/dungeon/${encodeURIComponent(dungeonInfo.value.name)}/mizong`)
}

const handlePendingChallenge = async () => {
  if (!pendingChallenge.value) return
  
  try {
    const res = await fetch('/api/dungeon/challenge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonInfo.value.name,
        floor: pendingChallenge.value.floor,
        beasts: pendingChallenge.value.beasts
      })
    })
    const data = await res.json()
    if (data.ok) {
      console.log('[DungeonChallenge] 挑战成功，导航到战斗结果页')
      router.push({
        path: `/dungeon/${encodeURIComponent(dungeonInfo.value.name)}/battle-result`,
        state: {
          battleData: data.battle_data,
          loot: data.loot,
          capturableBeast: data.capturable_beast,
          dungeonName: dungeonInfo.value.name,
          floor: pendingChallenge.value.floor
        }
      }).catch(err => {
        console.error('[DungeonChallenge] 导航到战斗结果页失败:', err)
        alert(`跳转失败: ${err.message || '未知错误'}`)
      })
    } else {
      alert(data.error || '挑战失败')
    }
  } catch (e) {
    console.error('挑战失败:', e)
    alert('网络错误')
  }
}

const handleOpenChest = async (costType = 'energy') => {
  if (!pendingChest.value) return
  
  try {
    const res = await fetch('/api/dungeon/chest/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonInfo.value.name,
        chest_type: pendingChest.value.type,
        cost_type: costType
      })
    })
    const data = await res.json()
    if (data.ok) {
      const rewardText = data.rewards.map(r => `${r.name} x${r.amount}`).join(', ')
      const doubleText = data.is_double ? '（双倍奖励）' : ''
      alert(`开启${pendingChest.value.name}成功！${doubleText}\n获得: ${rewardText}`)
      pendingChest.value = null
      await fetchDungeonProgress()
    } else {
      alert(data.error || '开启失败')
    }
  } catch (e) {
    console.error('开启宝箱失败:', e)
    alert('网络错误')
  }
}

const handleOpenChestInModal = async (costType = 'energy') => {
  if (!floorBeasts.value) return
  
  const chestType = floorBeasts.value.floor_event_type
  const chestName = chestType === 'giant_chest' ? '巨型宝箱' : '神秘宝箱'
  
  try {
    const res = await fetch('/api/dungeon/chest/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonInfo.value.name,
        chest_type: chestType,
        cost_type: costType
      })
    })
    const data = await res.json()
    if (data.ok) {
      const rewardText = data.rewards.map(r => `${r.name} x${r.amount}`).join(', ')
      const doubleText = data.is_double ? '（双倍奖励）' : ''
      alert(`开启${chestName}成功！${doubleText}\n获得: ${rewardText}`)
      closeAdvanceModal()
    } else {
      alert(data.error || '开启失败')
    }
  } catch (e) {
    console.error('开启宝箱失败:', e)
    alert('网络错误')
  }
}

const handleChallenge = async () => {
  if (!floorBeasts.value || !floorBeasts.value.beasts || floorBeasts.value.beasts.length === 0) {
    return
  }
  
  try {
    const res = await fetch('/api/dungeon/challenge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dungeon_name: dungeonInfo.value.name,
        floor: advanceResult.value?.newFloor || dungeonInfo.value.current_floor,
        beasts: floorBeasts.value.beasts
      })
    })
    const data = await res.json()
    if (data.ok) {
      console.log('[DungeonChallenge] 挑战成功，导航到战斗结果页')
      router.push({
        path: `/dungeon/${encodeURIComponent(dungeonInfo.value.name)}/battle-result`,
        state: {
          battleData: data.battle_data,
          loot: data.loot,
          capturableBeast: data.capturable_beast,
          dungeonName: dungeonInfo.value.name,
          floor: advanceResult.value?.newFloor || dungeonInfo.value.current_floor
        }
      }).catch(err => {
        console.error('[DungeonChallenge] 导航到战斗结果页失败:', err)
        alert(`跳转失败: ${err.message || '未知错误'}`)
      })
    } else {
      alert(data.error || '挑战失败')
    }
  } catch (e) {
    console.error('挑战失败:', e)
    alert('网络错误')
  }
}

const handleClimb = async () => {
  if (!pendingEvent.value || isLoading.value) return
  isLoading.value = true
  try {
    const res = await fetch('/api/dungeon/event/climb', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dungeon_name: dungeonInfo.value.name })
    })
    const data = await res.json()
    if (data.ok) {
      alert(data.message)
      if (data.success) {
        pendingEvent.value = null
        await fetchDungeonProgress()
      } else {
        dungeonInfo.value.dice = data.dice
      }
    } else {
      alert(data.error || '操作失败')
    }
  } catch (e) {
    console.error('攀登失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}

const handleVitalitySpring = async () => {
  if (!pendingEvent.value || isLoading.value) return
  isLoading.value = true
  try {
    const res = await fetch('/api/dungeon/event/vitality-spring', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dungeon_name: dungeonInfo.value.name })
    })
    const data = await res.json()
    if (data.ok) {
      alert(data.message)
      if (data.success) {
        pendingEvent.value = null
        await fetchDungeonProgress()
      } else {
        dungeonInfo.value.dice = data.dice
      }
    } else {
      alert(data.error || '操作失败')
    }
  } catch (e) {
    console.error('浸泡失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}

const handleRPS = async (choice) => {
  if (!pendingEvent.value || isLoading.value) return
  isLoading.value = true
  try {
    const res = await fetch('/api/dungeon/event/rps', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        dungeon_name: dungeonInfo.value.name,
        choice: choice 
      })
    })
    const data = await res.json()
    if (data.ok) {
      alert(`你出了 ${data.player_choice}，对方出了 ${data.bot_choice}\n结果: ${data.message}\n${data.result === 'win' ? '前进' : (data.result === 'lose' ? '后退' : '原地不动')} ${data.change} 层`)
      pendingEvent.value = null
      await fetchDungeonProgress()
    } else {
      alert(data.error || '操作失败')
    }
  } catch (e) {
    console.error('猜拳失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}

const viewBeastDetails = (beast) => {
  selectedBeast.value = beast
  showBeastInfo.value = true
}

const closeBeastInfo = () => {
  showBeastInfo.value = false
  selectedBeast.value = null
}

const handleEventInModal = async (type, choice = null) => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    let url = '/api/dungeon/event/' + (type === 'vitality_spring' ? 'vitality-spring' : type)
    let body = { dungeon_name: dungeonInfo.value.name }
    if (choice) body.choice = choice

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const data = await res.json()
    if (data.ok) {
      if (type === 'rps') {
        alert(`你出了 ${data.player_choice}，对方出了 ${data.bot_choice}\n结果: ${data.message}\n${data.result === 'win' ? '前进' : (data.result === 'lose' ? '后退' : '原地不动')} ${data.change} 层`)
      } else {
        alert(data.message)
      }
      
      if (data.success || type === 'rps') {
        closeAdvanceModal()
      } else {
        dungeonInfo.value.dice = data.dice
      }
    } else {
      alert(data.error || '操作失败')
    }
  } catch (e) {
    console.error('事件处理失败:', e)
    alert('网络错误')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDungeonProgress()
})

watch(
  () => route.path,
  () => {
    fetchDungeonProgress()
  }
)

onUnmounted(() => {
  if (rollInterval) clearInterval(rollInterval)
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>

<template>
  <div class="dungeon-page">
    <div class="section title">
      【副本】{{ dungeonInfo.name }} ({{ dungeonInfo.current_floor }}/{{ dungeonInfo.total_floors }}层) 
      <a class="link-reset" @click="handleReset">重置</a>
    </div>

    <div class="section">
      骰子:{{ dungeonInfo.dice }} <a class="link" @click="router.push({ path: '/dungeon/dice-supplement', query: { from: dungeonInfo.name } })">补充</a>
    </div>

    <div v-if="dungeonInfo.energy" class="section">
      活力:{{ dungeonInfo.energy }}
    </div>

    <div class="section">
      今日重置:{{ dungeonInfo.resets_today }}/{{ dungeonInfo.reset_limit }}次 <span class="gray">(每次200元宝)</span>
    </div>

    <div class="section">
      本层:{{ dungeonInfo.current_event }}
    </div>

    <div class="section">
      简介:{{ dungeonInfo.intro }}
    </div>

      <div class="section">
        地图: <a class="link" @click="openAdvanceModal">前进</a> | <a class="link" @click="handleMizong">迷踪</a> | <span class="gray">放弃操作</span>
      </div>

      <!-- 战利品掉落 -->
      <template v-if="pendingLoot">
        <div class="section spacer"></div>
        <div class="section gold">
          本层(第{{ pendingLoot.floor }}层)发现了战利品！
        </div>
        <div class="section">
          操作: <a class="link" @click="handleOpenLoot('energy')">开启战利品</a>(15活力) | <a class="link" @click="handleOpenLoot('double_card')">双倍开启</a>(1双倍卡) | <a class="link" @click="openAdvanceModal">继续前进</a>
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


      <!-- 如果当前层未通关，显示继续挑战 -->

      <template v-if="pendingChallenge">
        <div class="section spacer"></div>
        <div class="section pending-challenge">
          本层(第{{ pendingChallenge.floor }}层)幻兽尚未击败
        </div>
        <div class="section">
          本层幻兽: <span v-for="(beast, idx) in pendingChallenge.beasts" :key="idx"><a class="link" @click="viewBeastDetails(beast)">{{ beast.name }}</a>({{ beast.level }}级)<span v-if="idx < pendingChallenge.beasts.length - 1"> | </span></span>
        </div>
        <div class="section">
          操作: <a class="link" @click="handlePendingChallenge">挑战幻兽</a>(免活力)
        </div>
      </template>

        <!-- 宝箱事件 -->
        <template v-if="pendingChest">
          <div class="section spacer"></div>
          <div class="section chest-event">
            本层(第{{ pendingChest.floor }}层)发现了{{ pendingChest.name }}！
          </div>
          <div class="section">
            操作: <a class="link" @click="handleOpenChest('energy')">开启宝箱</a>(15活力) | <a class="link" @click="handleOpenChest('double_card')">双倍开启</a>(1双倍卡) | <a class="link" @click="openAdvanceModal">继续前进</a>
          </div>
        </template>

        <!-- 随机事件 -->
        <template v-if="pendingEvent">
          <div class="section spacer"></div>
          <div class="section event-msg">
            本层(第{{ pendingEvent.floor }}层): 随机事件
          </div>
          <div class="section">
            简介: {{ pendingEvent.description }}
          </div>
          <div v-if="pendingEvent.type === 'climb'" class="section">
            操作: <a class="link" @click="handleClimb">攀登</a>(1骰子)
          </div>
          <div v-else-if="pendingEvent.type === 'vitality_spring'" class="section">
            操作: <a class="link" @click="handleVitalitySpring">浸泡</a>(1骰子)
          </div>
          <div v-else-if="pendingEvent.type === 'rps'" class="section">
            操作: <a class="link" @click="handleRPS('stone')">[石头]</a> | <a class="link" @click="handleRPS('scissors')">[剪刀]</a> | <a class="link" @click="handleRPS('paper')">[布]</a>
          </div>
        </template>


    <div class="section">
      本层| <span v-for="(item, index) in dungeonInfo.floor_status" :key="index">{{ item }}| </span>
    </div>

    <div class="section spacer"></div>

    <div class="section">
      入:副本入口|?? :随机事件
    </div>
    <div class="section">
      怪:野生幻兽|精:精英幻兽
    </div>
    <div class="section">
      箱:神秘箱子|宝:巨型宝藏
    </div>
    <div class="section">
      BOSS:打败它即可通关
    </div>

    <div class="section spacer"></div>

    <div class="section">
      <a class="link" @click="goMap">返回地图首页</a>
    </div>
    <div class="section">
      <a class="link" @click="goBack">返回游戏首页</a>
    </div>

    <div v-if="showAdvanceModal" class="advance-modal">
      <div class="modal-content">
        <div class="dice-container">
          <div class="dice">{{ finalDiceValue && finalDiceValue > 0 ? finalDiceValue : currentDiceValue }}</div>
        </div>
        
        <template v-if="!finalDiceValue">
          <div class="advance-text">前进中......</div>
          <div class="advance-hint">
            点击<a class="link-red" @click="stopRolling">停止</a>让骰子定格,上面的数字将是你前进的层数,{{ countdown }}秒后将自动定格
          </div>
        </template>
        
          <template v-else>
            <div v-if="isLoading || isLoadingBeasts" class="advance-text">正在计算...</div>
            <template v-else-if="advanceResult">
              <div v-if="advanceResult.error" class="advance-result error">
                {{ advanceResult.error }}
              </div>
              <div v-else>
                <div class="section title">
                  【副本】{{ dungeonInfo.name }} ({{ advanceResult.newFloor }}/{{ dungeonInfo.total_floors }}层)
                </div>

                <div class="section">
                  你扔出{{ advanceResult.diceValue }}点,来到了第{{ advanceResult.newFloor }}层
                </div>

                <div class="section">
                  骰子:{{ dungeonInfo.dice }} <a class="link" @click="router.push('/dungeon/dice-supplement')">补充</a>
                </div>

                  <!-- 宝箱事件 -->
                  <template v-if="floorBeasts && (floorBeasts.floor_event_type === 'giant_chest' || floorBeasts.floor_event_type === 'mystery_chest')">
                    <div class="section chest-event">
                      本层: {{ floorBeasts.floor_event_type === 'giant_chest' ? '巨型宝箱' : '神秘宝箱' }}
                    </div>
                    <div class="section">
                      简介:{{ floorBeasts.description }}
                    </div>
                    <div class="section">
                      操作: <a class="link" @click="handleOpenChestInModal('energy')">开启宝箱</a>(15活力) | <a class="link" @click="handleOpenChestInModal('double_card')">双倍开启</a>(1双倍卡) | <a class="link" @click="openAdvanceModal">继续前进</a>
                    </div>
                    <div class="section">
                      本层| {{ floorBeasts.floor_event_type === 'giant_chest' ? '宝' : '箱' }}|
                    </div>
                  </template>
                  <!-- 幻兽事件 -->
                    <template v-else-if="floorBeasts && floorBeasts.beasts && floorBeasts.beasts.length > 0">
                      <div class="section">
                        本层: <span v-for="(beast, idx) in floorBeasts.beasts" :key="idx"><a class="link" @click="viewBeastDetails(beast)">{{ beast.name }}</a>({{ beast.level }}级)<span v-if="idx < floorBeasts.beasts.length - 1"> | </span></span>
                      </div>
                    <div class="section">
                      简介:{{ floorBeasts.description }}
                    </div>
                    <div class="section">
                      操作: <a class="link" @click="handleChallenge">挑战幻兽</a>(免活力)
                    </div>
                    <div class="section">
                      本层| {{ floorBeasts.floor_type === 'boss' ? 'boss' : (floorBeasts.floor_type === 'elite' ? '精' : '怪') }}|
                    </div>
                  </template>

                  <!-- 随机事件 (Modal) -->
                  <template v-else-if="floorBeasts && ['climb', 'vitality_spring', 'rps'].includes(floorBeasts.floor_event_type)">
                    <div class="section">
                      本层: 随机事件
                    </div>
                    <div class="section">
                      简介:{{ floorBeasts.description }}
                    </div>
                    <div v-if="floorBeasts.floor_event_type === 'climb'" class="section">
                      操作: <a class="link" @click="handleEventInModal('climb')">攀登</a>(1骰子)
                    </div>
                    <div v-else-if="floorBeasts.floor_event_type === 'vitality_spring'" class="section">
                      操作: <a class="link" @click="handleEventInModal('vitality_spring')">浸泡</a>(1骰子)
                    </div>
                    <div v-else-if="floorBeasts.floor_event_type === 'rps'" class="section">
                      操作: <a class="link" @click="handleEventInModal('rps', 'stone')">[石头]</a> | <a class="link" @click="handleEventInModal('rps', 'scissors')">[剪刀]</a> | <a class="link" @click="handleEventInModal('rps', 'paper')">[布]</a>
                    </div>
                    <div class="section">
                      本层| ?|
                    </div>
                  </template>

                  <template v-else>
                    <div class="section">
                      本层: 随机事件
                    </div>
                  </template>


                <div class="section spacer"></div>

                <div class="section">
                  入:副本入口|?? :随机事件
                </div>
                <div class="section">
                  怪:野生幻兽|精:精英幻兽
                </div>
                <div class="section">
                  箱:神秘箱子|宝:巨型宝藏
                </div>
                <div class="section">
                  BOSS:打败它即可通关
                </div>
              </div>
            </template>
          </template>

          <div class="section spacer"></div>
          
          <div class="modal-links">
            <a class="link" @click="closeAdvanceModal">返回副本</a>
          </div>
          <div class="modal-links">
            <a class="link" @click="goBack">返回游戏首页</a>
          </div>
        
      </div>
    </div>

    </div>

    <!-- 幻兽属性查看弹窗 -->
    <div v-if="showBeastInfo && selectedBeast" class="beast-info-modal" @click.self="closeBeastInfo">
      <div class="modal-content">
        <div class="section title">【幻兽属性】</div>
        <div class="section">名称: {{ selectedBeast.name }}</div>
        <div class="section">等级: {{ selectedBeast.level }}级</div>
        <div class="section">攻击类型: {{ selectedBeast.attack_type === 'physical' ? '物攻型' : '法攻型' }}</div>
        
        <div class="section spacer"></div>
        <div class="section">基础属性:</div>
        <div class="section">
          气血: {{ selectedBeast.stats?.hp || 0 }} | 
          {{ selectedBeast.attack_type === 'physical' ? '物攻' : '法攻' }}: {{ selectedBeast.stats?.atk || 0 }}
        </div>
        <div class="section">
          物防: {{ selectedBeast.stats?.def || 0 }} | 
          法防: {{ selectedBeast.stats?.mdef || 0 }}
        </div>
        <div class="section">
          速度: {{ selectedBeast.stats?.speed || 0 }}
        </div>

        <div v-if="selectedBeast.skills && selectedBeast.skills.length > 0" class="section spacer">
          技能: {{ selectedBeast.skills.join(' | ') }}
        </div>

        <div class="section spacer"></div>
        <div class="modal-links">
          <a class="link" @click="closeBeastInfo">关闭</a>
        </div>
      </div>
    </div>
  </template>

<style scoped>
.dungeon-page {
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
  font-weight: bold;
}

.spacer {
  height: 12px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link-reset {
  color: #CC0000;
  cursor: pointer;
  text-decoration: none;
  font-size: 18px;
  margin-left: 10px;
  border: 1px solid #CC0000;
  padding: 0 4px;
  border-radius: 3px;
}

.link-reset:hover {
  background: #CC0000;
  color: #fff;
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

.advance-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
  z-index: 100;
  padding: 8px 12px;
}

.modal-content {
  font-size: 16px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.dice-container {
  margin: 10px 0;
}

.dice {
  width: 40px;
  height: 40px;
  background: #fff;
  border: 2px solid #333;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.advance-text {
  color: #0066CC;
  margin: 10px 0;
}

.advance-hint {
  margin: 10px 0;
}

.link-red {
  color: #CC0000;
  cursor: pointer;
  text-decoration: none;
}

.link-red:hover {
  text-decoration: underline;
}

.modal-links {
  margin: 5px 0;
}

.modal-content .footer {
  margin-top: 30px;
}

.advance-result {
  margin: 10px 0;
  padding: 8px;
  background: #FFFFFF;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.advance-result.error {
  color: #CC0000;
  background: #ffe0e0;
  border-color: #ffaaaa;
}

.result-text {
  color: #333;
}

.result-text.success {
  color: #008800;
  font-weight: bold;
}

.pending-challenge {
  color: #d32f2f;
  font-weight: bold;
}

.chest-event {
  color: #ff9800;
  font-weight: bold;
}

.beast-info-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.beast-info-modal .modal-content {
  background: #ffffff;
  width: 80%;
  max-width: 300px;
  padding: 15px;
  border: 2px solid #8B4513;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.gold {
  color: #8B4513;
  font-weight: bold;
}

.beast-exp-item {
  margin-left: 10px;
  font-size: 18px;
}
</style>

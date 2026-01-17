<!-- 
  盟战测试按钮组件
  用于测试功能，点击后可以直接开战，不用等下一次开战时间
  
  删除方法：删除此文件，并从 AllianceWarPage.vue 中移除相关引用
-->
<script setup>
import { ref } from 'vue'
import http from '@/services/http'

const testing = ref(false)
const testResult = ref(null)

// 所有土地ID（根据实际情况调整）
const landIds = [1, 2, 3, 4]

const runTestBattle = async (landId) => {
  if (testing.value) return
  
  if (!confirm(`确定要对土地 ${landId} 执行测试开战吗？\n这将跳过时间检查，直接执行对战流程。`)) {
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    const res = await http.post(`/alliance/war/run-battle/${landId}`, { test_mode: true })
    if (res.data?.ok) {
      const battleCount = res.data.all_battle_results?.length || 0
      const rounds = res.data.rounds || 1
      const occupation = res.data.occupation
      
      let message = res.data.message || `土地 ${landId} 开战成功`
      if (occupation?.status === 'occupied') {
        message += `\n\n✅ 联盟 ${occupation.alliance_id} 占领了土地 ${landId}`
      }
      message += `\n\n执行了 ${rounds} 轮配对`
      message += `\n总对战数: ${battleCount}`
      
      testResult.value = {
        success: true,
        message: message,
        details: res.data
      }
      console.error(message)
    } else {
      const errorMsg = res.data?.error || '开战失败'
      testResult.value = {
        success: false,
        message: errorMsg
      }
      console.error(`❌ ${errorMsg}\n\n提示：请确保：\n1. 至少2个联盟已报名\n2. 每个联盟有成员已签到\n3. 成员有出战幻兽`)
    }
  } catch (err) {
    const errorMsg = err.response?.data?.error || err.message || '网络错误'
    testResult.value = {
      success: false,
      message: errorMsg
    }
    console.error(`❌ ${errorMsg}\n\n提示：请确保：\n1. 至少2个联盟已报名\n2. 每个联盟有成员已签到\n3. 成员有出战幻兽`)
  } finally {
    testing.value = false
  }
}

const runAllBattles = async () => {
  if (testing.value) return
  
  if (!confirm(`确定要对所有土地（${landIds.join(', ')}）执行测试开战吗？\n这将跳过时间检查，依次执行所有土地的对战流程。`)) {
    return
  }
  
  testing.value = true
  testResult.value = null
  
  const results = []
  for (const landId of landIds) {
    try {
      const res = await http.post(`/alliance/war/run-battle/${landId}`, { test_mode: true })
      if (res.data?.ok) {
        const battleCount = res.data.all_battle_results?.length || 0
        const occupation = res.data.occupation
        let message = res.data.message || `土地 ${landId} 开战成功`
        if (occupation?.status === 'occupied') {
          message += `，联盟 ${occupation.alliance_id} 占领`
        }
        results.push({
          landId,
          success: true,
          message: message,
          battles: battleCount
        })
      } else {
        results.push({
          landId,
          success: false,
          message: res.data?.error || '开战失败'
        })
      }
    } catch (err) {
      results.push({
        landId,
        success: false,
        message: err.response?.data?.error || err.message || '网络错误'
      })
    }
  }
  
  testing.value = false
  
  const successCount = results.filter(r => r.success).length
  const totalBattles = results.reduce((sum, r) => sum + (r.battles || 0), 0)
  
  console.error(`测试完成！\n\n成功: ${successCount}/${landIds.length}\n总对战数: ${totalBattles}\n\n详情请查看控制台`)
  console.log('测试开战结果:', results)
  testResult.value = { results }
}
</script>

<template>
  <div class="test-button-container">
    <div class="test-section">
      <div class="test-title">【测试功能】</div>
      <div class="test-buttons">
        <button 
          v-for="landId in landIds" 
          :key="landId"
          class="test-btn"
          :disabled="testing"
          @click="runTestBattle(landId)"
        >
          {{ testing ? '执行中...' : `测试开战-土地${landId}` }}
        </button>
        <button 
          class="test-btn test-btn-all"
          :disabled="testing"
          @click="runAllBattles"
        >
          {{ testing ? '执行中...' : '测试开战-全部土地' }}
        </button>
      </div>
      <div v-if="testResult" class="test-result" :class="{ success: testResult.success }">
        {{ testResult.message }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.test-button-container {
  margin: 12px 0;
  padding: 12px;
  background: #fff3cd;
  border: 2px dashed #ffc107;
  border-radius: 4px;
}

.test-section {
  font-size: 14px;
}

.test-title {
  font-weight: bold;
  color: #856404;
  margin-bottom: 8px;
}

.test-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.test-btn {
  padding: 6px 12px;
  border: 1px solid #ffc107;
  background: #fff;
  color: #856404;
  cursor: pointer;
  border-radius: 3px;
  font-size: 13px;
  font-family: SimSun, '宋体', serif;
}

.test-btn:hover:not(:disabled) {
  background: #ffeaa7;
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-btn-all {
  background: #ffc107;
  color: #000;
  font-weight: bold;
}

.test-btn-all:hover:not(:disabled) {
  background: #ffb300;
}

.test-result {
  font-size: 12px;
  color: #856404;
  margin-top: 4px;
}

.test-result.success {
  color: #155724;
}
</style>

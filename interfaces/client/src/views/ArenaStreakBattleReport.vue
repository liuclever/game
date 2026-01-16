<template>
  <div class="report-page">
    <template v-if="battleData">
      <!-- 连胜竞技场结果标题 -->
      <div class="section">连胜竞技场结果：</div>
      
      <!-- 凝神香加成 -->
      <div class="section">凝神香加成:{{ battleData.incense_bonus || '无' }}</div>
      
      <!-- 对战双方 -->
      <div class="section">
        {{ battleData.attacker_name }} vs {{ battleData.defender_name }}
      </div>
      
      <!-- 战斗结果 -->
      <div class="section result-line">
        【我】{{ resultText }}{{ resultSymbol }}
      </div>
      
      <!-- 当前连胜 -->
      <div class="section">
        当前连胜: {{ battleData.current_streak || 0 }}次
      </div>
      
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
    </template>

    <div v-else class="section">加载中...</div>

    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="router.push('/arena/streak')">返回连胜竞技场</a>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>
  </div>
</template>

<script>
import { useRouter, useRoute } from 'vue-router';
import { ref, onMounted, computed } from 'vue';

export default {
  name: 'ArenaStreakBattleReport',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const battleData = ref(null);
    const expandedBattles = ref(new Set());

    // 动态导入幻兽图片
    const beastImageModules = import.meta.glob('@/assets/images/image*.jpeg', { eager: true })
    const getBeastImage = (templateId) => {
      if (!templateId) return ''
      const key = `/src/assets/images/image${templateId}.jpeg`
      const module = beastImageModules[key]
      return module?.default || ''
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
      const match = result.match(/\([⚬×]+:[⚬×]+\)/)
      return match ? match[0] : ''
    })

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
      // 从 sessionStorage 读取战报数据
      const storedData = sessionStorage.getItem('arena_streak_battle_data');
      if (storedData) {
        try {
          battleData.value = JSON.parse(storedData);
          // 清除 sessionStorage
          sessionStorage.removeItem('arena_streak_battle_data');
        } catch (err) {
          console.error('解析战报数据失败', err);
        }
      }
    });

    return {
      router,
      battleData,
      resultText,
      resultSymbol,
      toggleBattle,
      isBattleExpanded,
      getBeastImage
    };
  }
};
</script>

<style scoped>
.report-page {
  background: #ffffff;
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

.result-line {
  font-weight: bold;
}

.battle-log {
  color: #333;
}

.battle-detail {
  background: #ffffff;
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

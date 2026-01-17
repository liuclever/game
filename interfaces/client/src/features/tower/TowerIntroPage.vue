<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// 获取塔类型
const towerType = computed(() => route.query.type || 'tongtian')

// 塔配置
const towerConfigs = {
  tongtian: {
    name: '通天塔',
    rules: [
      '通天塔闯塔需要消耗20活力',
      '每通过一层都可获得随机道具、丰厚铜钱',
      '玩家每天可闯塔1次（VIP5以上可增加次数）',
      '每一层的战斗需要消耗10秒',
    ],
    extraSection: null,
  },
  longwen: {
    name: '龙纹塔',
    rules: [
      '龙纹塔闯塔需要消耗20活力',
      '每通过一层都可概率获得随机战骨卷轴、丰厚铜钱',
      '玩家每天可闯塔1次（VIP5以上可增加次数）',
      '每一层的战斗需要消耗10秒',
    ],
    extraSection: {
      title: '【战骨卷轴产出分布】',
      items: [
        '1~10层 碎空卷轴',
        '11~20层 猎魔卷轴',
        '21~30层 龙炎卷轴',
        '31~40层 奔雷卷轴',
        '41~50层 凌霄卷轴',
        '51~60层 麒麟卷轴',
        '61~70层 武神卷轴',
        '71~80层 弑天卷轴',
        '81~90层 毁灭卷轴',
        '91~100层 圣魂卷轴',
      ],
    },
    maxFloor: 100,
  },
  zhanling: {
    name: '战灵塔',
    rules: [
      '战灵塔闯塔需要消耗20活力',
      '每通过一层都可概率获得随机战灵材料、丰厚铜钱',
      '玩家每天可闯塔1次（VIP5以上可增加次数）',
      '每一层的战斗需要消耗10秒',
    ],
    extraSection: null,
  },
}

const currentConfig = computed(() => towerConfigs[towerType.value] || towerConfigs.tongtian)

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="intro-page">
    <!-- 标题 -->
    <div class="section title">【{{ currentConfig.name }}规则】</div>

    <!-- 规则列表 -->
    <div v-for="(rule, index) in currentConfig.rules" :key="index" class="section">
      {{ index + 1 }}.{{ rule }}
    </div>

    <!-- 额外内容（如战骨卷轴分布） -->
    <template v-if="currentConfig.extraSection">
      <div class="section title">{{ currentConfig.extraSection.title }}</div>
      <div v-for="(item, index) in currentConfig.extraSection.items" :key="'extra-' + index" class="section">
        {{ item }}
      </div>
    </template>

    <!-- 导航 -->
    <div class="section spacer">
      <a class="link" @click="goBack">返回前页</a>
    </div>
    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.intro-page {
  background: #ffffff;
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
  margin-bottom: 8px;
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
  font-size: 11px;
}

.footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px solid #CCCCCC;
}
</style>

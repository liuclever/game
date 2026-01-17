<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const tabs = ['神兽', '道具',]
const activeTab = ref(tabs[0])

const exchangeMap = ref({
  神兽: [
    { name: '青龙召唤球', desc: '神·青龙召唤球×1', limit: '限1次' },
    { name: '玄武召唤球', desc: '神·玄武召唤球×1', limit: '限1次' },
    { name: '朱雀召唤球', desc: '神·朱雀召唤球×1', limit: '限1次' },
    { name: '绝影召唤球', desc: '神·绝影召唤球×1', limit: '限1次' },
    { name: '白虎召唤球', desc: '神·白虎召唤球×1', limit: '限1次' },
    { name: '不死鸟召唤球', desc: '神·不死鸟召唤球×1', limit: '限1次' },
    { name: '罗刹召唤球', desc: '神·罗刹召唤球×1', limit: '限1次' },
  ],
  道具: [
    { name: '逆鳞', desc: '神·逆鳞×1', limit: '限1次' },
    { name: '进化神草', desc: '进化神草×1', limit: '限1次' },
    { name: '进化圣水晶', desc: '进化圣水晶×1', limit: '限1次' },
  ],
  活动: [
    {
      name: '老玩家回馈礼包',
      detail:
        '老玩家回馈礼包：领取后礼包会进入背包，开启可获得活力草、强力捕捉球、骰子包、化仙丹、双倍卡、重生丹、追魂法宝、焚火晶、传送符、迷踪符、灵力水晶、招财神符、庄园建造手册、镇妖符、炼魂丹、金袋各1个。',
      actionText: '领取',
      limit: '限1次',
    },
  ],
})

const currentExchanges = computed(() => exchangeMap.value[activeTab.value] ?? [])

const exchangeRoutes = {
  '青龙召唤球': '/exchange/beast/qinglong',
  '玄武召唤球': '/exchange/beast/xuanwu',
  '朱雀召唤球': '/exchange/beast/zhuque',
  '绝影召唤球': '/exchange/beast/jueying',
  '白虎召唤球': '/exchange/beast/baihu',
  '不死鸟召唤球': '/exchange/beast/businiao',
  '罗刹召唤球': '/exchange/beast/luosha',
  '逆鳞': '/exchange/item/nilin',
  '进化神草': '/exchange/item/god-herb',
  '进化圣水晶': '/exchange/item/god-crystal',
}

const handleExchange = (item) => {
  const target = exchangeRoutes[item.name]
  if (target) {
    router.push(target)
  } else {
    console.error(`兑换：${item.desc}`)
  }
}

const getPrefix = (name) => {
  if (['进化神草', '进化圣水晶'].includes(name)) {
    return ''
  }
  return '神·'
}

const getDisplayText = (item) => {
  if (item.detail) {
    return item.detail
  }
  return `${getPrefix(item.name)}${item.name}×1`
}

const getActionLabel = (item) => item.actionText ?? '兑换'

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="exchange-page">
    <div class="section title">【兑换】</div>
    <div class="section tabs">
      <template v-for="tab in tabs" :key="tab">
        <a
          class="link"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >{{ tab }}</a>
        <span v-if="tab !== tabs[tabs.length - 1]"> | </span>
      </template>
    </div>

    <div class="section" v-for="item in currentExchanges" :key="item.name">
      {{ getDisplayText(item) }}
      <a class="link" @click="handleExchange(item)">{{ getActionLabel(item) }}</a>
    </div>

    <div class="section">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>

   
  </div>
</template>

<style scoped>
.exchange-page {
  padding: 16px;
  line-height: 1.8;
}

.link,
.exchange-page a {
  color: #1e4fd8;
  text-decoration: none;
}

.link:hover,
.exchange-page a:hover {
  text-decoration: underline;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
}

.tabs {
  margin-bottom: 12px;
}

.section {
  margin-bottom: 8px;
}

.footer {
  margin-top: 24px;
}

.small {
  font-size: 18px;
}
</style>

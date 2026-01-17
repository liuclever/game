<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateTo = (routeName) => {
  if (routeName) {
    router.push({ name: routeName })
  }
}
</script>

<template>
  <div class="bottom-bar">
    <div class="inner">
      <div class="line">
        皇域：<span class="link" @click="navigateTo('Home')">皇家召唤协会</span>　
        皇城：<span class="link" @click="navigateTo('SummonKingChallenge')">召唤之王挑战赛</span>
      </div>
      <div class="line">
        <span class="link" @click="navigateTo('Beast')">幻兽岛</span>、
        <span class="link" @click="navigateTo('Inventory')">背包</span>、
        <span class="link" @click="navigateTo('Shop')">商城</span>、
        <span class="link" @click="navigateTo('Sponsor')">赞助</span>、
        <span class="link" @click="navigateTo('Gifts')">礼包</span>
      </div>
      <div class="line">
        <span class="link" @click="navigateTo('Alliance')">联盟</span>：
        <span class="link" @click="navigateTo('AllianceWar')">盟战</span>、
        <span class="link" @click="navigateTo('Map')">地图</span>、
        <span class="link" @click="navigateTo('AllianceTalent')">天赋</span>、
        <span class="link" @click="navigateTo('HuaXian')">化仙</span>
      </div>
      <div class="line">
        <span class="link" @click="navigateTo('RefinePot')">结界</span>、
        <span class="link" @click="navigateTo('Ranking')">排行</span>、
        <span class="link" @click="navigateTo('DailyTasks')">成就</span>、
        <span class="link" @click="navigateTo('Battlefield')">圣战</span>、
        <span class="link" @click="navigateTo('Tree')">攻路</span>
      </div>
      <div class="line">
        <span class="link" @click="navigateTo('manor')">特训家园</span>－
        <span class="link" @click="navigateTo('WorldChat')">广场</span>－
        <span class="link" @click="navigateTo('HandbookIndex')">导航</span>－
        <span class="link" @click="navigateTo('Login')">退出</span>
      </div>
      <div class="line">
        <span class="link" @click="navigateTo('VipPrivilege')">VIP()</span>、
        <span class="link" @click="navigateTo('Dynamics')">空间()</span>、
        <span class="link" @click="navigateTo('manor')">家园()</span>、
        <span class="link readonly">微博()</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bottom-bar {
  background: #e5f0ff;
  border-top: 1px solid #c0d4f0;
  font-size: 18px;
}

.inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4px 8px;
  line-height: 1.4;
}

.line + .line {
  margin-top: 2px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.readonly {
  color: #000000;
  cursor: default;
  pointer-events: none;
}
</style>

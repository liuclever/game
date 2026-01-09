<template>
  <div class="bottom-bar">
    <div class="inner">
      <div class="line">
        皇域：<span class="link">皇家召唤协会</span>　
        皇城：<span class="link readonly">召唤之王挑战赛</span>
      </div>
      <div class="line">
        幻兽岛、背包、商城、赞助、礼包
      </div>
      <div class="line">
        联盟：盟战、地图、天赋、化仙
      </div>
      <div class="line">
        结界、排行、成就、圣战、攻路
      </div>
      <div class="line">
        特训家园－广场－导航－退出
      </div>
      <div class="line">
        VIP()、空间()、家园()、微博()
      </div>
    </div>
  </div>
</template>

<style scoped>
.bottom-bar {
  background: #e5f0ff;
  border-top: 1px solid #c0d4f0;
  font-size: 12px;
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
}

.link.readonly {
  color: #000000;
  cursor: default;
  pointer-events: none;
}
</style>

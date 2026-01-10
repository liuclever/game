<template>
  <div class="panel">
    <div class="tabs">
      <span class="link">[世界]</span>
      <span class="link">[动态]</span>
      <span class="link">[信件]</span>
    </div>
    <div class="messages">
      <div class="msg">【召唤之王】(23:32) 低调🐦：大量收号啦！V7及以下二十，V8及以上代价来</div>
      <div class="msg">【喊话】(07:47) 心平能怂三千疾🐦：</div>
      <div class="msg">【联盟】(20:42) 执扇9号🐦：每天签到不是送一个穿越神符，你可以玩一次哦</div>
      <div class="msg">
        【系统】(08:42) 20点打开1个黄金召唤礼包，获得铜钱×45000，金之结晶×2，传送符×1，强力捕捉球×1
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
}

.tabs {
  margin-bottom: 4px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-right: 4px;
}

.messages {
  max-height: 220px;
  overflow-y: auto;
}

.msg + .msg {
  margin-top: 2px;
}
</style>

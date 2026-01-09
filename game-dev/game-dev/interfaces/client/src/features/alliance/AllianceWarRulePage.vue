<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goWar = () => {
  router.push('/alliance/war')
}

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="rule-page">
    <div class="section title-row">
      【盟战规则】
      <a class="link" @click.prevent="goWar">返回</a>
    </div>

    <div class="section">
      1. 联盟中盟主和副盟主可以报名参加盟战
    </div>

    <div class="section">
      2. 每周举行2场盟战分别是周三、周六，报名时间：
      <div class="indent">
        (1) 周三盟战：周一00:00点至周三16:00点<br>
        (2) 周六盟战：周四00:00点至周六16:00点
      </div>
    </div>

    <div class="section">
      3. 联盟报名参加盟战后，出战的联盟成员需要进行签到才能参加盟战
    </div>

    <div class="section">
      4. 签到时间：
      <div class="indent">
        (1) 周三盟战：盟主报名后至周三20:00点<br>
        (2) 周六盟战：盟主报名后至周六20:00点
      </div>
    </div>

    <div class="section">
      5. 盟战当日的20~24点为系统统计比赛结果时间，当日24:00点前公布成绩
    </div>

    <div class="section">
      6. 盟战军队
      <div class="indent">
        (1) 飞龙军：联盟成员均可报名加入，不限制成员等级，军队前30人出战<br>
        (2) 伏虎军：联盟成员中，40级及40级以下的成员可以加入伏虎军，军队前30人出战
      </div>
    </div>

    <div class="section">
      7. 盟主和副盟主可以调整成员的出战顺序
    </div>

    <div class="section">
      8. 玩家签到盟战即可获得1点个人战功、铜钱3万、随机结晶1个
    </div>

    <div class="section">
      9. 每击杀一个对手可获得1点个人战功，战功可用于兑换道具
    </div>

    <div class="section">
      10. 联盟每夺沦一个对手联盟，可获得1点联盟战功，战功可用于兑换全员加成
    </div>

    <div class="section spacer">
      <a class="link" @click.prevent="goWar">返回盟战</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.rule-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 10px 14px 24px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 6px 0;
}

.title-row {
  font-weight: bold;
  font-size: 15px;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.indent {
  margin-left: 12px;
}

.gray {
  color: #777;
}

.small {
  font-size: 11px;
}

.footer {
  margin-top: 20px;
}

.spacer {
  margin-top: 16px;
}
</style>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBackCompetition = () => {
  router.push('/alliance/competition')
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="rules-page">
    <div>【争霸赛规则】</div>
    
    <div style="margin-top: 8px;">
      <div>1.联盟中盟主和副盟主可以报名参加争霸赛</div>
      <div>2.每周举行1场争霸赛，报名时间：周一0点至周三23:59</div>
      <div>3.联盟报名参加争霸赛后，出战的联盟成员需要进行签到才能参加争霸赛</div>
      <div>4.签到时间：周四0点-周日20:00点，战队至少一名成员签到才可激活参与本次争霸赛</div>
      <div>5.比赛当日的20点-22点为战斗时间，当日22:00点公布成绩</div>
      <div>6.联盟战队对应玩家等级如下</div>
      <div style="margin-left: 20px;">
        <div>（1）犊虎战队：1-39</div>
        <div>（2）白虎战队：40-49</div>
        <div>（3）青龙战队：50-59</div>
        <div>（4）朱雀战队：60-69</div>
        <div>（5）玄武战队：70-79</div>
        <div>（6）战神战队：80-100</div>
      </div>
      <div>7.每个战队最多可参战5人，最少参战1人，盟主和副盟主可以调整成员的出战顺序，调整时间截至周日20点</div>
    </div>

    <div style="margin-top: 12px;">
      <div>争霸赛积分计算方式：</div>
      <div>战队获得冠军，可获得20点积分</div>
      <div>战队进入2强，可获得15点积分</div>
      <div>战队进入4强，可获得10点积分</div>
      <div>战队进入8强，可获得5点积分</div>
      <div>战队成员每淘汰一名对手可获得2点个人积分</div>
    </div>

    <div style="margin-top: 12px;">
      <div>争霸赛奖励：</div>
      <div>战队奖励：进入八强的每个战队，战队成员都可领取对应排名奖励</div>
      <div>全盟奖励：联盟威望为战队积分和个人积分的总和，威望前八名的联盟所有成员可领取全盟奖励</div>
      <div>精英奖励：个人积分排名进入前八名将获得精英排名奖励</div>
      <div>奖励在争霸赛结束后可领取，最迟领取时间为下周六</div>
    </div>

    <div style="margin-top: 16px;">
      <a class="link" @click="goBackCompetition">返回争霸赛</a>
    </div>
    <div>
      <a class="link" @click="goBackAlliance">返回联盟</a>
    </div>
    <div>
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.rules-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 17px;
  line-height: 1.8;
  font-family: SimSun, "宋体", serif;
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

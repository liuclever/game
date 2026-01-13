<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => router.push('/')
</script>

<template>
  <div class="tree-rule">
    <div class="section title">幸运古树玩法规则：</div>

    <div class="section indent">1、幸运古树每天掉落一个幸运果，幸运果上面刻有1个幸运数字；</div>
    <div class="section indent">2、玩家每天登陆即可免费领取到1个幸运果；</div>
    <div class="section indent">3、周一至周六登录，每天可领取1个红果实幸运数字，数字范围01-100；</div>
    <div class="section indent">4、周日登录，可领取1个蓝果实幸运数字，数字范围01-100；</div>
    <div class="section indent">5、每周从100个红果实数字球中随机选出6个数字，从100个蓝果实数字球中随机选出1个数字，组合而成当周幸运数字；</div>
    <div class="section indent">6、当周幸运数字，下周一统一公布；</div>
    <div class="section indent">7、玩家获奖后，需手动领取，奖励有效期为一周，即在下次公布幸运数字时，如未领取当周奖励，则奖励作废。</div>

    <div class="section spacer">
      <a class="link" @click="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.tree-rule {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.7;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  margin-top: 6px;
}

.indent {
  padding-left: 12px;
}

.spacer {
  margin-top: 10px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-right: 10px;
}
</style>



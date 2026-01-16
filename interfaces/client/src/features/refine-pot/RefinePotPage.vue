<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goRefine = () => {
  router.push('/refine-pot/refine')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="refine-pot-page">
    <div class="section title">
      上古神器炼妖壶现世！
    </div>
    <div class="section indent">
      相传他能改善召唤大陆幻兽体质，打造至强的满技能。全<span class="stars">★★★★★</span>幻兽。
    </div>

    <div class="section title">【炼妖壶-炼妖】</div>
    <div class="section indent">
      通过消耗一只副幻兽，来较大概率增强主幻兽的专项能力。副幻兽的该能力提升将会继承至主幻兽。
    </div>
    <div class="section indent">
      炼妖所需材料，每日必做白银、黄金礼包一定概率免费获得。
    </div>

   

    <div class="section indent">
      <a class="link blue" @click.prevent="goRefine">去炼妖</a>
    </div>

    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.refine-pot-page {
  background: #ffffff;
  min-height: 100vh;
  font-family: SimSun, '宋体', serif;
  font-size: 16px;
  line-height: 1.6;
  padding: 8px 12px 40px;
  color: #000;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
  color: #000;
}

.indent {
  padding-left: 8px;
}

.stars {
  color: #ff9900;
  font-weight: bold;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>

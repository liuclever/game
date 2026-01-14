<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHpRefine = () => {
  router.push('/refine-pot/refine/hp')
}

const goSpeedRefine = () => {
  router.push('/refine-pot/refine/speed')
}

const goPhysicalRefine = () => {
  router.push('/refine-pot/refine/physical')
}

const goPhysicalDefenseRefine = () => {
  router.push('/refine-pot/refine/physical-defense')
}

const goMagicRefine = () => {
  router.push('/refine-pot/refine/magic')
}

const goMagicDefenseRefine = () => {
  router.push('/refine-pot/refine/magic-defense')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="refine-detail-page">
    <div class="section title">【炼妖】</div>
   
    <div class="section indent">
      <a class="link" @click.prevent="goHpRefine">气血资质炼妖</a>
    </div>
    <div class="section indent">
      <a class="link" @click.prevent="goSpeedRefine">速度资质炼妖</a>
    </div>
    <div class="section indent">
      <a class="link" @click.prevent="goPhysicalRefine">物攻资质炼妖</a>
    </div>
    <div class="section indent">
      <a class="link" @click.prevent="goPhysicalDefenseRefine">物防资质炼妖</a>
    </div>
    <div class="section indent">
      <a class="link" @click.prevent="goMagicRefine">法攻资质炼妖</a>
    </div>
    <div class="section indent">
      <a class="link" @click.prevent="goMagicDefenseRefine">法防资质炼妖</a>
    </div>

    <div class="section indent notice-title">炼妖壶说明：</div>
    <div class="section indent sub-title">（一）功能解释：</div>
    <div class="section indent">
      1. 通过献祭一只副幻兽，来较大概率增强主幻兽的气血、物攻、法攻、物防、法防、速度的资质，炼妖之后副幻兽会消失。
    </div>
    <div class="section indent">
      2. 炼魂丹可以通过商店购买直接获得，每日必做任务中的白银和黄金礼包会开出。
    </div>

    <div class="section indent sub-title">（二）炼妖的条件：</div>
    <div class="section indent">
      1. 副幻兽对应资质必须比主幻兽高才能进行炼妖操作。例如：副幻兽气血资质为900，主幻兽气血资质为700，此时可以献祭副幻兽提高主幻兽的气血资质。
    </div>
    <div class="section indent">
      2. 炼妖会消耗铜钱和炼魂丹。具体数量会在（三）中说明。
    </div>

    <div class="section indent sub-title">（三）幻兽所能炼妖资质的讲解：</div>
    <div class="section indent">
      1. 每次炼妖完后，主幻兽对应资质数值增加说明：
    </div>
    <div class="section indent list">
      ① 副幻兽某一资质数值与主幻兽对应资质的差值 X 为：0 ≤ X &lt; 20，此时炼妖一次，主幻兽该资质数值增加值 y 为：-5 ≤ y ≤ 2；
    </div>
    <div class="section indent list">
      ② 差值 X 为：20 ≤ X &lt; 60，此时炼妖一次，增加值 y 为：2 &lt; y ≤ 5；
    </div>
    <div class="section indent list">
      ③ 差值 X 为：60 ≤ X &lt; 100，此时炼妖一次，增加值 y 为：5 &lt; y ≤ 9；
    </div>
    <div class="section indent list">
      ④ 差值 X 为：X ≥ 100，此时炼妖一次，增加值 y 为：9 &lt; y ≤ 15。
    </div>
    <div class="section indent">
      2. 具体炼妖所需条件和材料说明请在各资质页面查看。
    </div>

    <div class="section indent notice-title">炼妖须知：</div>
    <div class="section indent">1、炼妖提升或降低的资质数值取决于主宠与副宠的资质差</div>
    <div class="section indent">2、副宠需对应资质比主宠高才可作为炼妖素材进行炼妖</div>
    <div class="section indent">3、炼妖时可能会降低资质</div>

    <div class="section">
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.refine-detail-page {
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

.notice-title {
  margin-top: 8px;
  font-weight: bold;
}

.sub-title {
  margin-top: 6px;
  font-weight: bold;
}

.list {
  padding-left: 16px;
}

.link {
  color: #0066cc;
  text-decoration: none;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}
</style>

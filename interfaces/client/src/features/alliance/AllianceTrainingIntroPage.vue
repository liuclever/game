<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="training-intro-page">
    <div class="section header">
      <span class="title">【火能修行简介】</span>
      <a class="link" @click.prevent="goAlliance">返回</a>
    </div>

    <ol class="intro-list">
      <li>火能修行是上古流传的至高秘法，通过修行可获取大量升级声望；</li>
      <li>火能修行 2 小时结束，期间不会占用普通修行时间；</li>
      <li>玩家每日消耗贡献领取 1 次火能原石；</li>
      <li>玩家获得材料后，必须寻找到盟友一起使用“焚天炉”修行；</li>
      <li>一起修行的玩家越多，获得收益越多；</li>
      <li>修行结束后，炉内的残渣“焚火晶”，是联盟建设的上佳材料；</li>
    </ol>


    <div class="section links">
      <a class="link" @click.prevent="goAlliance">返回联盟</a>
      <a class="link" @click.prevent="goHome">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.training-intro-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 12px 16px;
  font-family: SimSun, '宋体', serif;
  font-size: 17px;
  line-height: 1.8;
  color: #333;
}

.section {
  margin-bottom: 12px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.title {
  color: #8b4513;
}

.link {
  color: #0066cc;
  cursor: pointer;
}

.link + .link {
  margin-left: 16px;
}

.link:hover {
  text-decoration: underline;
}

.intro-list {
  margin: 0;
  padding-left: 18px;
}

.meta {
  font-size: 18px;
  color: #555;
  line-height: 1.6;
}

.links {
  font-size: 16px;
}
</style>

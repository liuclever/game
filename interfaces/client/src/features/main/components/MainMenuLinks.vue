<script setup>
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

// 导航到战灵：优先跳到第一只幻兽的战灵页
const goSpirit = async () => {
  try {
    const res = await http.get('/spirit/page-data')
    if (res.data && res.data.ok) {
      const beasts = res.data.beasts || []
      const firstId = beasts.length ? beasts[0].id : null
      if (firstId) {
        return router.push(`/beast/${firstId}/spirit`)
      }
    }
  } catch (e) {
    console.error('获取战灵默认数据失败', e)
  }
  // 若无幻兽或请求失败，进入灵件室
  router.push('/spirit/warehouse')
}

const handleClick = (name) => {
  const key = String(name || '').trim()
  if (!key) return

  // 特殊处理：战灵
  if (key === '战灵') return goSpirit()

  const routes = {
    '背包': '/inventory',
    '幻兽': '/beast',
    '商城': '/shop',
    '赞助': '/sponsor',
    '礼包': '/gifts',
    '联盟': '/alliance',
    '盟战': '/alliance/war',
    '地图': '/map',
    '化仙': '/huaxian',
    '切磋': '/spar/report',
    '闯塔': '/tower',
    '战场': '/battlefield',
    '擂台': '/arena',
    '古树': '/tree',
    '排行': '/ranking',
    '图鉴': '/handbook',
    '兑换': '/exchange',
    '签到': '/signin',
    'VIP': '/vip',
  }

  if (routes[key]) {
    router.push(routes[key])
  }
}
</script>

<template>
  <!-- 严格复刻主页“导航菜单”的文案与布局（5行×5项，使用“. ”分隔，部分为只读） -->
  <div class="main-menu">
    <div class="section">
      <a class="link" @click="handleClick('幻兽')">幻兽</a>. <a class="link" @click="handleClick('背包')">背包</a>. <a class="link" @click="handleClick('商城')">商城</a>. <a class="link" @click="handleClick('赞助')">赞助</a>. <a class="link" @click="handleClick('礼包')">礼包</a>
    </div>
    <div class="section">
      <a class="link" @click="handleClick('联盟')">联盟</a>. <a class="link" @click="handleClick('盟战')">盟战</a>. <a class="link" @click="handleClick('地图')">地图</a>. <span class="link readonly">天赋</span>. <a class="link" @click="handleClick('化仙')">化仙</a>
    </div>
    <div class="section">
      <a class="link" @click="handleClick('切磋')">切磋</a>. <a class="link" @click="handleClick('闯塔')">闯塔</a>. <a class="link" @click="handleClick('战场')">战场</a>. <a class="link" @click="handleClick('擂台')">擂台</a>. <span class="link readonly">坐骑</span>
    </div>
    <div class="section">
      <a class="link" @click="handleClick('古树')">古树</a>. <a class="link" @click="handleClick('排行')">排行</a>. <span class="link readonly">成就</span>. <a class="link" @click="handleClick('图鉴')">图鉴</a>. <span class="link readonly">攻略</span>
    </div>
    <div class="section">
      <a class="link" @click="handleClick('兑换')">兑换</a>. <a class="link" @click="handleClick('签到')">签到</a>. <span class="link readonly">论坛</span>. <a class="link" @click="handleClick('VIP')">VIP</a>. <span class="link readonly">安全锁</span>
    </div>
  </div>
</template>

<style scoped>
.main-menu {
  margin-top: 12px;
}

.section {
  margin: 2px 0;
}

.link {
  color: #0066CC;
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
  text-decoration: none;
}

.link.readonly:hover {
  text-decoration: none;
}
</style>



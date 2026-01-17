<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import MainMenuLinks from '@/features/main/components/MainMenuLinks.vue'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const gifts = ref([])
const claimingKey = ref('')

const fetchGifts = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await http.get('/gifts/list')
    if (res.data?.ok) {
      gifts.value = res.data.gifts || []
    } else {
      throw new Error(res.data?.error || '加载失败')
    }
  } catch (e) {
    console.error('加载礼包失败', e)
    error.value = e?.response?.data?.error || e?.message || '加载礼包失败'
  } finally {
    loading.value = false
  }
}

const claimGift = async (gift) => {
  if (!gift || !gift.key) return
  if (gift.claimed) {
    return
  }
  if (claimingKey.value) return

  claimingKey.value = gift.key
  try {
    const res = await http.post('/gifts/claim', { key: gift.key })
    if (res.data?.ok) {
      // 按需求：去除所有弹框提示，成功后仅静默刷新列表
      await fetchGifts()
    } else {
      throw new Error(res.data?.error || '领取失败')
    }
  } catch (e) {
    console.error('领取礼包失败', e)
    // 不弹框；仅显示页面内错误（非弹框）
    error.value = e?.response?.data?.error || e?.message || '领取礼包失败'
  } finally {
    claimingKey.value = ''
  }
}

onMounted(fetchGifts)
</script>

<template>
  <div class="gifts-page">
    <div class="line">【礼包】</div>

    <div v-if="loading" class="line gray">加载中...</div>
    <div v-else-if="error" class="line error">{{ error }}</div>

    <template v-else>
      <div class="line" v-for="gift in gifts" :key="gift.key">
        <span class="gift-name">{{ gift.name }}</span><span class="gift-detail">：{{ gift.detail }}</span>
        <template v-if="gift.claimed">
          <span class="gray"> 已领取</span>
        </template>
        <template v-else>
          <a class="link" @click="claimGift(gift)">{{ claimingKey === gift.key ? '领取中...' : '领取' }}</a>
        </template>
      </div>
    </template>

    <!-- 主页菜单（严格复刻主页内容与UI） -->
    <MainMenuLinks />

    <div class="line">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>
  </div>
</template>

<style scoped>
.gifts-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 18px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.line {
  margin: 2px 0;
}

.gift-name {
  font-weight: 700;
  color: #000000;
}

.gift-detail {
  font-weight: 400;
  color: #000000;
}

.gray {
  color: #666;
}

.error {
  color: #c0392b;
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

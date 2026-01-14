<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()

const loading = ref(true)
const playerInfo = ref({
  vipLevel: 0,
  diamondSpent: 0,
  claimedGiftLevels: [], // 已领取的礼包等级
  dailyCopperClaimed: false,
})
const vipPrivilegesData = ref(null)

// 当前VIP等级数据
const currentVipData = computed(() => {
  if (!vipPrivilegesData.value) return null
  return vipPrivilegesData.value.vip_levels.find(v => v.level === playerInfo.value.vipLevel)
})

// 下一级VIP数据
const nextVipData = computed(() => {
  if (!vipPrivilegesData.value) return null
  return vipPrivilegesData.value.vip_levels.find(v => v.level === playerInfo.value.vipLevel + 1)
})

// 距离下一级还需多少
const expToNextLevel = computed(() => {
  if (!nextVipData.value) return 0
  return Math.max(0, nextVipData.value.required_diamond - playerInfo.value.diamondSpent)
})

// 可领取的见面礼包列表（已解锁但未领取的）
const availableGifts = computed(() => {
  if (!vipPrivilegesData.value || playerInfo.value.vipLevel === 0) return []
  return vipPrivilegesData.value.vip_levels
    .filter(v => v.level > 0 && v.level <= playerInfo.value.vipLevel && !playerInfo.value.claimedGiftLevels.includes(v.level))
})

// 格式化礼包内容为一行文字
const formatGiftItems = (items) => {
  if (!items || items.length === 0) return ''
  return items.map(item => `${item.name}x${item.amount}`).join('、')
}

// 格式化修炼模式
const formatCultivationModes = (modes) => {
  return modes.filter(m => m > 8).map(m => m + '小时').join('、')
}

const loadData = async () => {
  loading.value = true
  try {
    // 加载VIP配置
    const configRes = await fetch('/configs/vip_privileges.json')
    vipPrivilegesData.value = await configRes.json()
    
    // 加载玩家VIP信息
    const vipRes = await http.get('/vip/info')
    if (vipRes.data?.ok) {
      playerInfo.value = {
        vipLevel: vipRes.data.vip_level || 0,
        diamondSpent: vipRes.data.diamond_spent || 0,
        claimedGiftLevels: vipRes.data.claimed_gift_levels || [],
        dailyCopperClaimed: vipRes.data.daily_copper_claimed || false,
      }
    }
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const goSponsor = () => {
  router.push('/sponsor')
}

const showPrivilegesModal = ref(false)

const viewAllPrivileges = () => {
  showPrivilegesModal.value = true
}

// 领取见面礼包
const claimWelcomeGift = async (level) => {
  try {
    const res = await http.post('/vip/claim-gift', { level })
    if (res.data?.ok) {
      alert(res.data.message || `成功领取VIP${level}见面礼包！`)
      playerInfo.value.claimedGiftLevels.push(level)
    } else {
      alert(res.data?.error || '领取失败')
    }
  } catch (error) {
    alert('领取失败: ' + (error.response?.data?.error || error.message))
  }
}

// 领取每日铜币
const claimDailyCopper = async () => {
  try {
    const res = await http.post('/vip/claim-daily-copper')
    if (res.data?.ok) {
      alert(res.data.message || '领取成功！')
      playerInfo.value.dailyCopperClaimed = true
    } else {
      alert(res.data?.error || '领取失败')
    }
  } catch (error) {
    alert('领取失败: ' + (error.response?.data?.error || error.message))
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="vip-page">
    <div class="section">【VIP】</div>
    
    <div v-if="loading" class="section">加载中...</div>
    <template v-else>
      <div class="section">
        您的级别: <span class="vip-icon">👑</span>VIP{{ playerInfo.vipLevel }}
        <a class="link" @click="viewAllPrivileges">查看特权</a>
      </div>
      
      <div class="section">
        累计消费: {{ playerInfo.diamondSpent }}宝石 / {{ nextVipData ? nextVipData.required_diamond : '∞' }}宝石
      </div>
      
      <div class="section" v-if="nextVipData">
        再消费{{ expToNextLevel }}宝石即可成为VIP{{ playerInfo.vipLevel + 1 }}!
      </div>
      <div class="section" v-else>
        您已达到最高VIP等级!
      </div>
      
      <!-- 可领取的见面礼包 -->
      <template v-if="availableGifts.length > 0">
        <div class="section">【可领取礼包】</div>
        <div class="section" v-for="gift in availableGifts" :key="gift.level">
          VIP{{ gift.level }}见面礼包: <a class="link" @click="claimWelcomeGift(gift.level)">领取</a>
          <div class="gift-detail">({{ formatGiftItems(gift.welcome_gift.items) }})</div>
        </div>
      </template>
      
      <!-- 每日铜币 -->
      <div class="section" v-if="currentVipData && currentVipData.privileges.daily_copper_chest > 0">
        每日{{ currentVipData.privileges.daily_copper_chest / 10000 }}万铜币宝箱: 
        <template v-if="playerInfo.dailyCopperClaimed">
          <span class="claimed">已领取</span>
        </template>
        <template v-else>
          <a class="link" @click="claimDailyCopper">领取</a>
        </template>
      </div>
      
      <template v-if="currentVipData && playerInfo.vipLevel > 0">
        <div id="privileges-section" class="section">【VIP{{ playerInfo.vipLevel }}特权】</div>
        
        <div class="section">
          1.招财神符使用(每日最多{{ currentVipData.privileges.fortune_talisman_uses }}次)
        </div>
        
        <div class="section">
          2.活力值上限增长为{{ currentVipData.privileges.vitality_max }}
        </div>
        
        <div class="section" v-if="currentVipData.privileges.cultivation_modes.length > 1">
          3.增加{{ formatCultivationModes(currentVipData.privileges.cultivation_modes) }}修炼模式
        </div>
        
        <div class="section">
          4.擂台普通场上限{{ currentVipData.privileges.arena_normal_limit }}次
        </div>
        
        <div class="section" v-if="currentVipData.privileges.arena_gold_limit > 10">
          5.擂台黄金场上限{{ currentVipData.privileges.arena_gold_limit }}次
        </div>
        
        <div class="section" v-if="currentVipData.privileges.beast_slot > 5">
          6.幻兽栏{{ currentVipData.privileges.beast_slot }}个
        </div>
        
        <div class="section" v-if="currentVipData.privileges.manor_yellow_land_open">
          7.开放庄园黄土地
        </div>
        
        <div class="section" v-if="currentVipData.privileges.manor_silver_land_open">
          8.开放庄园银土地
        </div>
        
        <div class="section" v-if="currentVipData.privileges.manor_gold_land_open">
          9.开放庄园金土地
        </div>
        
        <div class="section" v-if="currentVipData.privileges.war_spirit_free_wash > 1">
          10.战灵每日免费洗练{{ currentVipData.privileges.war_spirit_free_wash }}次
        </div>
      </template>
      
      <template v-else>
        <div id="privileges-section" class="section">【已享有特权】</div>
        <div class="section">暂无VIP特权，<a class="link" @click="goSponsor">立即充值</a>成为VIP!</div>
      </template>
    </template>
    
    <div class="section">
      <a class="link" @click="goSponsor">前往充值</a> | <a class="link" @click="goBack">返回游戏首页</a>
    </div>
    
    <!-- VIP特权弹窗 -->
    <div v-if="showPrivilegesModal" class="modal-overlay" @click="showPrivilegesModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          【所有VIP特权】
          <span class="close-btn" @click="showPrivilegesModal = false">×</span>
        </div>
        <div class="modal-body">
          <template v-for="vip in vipPrivilegesData?.vip_levels.filter(v => v.level > 0)" :key="vip.level">
            <div class="vip-title">【VIP{{ vip.level }}特权】累计消费{{ vip.required_diamond }}宝石解锁</div>
            <div class="priv-item">1.VIP{{ vip.level }}见面礼包({{ formatGiftItems(vip.welcome_gift?.items) }})</div>
            <div class="priv-item">2.每日{{ vip.privileges.daily_copper_chest / 10000 }}万铜币宝箱</div>
            <div class="priv-item">3.招财神符使用(每日最多{{ vip.privileges.fortune_talisman_uses }}次)</div>
            <div class="priv-item">4.活力值上限{{ vip.privileges.vitality_max }}</div>
            <div class="priv-item" v-if="vip.privileges.cultivation_modes.length > 1">5.增加{{ formatCultivationModes(vip.privileges.cultivation_modes) }}修炼模式</div>
            <div class="priv-item">6.擂台普通场上限{{ vip.privileges.arena_normal_limit }}次</div>
            <div class="priv-item" v-if="vip.privileges.arena_gold_limit > 10">7.擂台黄金场上限{{ vip.privileges.arena_gold_limit }}次</div>
            <div class="priv-item" v-if="vip.privileges.beast_slot > 5">8.幻兽栏{{ vip.privileges.beast_slot }}个</div>
            <div class="priv-item" v-if="vip.privileges.manor_yellow_land_open">9.开放庄园黄土地</div>
            <div class="priv-item" v-if="vip.privileges.manor_silver_land_open">10.开放庄园银土地</div>
            <div class="priv-item" v-if="vip.privileges.manor_gold_land_open">11.开放庄园金土地</div>
            <div class="priv-item" v-if="vip.privileges.war_spirit_free_wash > 1">12.战灵每日免费洗练{{ vip.privileges.war_spirit_free_wash }}次</div>
            <br/>
          </template>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.vip-page {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 10px 15px;
  font-size: 17px;
  color: #333;
  font-family: 'SimSun', '宋体', serif;
  line-height: 1.8;
}

.section {
  margin: 4px 0;
}

.link {
  color: #0066cc;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.vip-icon {
  color: #ffd700;
}

.claimed {
  color: #999;
}

.gift-detail {
  font-size: 18px;
  color: #666;
  margin-left: 10px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #FFFFFF;
  border: 2px solid #8b4513;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 10px;
}

.modal-header {
  font-weight: bold;
  padding-bottom: 8px;
  border-bottom: 1px solid #ccc;
  margin-bottom: 8px;
  position: relative;
}

.close-btn {
  position: absolute;
  right: 0;
  top: -5px;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  font-size: 16px;
  line-height: 1.6;
}

.vip-title {
  color: #8b4513;
  font-weight: bold;
  margin-top: 5px;
}

.priv-item {
  margin-left: 10px;
}

</style>

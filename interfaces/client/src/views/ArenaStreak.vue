<template>
  <div class="arena-streak-page">
    <!-- 标题 -->
    <div class="section title">【连胜竞技场】</div>

    <!-- 开放时间提示 -->
    <div v-if="!isOpen" class="section">
      连胜竞技场开放时间：每天 8:00 - 23:00
    </div>

    <template v-else>
      <!-- 当前连胜王 -->
      <div class="section">
        当前连胜王: <a class="link username" @click="viewPlayer(streakKing.user_id)" v-if="streakKing.user_id">{{ streakKing.nickname }}</a><span v-else>{{ streakKing.nickname }}</span> - {{ streakKing.streak }}连胜
      </div>

      <!-- 我的连胜 -->
      <div class="section">
        当前连胜: {{ currentStreak }}次. 今日最高: {{ maxStreakToday }}次
      </div>

      <!-- 活力消耗提示 -->
      <div class="section">
        战斗消耗活力: {{ energyCost }}点（{{ maxStreakToday >= 6 ? '已达成6连胜' : '未达成6连胜' }}）
      </div>

      <!-- 对手列表 -->
      <div class="section">
        <div class="section indent">
          <span v-for="(opp, idx) in opponents" :key="opp.user_id">
            <a class="link username" @click="viewPlayer(opp.user_id)">{{ opp.nickname }}</a> ({{ opp.level }}级). <a class="link" @click="battle(opp.user_id)">切磋</a>
            <span v-if="idx < opponents.length - 1"> / </span>
          </span>
        </div>
        <div class="section indent" v-if="opponents.length === 0">
          暂无对手
        </div>
      </div>

      <!-- 刷新 -->
      <div class="section">
        刷新: {{ refreshSeconds }}秒后将自动刷新. 
        <a class="link" @click="refresh">立即刷新(消耗50元宝)</a>
      </div>

      <!-- 连胜奖励 -->
      <div class="section">
        <div class="section indent">连胜奖励:</div>
        <div class="section indent" v-for="level in [1,2,3,4,5,6]" :key="level">
          {{ level }}连胜: {{ getRewardText(level) }}. 
          <a class="link" @click="claimReward(level)" v-if="canClaim(level) && !claimedRewards.includes(level)">领取</a>
          <span v-else-if="claimedRewards.includes(level)">[已领取]</span>
          <span v-else>[未达成]</span>
        </div>
      </div>

      <!-- 连胜大奖 -->
      <div class="section">
        <div class="section indent">
          连胜大奖（全服连胜王专属，每日限领1次）: 铜钱60万+追魂法宝1+金袋5+招财神符1. 
          <a class="link" @click="claimGrandPrize" v-if="isStreakKing && !claimedGrandPrize">领取</a>
          <span v-else-if="claimedGrandPrize">[已领取]</span>
          <span v-else-if="!isStreakKing">[仅连胜王可领取]</span>
        </div>
      </div>

      <!-- 今日连胜榜 -->
      <div class="section">
        今日连胜榜: <a class="link" @click="loadRanking">{{ showRanking ? '收起' : '查看' }}</a>
      </div>
      <div class="section indent" v-if="showRanking">
        <div v-for="(r, idx) in ranking" :key="idx">
          {{ idx + 1 }}. <a class="link username" @click="viewPlayer(r.user_id)" v-if="r.user_id">{{ r.nickname }}</a><span v-else>{{ r.nickname }}</span> - {{ r.streak }}连胜
        </div>
      </div>

      <!-- 历届连胜王 -->
      <div class="section">
        历届连胜王: <a class="link" @click="loadHistory">{{ showHistory ? '收起' : '查看' }}</a>
      </div>
      <div class="section indent" v-if="showHistory">
        <div v-for="h in history" :key="h.date">
          {{ h.date }} - <a class="link username" @click="viewPlayer(h.user_id)" v-if="h.user_id">{{ h.nickname }}</a><span v-else>{{ h.nickname }}</span> ({{ h.streak }}连胜)
        </div>
      </div>
    </template>

    <!-- 返回 -->
    <div class="section">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>

    <!-- 战斗结果提示 -->
    <div v-if="battleResult" class="section" :style="{ color: battleResult.victory ? 'green' : 'red' }">
      {{ battleResult.message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  name: 'ArenaStreak',
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      isOpen: true,
      currentStreak: 0,
      maxStreakToday: 0,
      opponents: [],
      refreshSeconds: 300,
      streakKing: { nickname: '暂无', streak: 0 },
      claimedRewards: [],
      claimedGrandPrize: false,
      ranking: [],
      history: [],
      showRanking: false,
      showHistory: false,
      battling: false,
      battleResult: null,
      refreshTimer: null
    };
  },
  computed: {
    isStreakKing() {
      // 检查当前用户是否是连胜王
      return this.streakKing.user_id && this.streakKing.user_id === this.$root.userId;
    },
    energyCost() {
      // 计算活力消耗：未达成6连胜之前消耗100活力，达成6连胜之后消耗15活力
      return this.maxStreakToday >= 6 ? 15 : 100;
    }
  },
  mounted() {
    this.loadInfo();
    this.startRefreshTimer();
  },
  beforeUnmount() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  methods: {
    async loadInfo() {
      try {
        const res = await axios.get('/api/arena-streak/info');
        if (res.data.ok) {
          this.currentStreak = res.data.current_streak || 0;
          this.maxStreakToday = res.data.max_streak_today || 0;
          this.opponents = res.data.opponents || [];
          this.refreshSeconds = res.data.refresh_seconds || 300;
          this.streakKing = res.data.streak_king || { nickname: '暂无', streak: 0 };
          // 确保 claimedRewards 始终是数组
          this.claimedRewards = Array.isArray(res.data.claimed_rewards) ? res.data.claimed_rewards : [];
          this.claimedGrandPrize = res.data.claimed_grand_prize || false;
          
          // 调试日志
          console.log('连胜竞技场信息加载成功:');
          console.log('  当前连胜:', this.currentStreak);
          console.log('  今日最高:', this.maxStreakToday);
          console.log('  已领取奖励:', this.claimedRewards);
        } else {
          if (res.data.error && res.data.error.includes('开放时间')) {
            this.isOpen = false;
          }
        }
      } catch (err) {
        console.error('加载竞技场信息失败', err);
      }
    },
    
    async battle(opponentId) {
      if (this.battling) return;
      this.battling = true;
      this.battleResult = null;
      
      console.log('开始切磋，对手ID:', opponentId);
      
      try {
        console.log('发送切磋请求...');
        const res = await axios.post('/api/arena-streak/battle', {
          opponent_id: opponentId
        });
        
        console.log('收到响应:', res.data);
        
        if (res.data.ok) {
          // 存储战报数据到 sessionStorage（注意：战报数据在 battle 字段中）
          sessionStorage.setItem('arena_streak_battle_data', JSON.stringify(res.data.battle));
          
          console.log('跳转到战报页面...');
          // 跳转到战报页面
          this.router.push({
            path: '/arena/streak/battle-report'
          });
        } else {
          // 显示错误信息
          console.error('战斗失败:', res.data.error);
          this.battleResult = {
            victory: false,
            message: res.data.error || '战斗失败'
          };
        }
      } catch (err) {
        console.error('战斗请求异常:', err);
        console.error('错误详情:', err.response);
        // 显示错误信息
        this.battleResult = {
          victory: false,
          message: err.response?.data?.error || err.message || '战斗请求失败'
        };
      } finally {
        this.battling = false;
        console.log('切磋流程结束');
      }
    },
    
    async refresh() {
      // 清除之前的消息
      this.battleResult = null;
      
      try {
        const res = await axios.post('/api/arena-streak/refresh');
        if (res.data.ok) {
          // 显示成功消息
          this.battleResult = {
            victory: true,
            message: res.data.message || '刷新成功！'
          };
          // 重新加载信息（包括新的对手列表和刷新倒计时）
          await this.loadInfo();
          // 重置倒计时为300秒
          this.refreshSeconds = 300;
          
          // 3秒后自动清除消息
          setTimeout(() => {
            this.battleResult = null;
          }, 3000);
        } else {
          // 显示错误消息
          this.battleResult = {
            victory: false,
            message: res.data.error || '刷新失败'
          };
        }
      } catch (err) {
        console.error('刷新失败', err);
        // 显示错误消息
        this.battleResult = {
          victory: false,
          message: err.response?.data?.error || '刷新失败，请稍后重试'
        };
      }
    },
    
    async claimReward(level) {
      try {
        console.log(`尝试领取 ${level}连胜奖励...`);
        console.log('  当前 maxStreakToday:', this.maxStreakToday);
        console.log('  当前 claimedRewards:', this.claimedRewards);
        
        const res = await axios.post('/api/arena-streak/claim-reward', {
          streak_level: level
        });
        
        console.log('领取奖励响应:', res.data);
        
        if (res.data.ok) {
          // 确保 claimedRewards 是数组
          if (!Array.isArray(this.claimedRewards)) {
            this.claimedRewards = [];
          }
          // 添加到已领取列表
          if (!this.claimedRewards.includes(level)) {
            this.claimedRewards.push(level);
          }
          this.battleResult = {
            victory: true,
            message: res.data.message || '领取成功！'
          };
          setTimeout(() => {
            this.battleResult = null;
          }, 3000);
        } else {
          this.battleResult = {
            victory: false,
            message: res.data.error || '领取失败'
          };
        }
      } catch (err) {
        console.error('领取奖励失败', err);
        this.battleResult = {
          victory: false,
          message: err.response?.data?.error || '领取失败，请稍后重试'
        };
      }
    },
    
    async claimGrandPrize() {
      try {
        const res = await axios.post('/api/arena-streak/claim-grand-prize');
        
        if (res.data.ok) {
          this.claimedGrandPrize = true;
          this.battleResult = {
            victory: true,
            message: res.data.message || '恭喜！领取连胜大奖成功！'
          };
          setTimeout(() => {
            this.battleResult = null;
          }, 5000);
        } else {
          this.battleResult = {
            victory: false,
            message: res.data.error || '领取失败'
          };
        }
      } catch (err) {
        console.error('领取连胜大奖失败', err);
        this.battleResult = {
          victory: false,
          message: err.response?.data?.error || '领取失败，请稍后重试'
        };
      }
    },
    
    async loadRanking() {
      this.showRanking = !this.showRanking;
      if (this.showRanking && this.ranking.length === 0) {
        try {
          const res = await axios.get('/api/arena-streak/ranking');
          if (res.data.ok) {
            this.ranking = res.data.ranking;
          }
        } catch (err) {
          console.error('加载排行榜失败', err);
        }
      }
    },
    
    async loadHistory() {
      this.showHistory = !this.showHistory;
      if (this.showHistory && this.history.length === 0) {
        try {
          const res = await axios.get('/api/arena-streak/history');
          if (res.data.ok) {
            this.history = res.data.history;
          }
        } catch (err) {
          console.error('加载历史失败', err);
        }
      }
    },
    
    startRefreshTimer() {
      this.refreshTimer = setInterval(() => {
        if (this.refreshSeconds > 0) {
          this.refreshSeconds--;
        } else {
          // 倒计时到0时，自动刷新对手列表（不消耗元宝）
          this.autoRefresh();
        }
      }, 1000);
    },
    
    async autoRefresh() {
      // 自动刷新（倒计时到0时触发，不消耗元宝）
      try {
        await this.loadInfo();
      } catch (err) {
        console.error('自动刷新失败', err);
      }
    },
    
    canClaim(level) {
      return this.maxStreakToday >= level;
    },
    
    getRewardText(level) {
      const rewards = {
        1: '铜钱1000+双倍卡1+随机结晶1',
        2: '铜钱5000+强力捕捉球1+随机结晶1',
        3: '铜钱1万+化仙丹1+随机结晶1',
        4: '铜钱5万+活力草1+随机结晶1',
        5: '铜钱10万+活力草2+小喇叭2',
        6: '铜钱15万+重生丹2+神·逆鳞碎片5'
      };
      return rewards[level] || '';
    },
    
    viewPlayer(userId) {
      if (userId) {
        this.router.push({ path: '/player/detail', query: { id: userId } });
      }
    }
  }
};
</script>

<style scoped>
.arena-streak-page {
  background: #ffffff;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
}

.section.title {
  font-weight: bold;
  margin: 12px 0;
}

.section.indent {
  margin-left: 20px;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.username {
  color: #CC3300;
  font-weight: bold;
}
</style>

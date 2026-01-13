<template>
  <div class="battle-page">
    <!-- 标题 -->
    <div class="section">{{ battleTitle }}</div>

    <!-- 战斗双方 -->
    <div class="section">
      {{ attacker.nickname }} | {{ attacker.title }}
    </div>

    <!-- 幻兽对阵图 -->
    <div class="section" v-if="battleData">
      <div v-for="(beast, idx) in attackerBeasts" :key="'a' + idx" style="display: inline-block; margin: 5px;">
        <img :src="getBeastImage(beast)" :alt="beast.name" style="width: 60px; height: 60px;">
      </div>
      <span style="margin: 0 20px;">PK</span>
      <div v-for="(beast, idx) in defenderBeasts" :key="'d' + idx" style="display: inline-block; margin: 5px;">
        <img :src="getBeastImage(beast)" :alt="beast.name" style="width: 60px; height: 60px;">
      </div>
    </div>

    <!-- 幻兽信息 -->
    <div class="section" v-if="battleData">
      {{ attackerBeastsText }}
    </div>

    <!-- 战斗记录 -->
    <div class="section" v-if="battleLogs.length > 0">
      <div v-for="(log, idx) in battleLogs" :key="idx" class="section indent">
        【第{{ idx + 1 }}战】{{ log }}
      </div>
    </div>

    <!-- 查看详细战报 -->
    <div class="section" v-if="battleData">
      <a class="link" @click="showDetail = !showDetail">
        {{ showDetail ? '收起详细战报' : '查看详细战报' }}
      </a>
    </div>

    <!-- 详细战报 -->
    <div v-if="showDetail && detailLogs.length > 0">
      <div v-for="(log, idx) in detailLogs" :key="idx" class="section indent">
        {{ log }}
      </div>
    </div>

    <!-- 切磋战绩 -->
    <div class="section" v-if="battleData">
      切磋战绩:{{ winCount }}/{{ totalCount }} (胜率{{ winRate }}%)
    </div>

    <!-- 返回链接 -->
    <div class="section">
      <a class="link" @click="router.push('/arena/index')">返回前页</a>
    </div>

    <div class="section">
      <a class="link" @click="router.push('/')">返回游戏首页</a>
    </div>
  </div>
</template>

<script>
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

export default {
  name: 'ArenaStreakBattle',
  setup() {
    const router = useRouter();
    const route = useRoute();
    return { router, route };
  },
  data() {
    return {
      battleTitle: '凝神香加成无',
      attacker: { nickname: '', title: '' },
      defender: { nickname: '', title: '' },
      attackerBeasts: [],
      defenderBeasts: [],
      attackerBeastsText: '',
      battleLogs: [],
      detailLogs: [],
      battleData: null,
      showDetail: false,
      winCount: 3679,
      totalCount: 4714,
      winRate: 78.04
    };
  },
  mounted() {
    this.startBattle();
  },
  methods: {
    async startBattle() {
      const opponentId = this.route.query.opponent_id;
      if (!opponentId) {
        console.error('缺少对手信息');
        this.router.push('/arena/streak');
        return;
      }

      try {
        const res = await axios.post('/api/arena-streak/battle', {
          opponent_id: opponentId
        });

        if (res.data.ok) {
          this.battleData = res.data;
          this.parseBattleData(res.data);
        } else {
          console.error('战斗失败:', res.data.error);
          this.router.push('/arena/streak');
        }
      } catch (err) {
        console.error('战斗请求失败', err);
        this.router.push('/arena/streak');
      }
    },

    parseBattleData(data) {
      // 保存完整战报数据到 sessionStorage，然后跳转到战报页面
      const battleData = data.battle || data;
      sessionStorage.setItem('arena_streak_battle_data', JSON.stringify(battleData));
      
      // 跳转到战报页面
      this.router.push('/arena/streak/battle-report');
    },

    formatBeastsText(beasts) {
      return beasts.map(b => `${b.name}+${b.level || 0}`).join(' · ');
    },

    getBeastImage(beast) {
      // 返回幻兽图片占位符
      return '/images/beast_placeholder.png';
    }
  }
};
</script>

<style scoped>
.battle-page {
  background: #FFF8DC;
  min-height: 100vh;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.6;
  font-family: SimSun, "宋体", serif;
}

.section {
  margin: 8px 0;
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
</style>

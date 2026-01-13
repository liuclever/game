<script setup>
import { useMessage } from '@/composables/useMessage'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'

const router = useRouter()
const { message, messageType, showMessage } = useMessage()

const loading = ref(true)
const talentData = ref(null)

const fetchTalentInfo = async () => {
  loading.value = true
  try {
    const res = await http.get('/alliance/talent')
    if (res.data.ok) {
      talentData.value = res.data
    } else {
      showMessage(res.data.error || '获取天赋信息失败', 'error')
      talentData.value = null
    }
  } catch (e) {
    showMessage(e.response?.data?.error || '获取天赋信息失败', 'error')
    talentData.value = null
  } finally {
    loading.value = false
  }
}

const goBackAlliance = () => {
  router.push('/alliance')
}

const goHome = () => {
  router.push('/')
}

const goLearn = (key) => {
  router.push({ name: 'AllianceTalentLearn', params: { key } })
}

const goResearch = (key) => {
  router.push({ name: 'AllianceTalentResearch', params: { key } })
}

onMounted(() => {
  fetchTalentInfo()
})
</script>

<template>
  <div class="alliance-talent-page">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <div v-if="loading" class="section">加载中...</div>
    <template v-else-if="talentData">
      <div class="section title">天赋池能进行联盟天赋学习</div>
      <div class="section">建筑等级：{{ talentData.building_level }}级</div>
      <div class="section">个人贡献：{{ talentData.member?.contribution ?? 0 }} 点</div>

      <div class="section talent-list">
        <div
          v-for="entry in talentData.talents"
          :key="entry.key"
          class="talent-item"
        >
          <div>
            {{ entry.label }}：{{ entry.player_level }}/{{ entry.max_level }}级
            <span class="tip">(研究等级 {{ entry.research_level }}，裸属性+{{ entry.effect_percent }}%)</span>
          </div>
          <div class="cost" v-if="entry.learn_cost">
            下一次学习目标等级 {{ entry.next_level }} 级，单项消耗 {{ entry.learn_cost.per_talent }} 点贡献（六项合计 {{ entry.learn_cost.total }} 点）
          </div>
          <div class="actions">
            <template v-if="entry.can_learn">
              <a class="link" @click="goLearn(entry.key)">学习</a>
            </template>
            <span v-else class="muted">学习已满级</span>

            <template v-if="talentData.can_research">
              <span class="divider">|</span>
              <a
                class="link"
                :class="{ disabled: entry.research_level >= talentData.building_level }"
                @click="entry.research_level >= talentData.building_level ? null : goResearch(entry.key)"
              >
                研究
              </a>
              <span v-if="entry.research_cost && entry.can_research" class="cost-tip">
                (研发消耗：资金 {{ entry.research_cost.funds }}，焚火晶 {{ entry.research_cost.crystals }})
              </span>
              <span
                v-else-if="entry.research_level >= talentData.building_level"
                class="muted"
              >研究已达建筑上限</span>
            </template>
          </div>
        </div>
      </div>

      <div class="section nav-links">
        <a class="link" @click="goBackAlliance">返回联盟</a><br>
        <a class="link" @click="goHome">返回游戏首页</a>
      </div>

    </template>
    <div v-else class="section">未加入联盟或暂无数据</div>
  </div>
</template>

<style scoped>
.alliance-talent-page {
  background: #fff8dc;
  min-height: 100vh;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.8;
  font-family: SimSun, '宋体', serif;
}

.section {
  margin: 8px 0;
}

.title {
  font-weight: bold;
  font-size: 15px;
}

.talent-item {
  margin: 8px 0;
  padding: 6px 0;
  border-bottom: 1px dotted #d4c49a;
}

.actions {
  margin-top: 4px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.cost {
  color: #8b5e00;
  font-size: 12px;
}

.tip {
  color: #555;
  font-size: 12px;
  margin-left: 6px;
}

.cost-tip {
  color: #8a5c00;
  font-size: 12px;
}

.divider {
  color: #bbb;
}

.link {
  color: #0066cc;
  cursor: pointer;
  margin-left: 8px;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.link.disabled {
  pointer-events: none;
  color: #aaa;
}

.muted {
  color: #999;
  font-size: 12px;
}

.footer-info {
  margin-top: 16px;
  color: #777;
  font-size: 11px;
  border-top: 1px solid #eee;
  padding-top: 8px;
}

/* 消息提示样式 */
.message {
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  font-weight: bold;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

</style>

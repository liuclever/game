<script setup>
import { computed } from 'vue'
import BeastSelector from './BeastSelector.vue'

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  costCoins: { type: Number, required: true },
  costPills: { type: Number, required: true },
  currentCoins: { type: [Number, String], default: 0 },
  pillsCount: { type: [Number, String], default: '加载中...' },
  beasts: {
    type: Array,
    default: () => [],
  },
  loading: { type: Boolean, default: false },
  errorMsg: { type: String, default: '' },
  mainBeast: { type: Object, default: null },
  subBeast: { type: Object, default: null },
  mainBeastId: { type: [String, Number], default: '' },
  subBeastId: { type: [String, Number], default: '' },
  aptitudeKey: { type: String, default: '' },
  mainAptitude: { type: [Number, String], default: null },
  subAptitude: { type: [Number, String], default: null },
  isAptitudeValid: { type: Boolean, default: true },
  aptitudeWarning: { type: String, default: '' },
  showFooter: { type: Boolean, default: true },
  onBack: { type: Function, default: () => {} },
  onGoRefinePot: { type: Function, default: () => {} },
  onGoHome: { type: Function, default: () => {} },
  onSelectMain: { type: Function, default: null },
  onSelectSub: { type: Function, default: null },
  onChangeMain: { type: Function, default: null },
  onChangeSub: { type: Function, default: null },
  onGoShop: { type: Function, default: null },
  onGoQuest: { type: Function, default: null },
  onStartRefine: { type: Function, default: null },
})

const displayCoins = computed(() => {
  if (typeof props.currentCoins === 'number') return props.currentCoins.toLocaleString('zh-CN')
  return props.currentCoins || '加载中'
})

const displayPills = computed(() => {
  if (typeof props.pillsCount === 'number') return props.pillsCount.toLocaleString('zh-CN')
  return props.pillsCount || '加载中'
})

const displayMainBeast = computed(() => {
  if (props.mainBeast?.name) {
    const realm = props.mainBeast.realm ? `-${props.mainBeast.realm}` : ''
    return `${props.mainBeast.name}${realm}`
  }
  return '选择'
})

const displaySubBeast = computed(() => {
  if (props.subBeast?.name) {
    const realm = props.subBeast.realm ? `-${props.subBeast.realm}` : ''
    return `${props.subBeast.name}${realm}`
  }
  return '选择'
})

const coinsValue = computed(() => {
  const parsed = Number(props.currentCoins)
  if (Number.isFinite(parsed)) return parsed
  return -1
})

const pillsValue = computed(() => {
  const parsed = Number(props.pillsCount)
  if (Number.isFinite(parsed)) return parsed
  return -1
})

const hasEnoughCoins = computed(() => {
  if (props.loading) return false
  if (coinsValue.value < 0) return false
  return coinsValue.value >= props.costCoins
})

const hasEnoughPills = computed(() => {
  if (props.loading) return false
  if (pillsValue.value < 0) return false
  return pillsValue.value >= props.costPills
})

const isSelectionComplete = computed(() => Boolean(props.mainBeastId) && Boolean(props.subBeastId))

const startDisabled = computed(() => {
  return (
    props.loading ||
    !!props.errorMsg ||
    !props.isAptitudeValid ||
    !isSelectionComplete.value ||
    !hasEnoughCoins.value ||
    !hasEnoughPills.value
  )
})

const combinedWarning = computed(() => {
  const warnings = []
  if (!props.isAptitudeValid && props.aptitudeWarning) warnings.push(props.aptitudeWarning)
  if (!hasEnoughCoins.value && coinsValue.value >= 0) warnings.push('铜钱不足，请先补充所需铜钱')
  if (!hasEnoughPills.value && pillsValue.value >= 0) warnings.push('炼魂丹不足，请先补充炼魂丹')
  if (props.errorMsg) warnings.push(props.errorMsg)
  return warnings
})

const handleStart = () => {
  if (startDisabled.value) return
  props.onStartRefine && props.onStartRefine()
}

const handleGoShop = () => {
  props.onGoShop && props.onGoShop()
}

const handleGoQuest = () => {
  props.onGoQuest && props.onGoQuest()
}
</script>

<template>
  <div class="refine-aptitude-page">
    <div class="section title">
      {{ props.title }}
      <a class="link" @click.prevent="props.onBack">返回</a>
    </div>

    <div class="section indent">
      {{ props.description }}
    </div>

    <div class="section">
      <slot name="mainSlot">
        <BeastSelector
          label="主幻兽"
          :model-value="props.mainBeastId"
          :options="props.beasts"
          :loading="props.loading"
          :error="props.errorMsg"
          :disabled-ids="[props.subBeastId]"
          :aptitude-key="props.aptitudeKey"
          placeholder="请选择主幻兽"
          @update:model-value="props.onChangeMain && props.onChangeMain($event)"
        />
      </slot>
    </div>
    <div class="section indent" v-if="props.mainAptitude !== null && props.mainAptitude !== undefined">
      主幻兽资质：{{ props.mainAptitude }}
    </div>

    <div class="section">
      <slot name="subSlot">
        <BeastSelector
          label="副幻兽"
          :model-value="props.subBeastId"
          :options="props.beasts"
          :loading="props.loading"
          :error="props.errorMsg"
          :disabled-ids="[props.mainBeastId]"
          :aptitude-key="props.aptitudeKey"
          placeholder="请选择副幻兽"
          @update:model-value="props.onChangeSub && props.onChangeSub($event)"
        />
      </slot>
    </div>
    <div class="section indent" v-if="props.subAptitude !== null && props.subAptitude !== undefined">
      副幻兽资质：{{ props.subAptitude }}
    </div>

    <div class="section">
      炼妖费用:
    </div>
    <div class="section indent">
      铜钱: {{ props.costCoins.toLocaleString('zh-CN') }}
    </div>
    <div class="section indent">
      炼魂丹: {{ props.costPills }}
      <a class="link" href="javascript:void(0)" @click.prevent="handleGoShop">购买</a>
    </div>
    <div class="section indent note">
      炼魂丹可在商店直接购买，也可通过每日必做的白银/黄金礼包获得。
    </div>
    <div class="section indent">
      炼魂丹库存：{{ displayPills }}
    </div>

    <slot name="extra" />

    <div v-if="combinedWarning.length" class="section indent warn">
      <div v-for="(warning, index) in combinedWarning" :key="index">{{ warning }}</div>
      <div class="actions-inline">
        <a
          v-if="!hasEnoughCoins && coinsValue >= 0 && props.onGoShop"
          class="link"
          href="javascript:void(0)"
          @click.prevent="handleGoShop"
        >
          去商城补充
        </a>
        <a
          v-if="!hasEnoughPills && pillsValue >= 0 && props.onGoQuest"
          class="link"
          href="javascript:void(0)"
          @click.prevent="handleGoQuest"
        >
          去任务获取
        </a>
      </div>
    </div>

    <div class="section action">
      <a
        class="link start-link"
        :class="{ disabled: startDisabled }"
        href="javascript:void(0)"
        @click.prevent="handleStart"
      >
        开始炼妖
      </a>
    </div>

    <div class="section">
      当前铜钱: {{ displayCoins }}
    </div>

    <div class="section">
      <a class="link" @click.prevent="props.onGoRefinePot">返回炼妖壶</a>
    </div>
    <div class="section">
      <a class="link" @click.prevent="props.onGoHome">返回游戏首页</a>
    </div>

  </div>
</template>

<style scoped>
.refine-aptitude-page {
  background: #fff8dc;
  min-height: 100vh;
  font-family: SimSun, '宋体', serif;
  font-size: 13px;
  line-height: 1.6;
  padding: 8px 12px 40px;
  color: #000;
}

.section {
  margin: 2px 0;
}

.title {
  font-weight: bold;
}

.indent {
  padding-left: 8px;
}

.note {
  font-size: 12px;
  color: #333;
}

.link {
  color: #0066cc;
  text-decoration: none;
  cursor: pointer;
}

.link:hover {
  text-decoration: underline;
}

.link.blue {
  color: #003c99;
}

.start-link.disabled {
  color: #999;
  pointer-events: none;
  text-decoration: none;
}

.action {
  margin: 8px 0;
}

.warn {
  color: #c05432;
}

.actions-inline {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.footer {
  margin-top: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
  color: #333;
}
</style>

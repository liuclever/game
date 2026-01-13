<script setup>
import { useMessage } from '@/composables/useMessage'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/services/http'
import RefinePotAptitudeTemplate from './components/RefinePotAptitudeTemplate.vue'
import { aptitudeCosts } from './constants/aptitudeCosts'
import { useRefinePotData } from './hooks/useRefinePotData'

const router = useRouter()
const cost = aptitudeCosts.magic
const aptitudeKey = 'magic_atk_aptitude'

const {
  loading,
  errorMsg,
  currentCoins,
  pillsCount,
  beasts,
  mainBeastId,
  subBeastId,
  selectedMain,
  selectedSub,
  setMainBeast,
  setSubBeast,
  getAptitudeValue,
  reload,
} = useRefinePotData()

const mainAptitude = computed(() => getAptitudeValue(selectedMain.value, aptitudeKey))
const subAptitude = computed(() => getAptitudeValue(selectedSub.value, aptitudeKey))

const isAptitudeValid = computed(() => {
  if (!mainBeastId.value || !subBeastId.value) return true
  return subAptitude.value > mainAptitude.value
})

const aptitudeWarning = computed(() => {
  if (!isAptitudeValid.value) return '副幻兽法攻资质需高于主幻兽'
  return ''
})

const goBack = () => {
  router.push('/refine-pot/refine')
}

const goHome = () => {
  router.push('/')
}

const goRefinePot = () => {
  router.push('/refine-pot')
}

const goShop = () => {
  router.push('/shop')
}

const goQuest = () => {
  router.push('/tasks/daily')
}

const handleChangeMain = (value) => {
  setMainBeast(value)
}

const handleChangeSub = (value) => {
  setSubBeast(value)
}

const handleStartRefine = async () => {
  if (!isAptitudeValid.value) return
  try {
    const res = await http.post('/refine-pot/refine', {
      main_beast_id: mainBeastId.value,
      material_beast_id: subBeastId.value,
      attr_type: aptitudeKey,
    })
    if (!res.data?.ok) {
      showMessage(res.data?.error || '炼妖失败', 'error')
      return
    }
    const { data } = res.data
    showMessage(`成功！主幻兽资质 +${data?.delta ?? 0}，新值 ${data?.after ?? '未知'}`, 'success')
    await reload()
  } catch (err) {
    const message = err?.response?.data?.error || err?.message || '网络异常，请重试'
    showMessage(message, 'info')
  }
}
</script>

<template>
  <RefinePotAptitudeTemplate
    title="【炼妖壶-法攻资质炼妖】"
    description="对主幻兽进行法攻资质炼化，副幻兽法攻资质越高效果越好"
    :cost-coins="cost.coins"
    :cost-pills="cost.pills"
    :current-coins="currentCoins"
    :pills-count="pillsCount"
    :beasts="beasts"
    :loading="loading"
    :error-msg="errorMsg"
    :main-beast="selectedMain"
    :sub-beast="selectedSub"
    :main-beast-id="mainBeastId"
    :sub-beast-id="subBeastId"
    :main-aptitude="mainAptitude"
    :sub-aptitude="subAptitude"
    :aptitude-key="aptitudeKey"
    :is-aptitude-valid="isAptitudeValid"
    :aptitude-warning="aptitudeWarning"
    :on-change-main="handleChangeMain"
    :on-change-sub="handleChangeSub"
    :on-back="goBack"
    :on-go-refine-pot="goRefinePot"
    :on-go-home="goHome"
    :on-go-shop="goShop"
    :on-go-quest="goQuest"
    :on-start-refine="handleStartRefine"
  >
    <template #extra>
      <div v-if="loading" class="section indent">数据加载中...</div>
    </template>
  </RefinePotAptitudeTemplate>
</template>

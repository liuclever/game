import { ref, onMounted, watch } from 'vue'
import http from '@/services/http'

export function useRefinePotData() {
  const loading = ref(false)
  const errorMsg = ref('')
  const currentCoins = ref('加载中')
  const pillsCount = ref('加载中')
  const beasts = ref([])
  const mainBeastId = ref('')
  const subBeastId = ref('')
  const selectedMain = ref(null)
  const selectedSub = ref(null)

  const fetchPlayerInfo = async () => {
    try {
      const res = await http.get('/player/info')
      if (res.data?.ok) {
        currentCoins.value = res.data.player?.gold ?? 0
      } else {
        currentCoins.value = '加载失败'
      }
    } catch (err) {
      console.error('加载玩家信息失败:', err)
      currentCoins.value = '加载失败'
      throw err
    }
  }

  const fetchBeasts = async () => {
    try {
      const res = await http.get('/beast/list')
      if (res.data?.ok) {
        beasts.value = res.data.beastList || res.data.beasts || []
      } else {
        beasts.value = []
        throw new Error(res.data?.error || '加载幻兽列表失败')
      }
    } catch (err) {
      console.error('加载幻兽列表失败:', err)
      beasts.value = []
      throw err
    }
  }

  const fetchPillsCount = async () => {
    try {
      const res = await http.get('/inventory/item-count', { params: { item_id: 6028 } })
      if (res.data?.ok) {
        pillsCount.value = res.data.count ?? 0
      } else {
        pillsCount.value = '暂未接入，请联系后端'
      }
    } catch (err) {
      console.warn('加载炼魂丹库存失败，可能接口未实现:', err)
      pillsCount.value = '暂未接入，请联系后端'
    }
  }

  const loadAll = async () => {
    loading.value = true
    errorMsg.value = ''
    try {
      await Promise.all([fetchPlayerInfo(), fetchBeasts(), fetchPillsCount()])
    } catch (err) {
      errorMsg.value = '部分数据加载失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    loadAll()
  })

  const resolveBeastById = (id) => {
    if (!id) return null
    return beasts.value.find((beast) => String(beast.id) === String(id)) || null
  }

  const formatBeastLabel = (beast) => {
    if (!beast) return '未知幻兽'
    return `${beast.name}${beast.realm ? `-${beast.realm}` : ''}`
  }

  watch([mainBeastId, beasts], () => {
    selectedMain.value = resolveBeastById(mainBeastId.value)
  })

  watch([subBeastId, beasts], () => {
    selectedSub.value = resolveBeastById(subBeastId.value)
  })

  const setMainBeast = (id) => {
    mainBeastId.value = id || ''
  }

  const setSubBeast = (id) => {
    subBeastId.value = id || ''
  }

  const normalizeKeyVariants = (key) => {
    if (!key) return []
    const base = key.toString()
    const camel = base.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
    const snake = base.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`).replace(/^_/, '')
    const upper = base.toUpperCase()
    const lower = base.toLowerCase()
    return Array.from(new Set([base, camel, snake, upper, lower]))
  }

  const getAptitudeValue = (beast, aptitudeKey) => {
    if (!beast || !aptitudeKey) return 0
    const candidates = normalizeKeyVariants(aptitudeKey)
    const sources = [beast?.aptitude, beast?.aptitudes, beast?.attrs, beast]
    for (const source of sources) {
      if (!source) continue
      for (const key of candidates) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          const raw = source[key]
          const parsed = Number(raw)
          if (!Number.isNaN(parsed)) return parsed
        }
      }
    }
    return 0
  }

  return {
    loading,
    errorMsg,
    currentCoins,
    pillsCount,
    beasts,
    mainBeastId,
    subBeastId,
    selectedMain,
    selectedSub,
    formatBeastLabel,
    setMainBeast,
    setSubBeast,
    getAptitudeValue,
    reload: loadAll,
  }
}

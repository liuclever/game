<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '幻兽' },
  modelValue: { type: [String, Number], default: '' },
  placeholder: { type: String, default: '请选择' },
  aptitudeKey: { type: String, default: '' },
  disabledIds: {
    type: Array,
    default: () => [],
  },
  options: {
    type: Array,
    default: () => [],
  },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const disabledIdSet = computed(() =>
  new Set((props.disabledIds || []).map((item) => String(item ?? '')))
)

const hasOptions = computed(() => Array.isArray(props.options) && props.options.length > 0)

const isLoading = computed(() => props.loading)
const errorMessage = computed(() => props.error)

const normalizeKeyVariants = (key) => {
  if (!key) return []
  const base = key.toString()
  const camel = base.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
  const snake = base.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`).replace(/^_/, '')
  const upper = base.toUpperCase()
  const lower = base.toLowerCase()
  return Array.from(new Set([base, camel, snake, upper, lower]))
}

const getAptitudeValue = (beast) => {
  if (!beast || !props.aptitudeKey) return ''
  const candidates = normalizeKeyVariants(props.aptitudeKey)
  const sources = [beast?.aptitude, beast?.aptitudes, beast?.attrs, beast]
  for (const source of sources) {
    if (!source) continue
    for (const key of candidates) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        const parsed = Number(source[key])
        if (!Number.isNaN(parsed)) return parsed
      }
    }
  }
  return ''
}

const formatOptionLabel = (beast) => {
  if (!beast) return '未知幻兽'
  const name = beast.name || '未知幻兽'
  const realm = beast.realm ? `-${beast.realm}` : ''
  const aptitude = getAptitudeValue(beast)
  if (aptitude !== '' && aptitude !== undefined) {
    return `${name}${realm}（资质${aptitude}）`
  }
  return `${name}${realm}`
}

const handleChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="beast-selector">
    <div class="label">[{{ label }}]</div>
    <select
      class="selector"
      :value="modelValue"
      @change="handleChange"
      :disabled="isLoading"
    >
      <option value="">{{ placeholder }}</option>
      <option
        v-for="beast in options"
        :key="beast.id"
        :value="beast.id"
        :disabled="disabledIdSet.has(String(beast.id))"
      >
        {{ formatOptionLabel(beast) }}
      </option>
    </select>

    <div v-if="isLoading" class="hint">幻兽列表加载中...</div>
    <div v-else-if="errorMessage" class="hint warn">{{ errorMessage }}</div>
    <div v-else-if="!hasOptions" class="hint">暂无可用幻兽</div>
  </div>
</template>

<style scoped>
.beast-selector {
  display: inline-flex;
  flex-direction: column;
  font-family: SimSun, '宋体', serif;
  font-size: 16px;
  color: #000;
}

.label {
  margin-bottom: 4px;
}

.selector {
  min-width: 160px;
  font-size: 16px;
}

.hint {
  margin-top: 4px;
  color: #555;
}

.hint.warn {
  color: #c05432;
}
</style>

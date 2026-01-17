/**
 * 战报分页组合式函数
 * 用于所有战报页面的分页功能
 */
import { ref, computed } from 'vue'

export function useBattleReportPagination(rounds, roundsPerPage = 10) {
  const currentPage = ref(1)

  // 总页数
  const totalPages = computed(() => {
    const total = rounds.value?.length || 0
    return Math.max(1, Math.ceil(total / roundsPerPage))
  })

  // 当前页的回合
  const currentRounds = computed(() => {
    if (!rounds.value) return []
    const start = (currentPage.value - 1) * roundsPerPage
    const end = start + roundsPerPage
    return rounds.value.slice(start, end)
  })

  // 是否有上一页
  const hasPrevPage = computed(() => currentPage.value > 1)

  // 是否有下一页
  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  // 上一页
  const prevPage = () => {
    if (hasPrevPage.value) {
      currentPage.value--
    }
  }

  // 下一页
  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  // 跳转到指定页
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  // 重置到第一页
  const resetPage = () => {
    currentPage.value = 1
  }

  return {
    currentPage,
    totalPages,
    currentRounds,
    hasPrevPage,
    hasNextPage,
    prevPage,
    nextPage,
    goToPage,
    resetPage,
  }
}

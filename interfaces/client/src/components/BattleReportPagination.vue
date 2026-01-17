<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
  hasPrevPage: {
    type: Boolean,
    required: true,
  },
  hasNextPage: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['prev', 'next', 'goto'])

// 显示的页码列表（最多显示10个页码）
const pageNumbers = computed(() => {
  const total = props.totalPages
  const current = props.currentPage
  const pages = []

  if (total <= 10) {
    // 总页数<=10，显示所有页码
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // 总页数>10，显示部分页码
    if (current <= 5) {
      // 当前页在前5页
      for (let i = 1; i <= 7; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 4) {
      // 当前页在后5页
      pages.push(1)
      pages.push('...')
      for (let i = total - 6; i <= total; i++) {
        pages.push(i)
      }
    } else {
      // 当前页在中间
      pages.push(1)
      pages.push('...')
      for (let i = current - 2; i <= current + 2; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }

  return pages
})

const handlePrev = () => {
  emit('prev')
}

const handleNext = () => {
  emit('next')
}

const handleGoto = (page) => {
  if (typeof page === 'number') {
    emit('goto', page)
  }
}
</script>

<template>
  <div class="pagination">
    <a v-if="hasPrevPage" class="link" @click="handlePrev">上一页</a>
    <span v-else class="gray">上一页</span>
    <span class="page-info">第{{ currentPage }}/{{ totalPages }}页</span>
    <a v-if="hasNextPage" class="link" @click="handleNext">下一页</a>
    <span v-else class="gray">下一页</span>
  </div>

  <!-- 页码快速跳转 -->
  <div class="page-numbers">
    跳转到：
    <template v-for="(page, index) in pageNumbers" :key="index">
      <span v-if="page === '...'" class="ellipsis">...</span>
      <a 
        v-else-if="page !== currentPage" 
        class="link page-num" 
        @click="handleGoto(page)"
      >{{ page }}</a>
      <span v-else class="current-page">{{ page }}</span>
    </template>
  </div>
</template>

<style scoped>
.pagination {
  margin: 12px 0;
  padding: 8px 0;
  border-top: 1px solid #EEEEEE;
  border-bottom: 1px solid #EEEEEE;
}

.page-info {
  margin: 0 12px;
  color: #333333;
}

.page-numbers {
  margin: 8px 0;
}

.page-num {
  margin: 0 4px;
}

.current-page {
  margin: 0 4px;
  color: #CC3300;
  font-weight: bold;
}

.ellipsis {
  margin: 0 4px;
  color: #999999;
}

.link {
  color: #0066CC;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.gray {
  color: #999999;
}
</style>

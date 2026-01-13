<template>
  <div class="manor-page p-4 bg-[#fdf5d6] min-h-screen font-sans text-sm">
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- Header -->
    <div class="mb-4">
      <div class="text-lg font-bold mb-2">
        【庄园】 <span class="text-blue-600 cursor-pointer">简介</span>
      </div>
      <div class="mb-2 text-gray-800">风水:青山绿水</div>
        <div class="flex items-center gap-2">
          <span>[{{ normalLandCount }}块庄园土地]</span>
          <router-link to="/manor/expand" class="text-blue-600 underline cursor-pointer">
            扩建
          </router-link>
        </div>
      </div>

        <!-- Land List -->
        <div v-if="loading" class="py-4 text-gray-500">加载中...</div>
        <div v-else class="grid grid-cols-1 mb-8 leading-relaxed">
          <div 
            v-for="(land, index) in displayLands" 
            :key="index" 
            class="flex items-center"
          >
            <span>{{ index + 1 }}. {{ getLandName(land) }}</span>
            
            <template v-if="land.status === 0">
              <router-link 
                :to="`/manor/expand?land_index=${land.land_index}`"
                class="text-blue-600 underline cursor-pointer ml-1"
              >
                开启
              </router-link>
            </template>
            
            <template v-else-if="land.status === 1">
              <router-link 
                :to="`/manor/plant?land_index=${land.land_index}`"
                class="text-blue-600 underline cursor-pointer"
              >
                种植
              </router-link>
            </template>

            <template v-else-if="land.is_mature">
              <span 
                class="harvest-button"
                @click="handleHarvest"
              >
                收获
              </span>
            </template>

            <template v-else>
              <span class="ml-1">
                {{ getTreeTypeName(land.tree_type) }} {{ formatRemainingTime(land.remaining_seconds) }}
              </span>
            </template>
        </div>
      </div>


    <!-- Navigation Footer -->
    <div class="mt-8 border-t border-gray-300 pt-4">
      <router-link 
        to="/main" 
        class="text-blue-600 cursor-pointer text-base hover:underline no-underline"
      >
        返回游戏首页
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface Land {
  land_index: number;
  status: number;
  tree_type: number;
  remaining_seconds: number;
  is_mature: boolean;
}

const lands = ref<Land[]>([]);
const { message, messageType, showMessage } = useMessage()

const loading = ref(true);

// 计算普通土地数量（用于显示）
const normalLandCount = computed(() => {
  return lands.value.filter(l => l.land_index >= 0 && l.land_index <= 9).length;
});

const displayLands = computed(() => {
  const result: Land[] = [];
  
  // 1. 先处理普通土地（空土地）：land_index 0-9
  const normalLands = lands.value.filter(l => l.land_index >= 0 && l.land_index <= 9);
  
  // 只有当玩家至少拥有1块普通土地时，才显示空土地
  if (normalLandCount.value > 0) {
    for (let i = 0; i < normalLandCount.value; i++) {
      const existing = normalLands.find(l => l.land_index === i);
      if (existing) {
        result.push(existing);
      } else {
        // 如果数据库中没有该索引的土地，创建默认的未开启状态
        result.push({
          land_index: i,
          status: 0,
          tree_type: 0,
          remaining_seconds: 0,
          is_mature: false
        });
      }
    }
  }
  
  // 2. 固定显示特殊土地：黄土地(10)、银土地(11)、金土地(12)
  const specialLandIndices = [10, 11, 12];
  
  specialLandIndices.forEach((landIndex) => {
    const existing = lands.value.find(l => l.land_index === landIndex);
    if (existing) {
      result.push(existing);
    } else {
      // 即使玩家没有拥有，也显示为未开启状态
      result.push({
        land_index: landIndex,
        status: 0,
        tree_type: 0,
        remaining_seconds: 0,
        is_mature: false
      });
    }
  });
  
  return result;
});

const fetchStatus = async () => {
  try {
    const res = await fetch('/api/manor/status');
    const data = await res.json();
    if (data.ok) {
      lands.value = data.lands || [];
    }
  } catch (error) {
    console.error('Failed to fetch manor status:', error);
  } finally {
    loading.value = false;
  }
};

const getLandName = (land: Land) => {
  // 特殊土地
  if (land.land_index === 10) return '黄土地(5%加成)';
  if (land.land_index === 11) return '银土地(10%加成)';
  if (land.land_index === 12) return '金土地(20%加成)';
  
  // 普通土地（空土地）
  if (land.land_index >= 0 && land.land_index <= 9) {
    return '空土地';
  }
  
  return '普通土地';
};

const getTreeTypeName = (treeType: number) => {
  const treeNames: Record<number, string> = {
    1: '单株摇钱树',
    2: '双株摇钱树',
    4: '四株摇钱树',
    6: '六株摇钱树',
    8: '八株摇钱树',
  };
  return treeNames[treeType] || '未知品种';
};

const formatRemainingTime = (remainingSeconds: number) => {
  if (remainingSeconds <= 0) {
    return '已成熟';
  }
  
  const hours = Math.floor(remainingSeconds / 3600);
  const minutes = Math.floor((remainingSeconds % 3600) / 60);
  
  if (hours > 0 && minutes > 0) {
    return `${hours}小时${minutes}分钟`;
  } else if (hours > 0) {
    return `${hours}小时`;
  } else if (minutes > 0) {
    return `${minutes}分钟`;
  } else {
    return '即将成熟';
  }
};

const getActionText = (land: Land) => {
  if (land.status === 0) return '开启';
  if (land.status === 1) return '种植';
  if (land.is_mature) return '收获';
  return '详情';
};

const getStatusClass = (land: Land) => {
  return 'text-blue-600';
};

const handleHarvest = async () => {
  try {
    const res = await fetch('/api/manor/harvest', { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showMessage(data.message, 'success');
      fetchStatus();
    } else {
      showMessage(data.error || data.message || '收获失败', 'error');
    }
  } catch (error) {
    console.error('Failed to harvest:', error);
  }
};

onMounted(() => {
  fetchStatus();
});
</script>

<style scoped>
.manor-page {
  max-width: 600px;
}

.harvest-button {
  color: #2563eb !important;
  text-decoration: underline !important;
  cursor: pointer;
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

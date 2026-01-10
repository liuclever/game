<template>
  <div class="manor-plant-page p-4 bg-[#fdf5d6] min-h-screen font-sans text-sm leading-relaxed">
    <!-- Header -->
    <div v-if="!showConfirm" class="mb-4">
      <div class="font-bold border-b border-gray-400 pb-1 mb-2">
        种子|价格|操作.
      </div>
    </div>

    <!-- Seed List -->
    <div v-if="!showConfirm" class="seed-list space-y-1">
      <div 
        v-for="(seed, index) in seeds" 
        :key="index"
        class="flex items-center"
      >
        <span class="text-blue-700">{{ seed.name }}</span>
        <span class="mx-1">|</span>
        <span :class="seed.price === '免费' ? 'text-black' : 'text-blue-700'">{{ seed.price }}</span>
        <span class="mx-1">|</span>
        <span 
          class="plant-button"
          @click="handlePlant(seed)"
        >
          种植
        </span>
        <span class="mx-1">.</span>
        <span 
          class="plant-button"
          @click="handleQuickPlant(seed)"
        >
          一键
        </span>
      </div>
    </div>

    <!-- Confirm Plant Info -->
    <div v-if="showConfirm" class="confirm-section space-y-2">
      <div>确认种植{{ selectedSeed?.name }}?</div>
      <div>种植后6小时恢复</div>
      <div class="mt-4 space-y-2">
        <div>
          <span 
            class="plant-button"
            @click="confirmPlant"
          >
            确认种植
          </span>
        </div>
        <div>
          <router-link to="/manor" class="text-blue-600 underline cursor-pointer text-base">
            返回庄园
          </router-link>
        </div>
        <div>
          <router-link to="/main" class="text-blue-600 underline cursor-pointer text-base">
            返回游戏首页
          </router-link>
        </div>
      </div>
    </div>

    <!-- Navigation Footer -->
    <div v-if="!showConfirm" class="mt-6 space-y-2 border-t border-gray-300 pt-4">
      <div>
        <router-link to="/manor" class="text-blue-600 underline cursor-pointer text-base">
          返回庄园
        </router-link>
      </div>
      <div>
        <router-link to="/main" class="text-blue-600 underline cursor-pointer text-base">
          返回游戏首页
        </router-link>
      </div>
    </div>


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

interface Land {
  land_index: number;
  status: number;
  tree_type: number;
  remaining_seconds: number;
  is_mature: boolean;
}

const router = useRouter();
const route = useRoute();
const showConfirm = ref(false);
const selectedSeed = ref<any>(null);
const landIndex = ref<number | null>(null);
const availableLands = ref<Land[]>([]);

const seeds = [
  // 摇钱树
  { name: '单株摇钱树', price: '10元宝', type: 'money', count: 1 },
  { name: '双株摇钱树', price: '60元宝', type: 'money', count: 2 },
  { name: '四株摇钱树', price: '80元宝', type: 'money', count: 4 },
  { name: '六株摇钱树', price: '100元宝', type: 'money', count: 6 },
  { name: '八株摇钱树', price: '120元宝', type: 'money', count: 8 },
];


const handlePlant = (seed: any) => {
  selectedSeed.value = seed;
  showConfirm.value = true;
};

const fetchAvailableLands = async () => {
  try {
    const res = await fetch('/api/manor/status');
    const data = await res.json();
    if (data.ok) {
      const lands = data.lands || [];
      // 筛选空闲土地（status === 1）
      availableLands.value = lands.filter((l: any) => l.status === 1);
    }
  } catch (error) {
    console.error('Failed to fetch available lands:', error);
  }
};

const confirmPlant = async () => {
  if (!selectedSeed.value || landIndex.value === null) {
    alert('参数错误');
    return;
  }
  
  // 将 count 映射到 tree_type
  const treeType = selectedSeed.value.count;
  
  try {
    const res = await fetch('/api/manor/plant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        land_indices: [landIndex.value],
        tree_type: treeType
      })
    });
    const data = await res.json();
    if (data.ok) {
      alert(data.message || '种植成功');
      router.push('/manor');  // 返回庄园页面
    } else {
      alert(data.error || data.message || '种植失败');
    }
  } catch (error) {
    console.error('Plant failed:', error);
    alert('请求失败，请稍后重试');
  }
};

const handleQuickPlant = async (seed: any) => {
  // 先获取最新的空闲土地列表
  await fetchAvailableLands();
  
  if (availableLands.value.length === 0) {
    alert('没有可种植的空闲土地');
    return;
  }
  
  // 将 count 映射到 tree_type
  const treeType = seed.count;
  const allLandIndices = availableLands.value.map(l => l.land_index);
  
  try {
    const res = await fetch('/api/manor/plant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        land_indices: allLandIndices,
        tree_type: treeType
      })
    });
    const data = await res.json();
    if (data.ok) {
      alert(data.message || '一键种植成功');
      router.push('/manor');  // 返回庄园页面
    } else {
      alert(data.error || data.message || '一键种植失败');
    }
  } catch (error) {
    console.error('Quick plant failed:', error);
    alert('请求失败，请稍后重试');
  }
};

onMounted(() => {
  // 从路由参数获取 land_index
  const landIndexParam = route.query.land_index;
  if (landIndexParam) {
    landIndex.value = parseInt(landIndexParam as string, 10);
  } else {
    alert('缺少土地参数');
    router.push('/manor');
    return;
  }
  // 获取空闲土地列表（用于一键种植功能）
  fetchAvailableLands();
});
</script>

<style scoped>
.manor-plant-page {
  max-width: 600px;
}

.plant-button {
  color: #2563eb !important;
  text-decoration: underline !important;
  cursor: pointer;
  font-size: 1rem;
}
</style>

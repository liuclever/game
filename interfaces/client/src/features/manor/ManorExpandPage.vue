<template>
  <div class="manor-expand-page p-2 bg-[#fdf5d6] min-h-screen font-sans text-sm sm:text-base leading-tight">
    <!-- Header -->
    <div>【庄园】 简介</div>
    <div v-if="isSpecialLand && landConfig">
      开启{{ landConfig.name }},能获得更高收益.
    </div>
    <div v-else>
      扩建第{{ normalLandCount + 1 }}块土地,能获得更高收益.
    </div>
    
    <!-- Requirements -->
    <template v-if="isSpecialLand">
      <div>
        庄园建造手册×{{ requiredManuals }}({{ itemSatisfied ? '满足' : '不满足' }})
        <router-link to="/shop" class="text-blue-700 ml-1">购买</router-link>
      </div>
      <div>
        VIP等级:VIP{{ requiredVip }}({{ vipSatisfied ? '满足' : '不满足' }})
      </div>
    </template>
    <template v-else>
      <div>
        建造需要:人物等级{{ toChineseStar(requiredStar) }}星召唤师({{ levelSatisfied ? '满足' : '不满足' }})
      </div>
      <div>
        庄园建造手册×{{ requiredManuals }}({{ itemSatisfied ? '满足' : '不满足' }})
        <router-link to="/shop" class="text-blue-700 ml-1">购买</router-link>
      </div>
    </template>

    <!-- Actions -->
    <div class="mt-2 space-y-0">
      <div>
<a class="link-text" @click="handleExpand">确认扩建</a>
</div>
      <div>
        <router-link to="/manor" class="text-blue-700">
          返回庄园
        </router-link>
      </div>
      <div>
        <router-link to="/main" class="text-blue-700">
          返回游戏首页
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="fixed inset-0 bg-black/5 flex items-center justify-center pointer-events-none">
      <div class="bg-white/80 p-2 text-xs">加载中...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const lands = ref<any[]>([]);
const playerLevel = ref(0);
const playerVipLevel = ref(0);
const manualCount = ref(0);
const landIndex = ref<number | null>(null);

const MANUAL_ID = 6029;

// 特殊土地配置（与后端保持一致）
const SPECIAL_LAND_CONFIG: Record<number, { vip: number; manuals: number; name: string }> = {
  10: { vip: 4, manuals: 2, name: '黄土地' },
  11: { vip: 6, manuals: 3, name: '银土地' },
  12: { vip: 8, manuals: 4, name: '金土地' },
};

const isSpecialLand = computed(() => landIndex.value !== null && landIndex.value in SPECIAL_LAND_CONFIG);
const landConfig = computed(() => {
  if (isSpecialLand.value && landIndex.value !== null) {
    return SPECIAL_LAND_CONFIG[landIndex.value];
  }
  return null;
});

const normalLandCount = computed(() => {
  return lands.value.filter((l: any) => l?.land_index >= 0 && l?.land_index <= 9).length;
});

const nextLandIndex = computed(() => {
  if (landIndex.value !== null) {
    return landIndex.value;
  }
  return normalLandCount.value;
});

const requiredLevel = computed(() => {
  if (isSpecialLand.value) return 0;
  return (nextLandIndex.value + 1) * 10;
});

const requiredStar = computed(() => {
  if (isSpecialLand.value) return 0;
  return nextLandIndex.value + 1;
});

const requiredManuals = computed(() => {
  if (isSpecialLand.value && landConfig.value) {
    return landConfig.value.manuals;
  }
  return nextLandIndex.value + 1;
});

const requiredVip = computed(() => {
  if (isSpecialLand.value && landConfig.value) {
    return landConfig.value.vip;
  }
  return 0;
});

const levelSatisfied = computed(() => {
  if (isSpecialLand.value) return true;
  return playerLevel.value >= requiredLevel.value;
});

const vipSatisfied = computed(() => {
  if (!isSpecialLand.value) return true;
  return playerVipLevel.value >= requiredVip.value;
});

const itemSatisfied = computed(() => manualCount.value >= requiredManuals.value);

const toChineseStar = (num: number) => {
  const dict: Record<number, string> = {
    1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
    6: '六', 7: '七', 8: '八', 9: '九', 10: '十'
  };
  return dict[num] || num.toString();
};

const fetchData = async () => {
  loading.value = true;
  try {
    const [manorRes, profileRes, invRes] = await Promise.all([
      fetch('/api/manor/status').then(r => r.json()),
      fetch('/api/player/info').then(r => r.json()),
      fetch('/api/inventory/list').then(r => r.json())
    ]);

    if (manorRes.ok) lands.value = manorRes.lands || [];
    if (profileRes.ok) {
      playerLevel.value = profileRes.player?.level || 0;
      playerVipLevel.value = profileRes.player?.vip_level || 0;
    }
    if (invRes.ok) {
      const items = invRes.items || [];
      manualCount.value = items
        .filter((it: any) => it.item_id === MANUAL_ID)
        .reduce((sum: number, it: any) => sum + (it.quantity || 0), 0);
    }

  } catch (error) {
    console.error('Failed to fetch data:', error);
  } finally {
    loading.value = false;
  }
};

const handleExpand = async () => {
  if (!isSpecialLand.value && nextLandIndex.value >= 10) {
    console.error('普通土地最多10块，无法继续扩建');
    return;
  }
  if (!levelSatisfied.value) {
    console.error(`等级不足，需要${toChineseStar(requiredStar.value)}星召唤师（${requiredLevel.value}级）`);
    return;
  }
  if (!itemSatisfied.value) {
    console.error(`道具不足，需要庄园建造手册×${requiredManuals.value}`);
    return;
  }
  if (isSpecialLand.value && !vipSatisfied.value) {
    console.error(`VIP等级不足，需要VIP ${requiredVip.value}`);
    return;
  }

  loading.value = true;
  try {
    const res = await fetch('/api/manor/expand', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ land_index: nextLandIndex.value })
    });
    const data = await res.json();
    if (data.ok) {
      console.error('扩建成功！');
      router.push('/manor');
    } else {
      console.error(data.message || '扩建失败');
    }
  } catch (error) {
    console.error('Failed to expand:', error);
    console.error('请求失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // 从路由参数获取 land_index
  const landIndexParam = route.query.land_index;
  if (landIndexParam) {
    landIndex.value = parseInt(landIndexParam as string, 10);
  }
  fetchData();
});
</script>

<style scoped>
.manor-expand-page {
  max-width: 100%;
}
.link-text {
  color: #0000EE; /* 标准链接蓝 */
  text-decoration: underline;
  cursor: pointer;
}

</style>

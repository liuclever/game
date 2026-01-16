<script setup>
import { ref } from 'vue'

// 地图数据（后续可从后端获取）
const mapRegions = ref([
  { id: 1, name: "林中空地", level_range: "1-9级", sub_maps: ["森林入口(1-2级)", "宁静之森(3-5级)", "森林秘境(6-9级)"], drops: "各类结晶、铜钱和经验" },
  { id: 2, name: "幻灵镇", level_range: "10-19级", sub_maps: ["呼啸平原(10-14级)", "天罚山(15-19级)"], drops: "各类结晶、铜钱和经验、碎空骨魂" },
  { id: 3, name: "定老城", level_range: "20-29级", sub_maps: ["石工矿场(20-24级)", "幻灵湖畔(25-29级)"], drops: "各类结晶、铜钱和经验、黄阶进化石、猎魔骨魂" },
  { id: 4, name: "迷雾城", level_range: "30-39级", sub_maps: ["回音之谷(30-34级)", "死亡沼泽(35-39级)"], drops: "各类结晶、铜钱和经验、玄阶进化石、龙炎骨魂" },
  { id: 5, name: "飞龙港", level_range: "40-49级", sub_maps: ["日落海峡(40-44级)", "聚灵孤岛(45-49级)"], drops: "各类结晶、铜钱和经验、地阶进化石、奔雷骨魂" },
  { id: 6, name: "落龙镇", level_range: "50-59级", sub_maps: ["龙骨墓地(50-54级)", "巨龙冰原(55-59级)"], drops: "各类结晶、铜钱和经验、天阶进化石、凌霄骨魂" },
  { id: 7, name: "圣龙城", level_range: "60-69级", sub_maps: ["圣龙城郊(60-64级)", "皇城迷宫(65-69级)"], drops: "各类结晶、铜钱和经验、飞马进化石、麒麟/武神骨魂" },
  { id: 8, name: "乌托邦", level_range: "70级以上", sub_maps: ["梦幻海湾(70-74级)", "幻光公园(75级+)"], drops: "各类结晶、铜钱和经验、天龙进化石、弑天/毁灭骨魂" },
])

const expandedId = ref(null)

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}
</script>

<template>
  <div class="panel">
    <div class="title">【地图列表】</div>
    
    <div 
      v-for="region in mapRegions" 
      :key="region.id" 
      class="region"
    >
      <div class="region-header" @click="toggleExpand(region.id)">
        <span class="arrow">{{ expandedId === region.id ? '▼' : '▶' }}</span>
        <span class="name">{{ region.name }}</span>
        <span class="level">({{ region.level_range }})</span>
        <span class="link">进入</span>
      </div>
      
      <div v-if="expandedId === region.id" class="region-detail">
        <div class="sub-maps">
          └ {{ region.sub_maps.join(' | ') }}
        </div>
        <div class="drops">产出：{{ region.drops }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel {
  border: 1px solid #dddddd;
  padding: 4px 8px;
  max-height: 300px;
  overflow-y: auto;
}

.title {
  margin-bottom: 6px;
  font-weight: bold;
}

.region {
  margin-bottom: 4px;
}

.region-header {
  cursor: pointer;
  padding: 2px 0;
}

.region-header:hover {
  background: #ffffff;
}

.arrow {
  font-size: 10px;
  margin-right: 4px;
  color: #666;
}

.name {
  color: #0033cc;
  font-weight: bold;
}

.level {
  color: #666;
  margin-left: 4px;
}

.link {
  color: #0033cc;
  cursor: pointer;
  margin-left: 8px;
}

.region-detail {
  margin-left: 16px;
  padding: 4px 0;
  font-size: 17px;
  color: #555;
}

.sub-maps {
  margin-bottom: 2px;
}

.drops {
  color: #996600;
}
</style>

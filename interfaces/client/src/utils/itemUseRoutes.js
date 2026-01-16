/**
 * 道具ID到使用路由的映射配置
 * 当道具需要跳转到特定界面使用时，在这里配置
 */
export const ITEM_USE_ROUTES = {
  // 喇叭 - 跳转到世界聊天
  4004: '/world-chat',
  6012: '/world-chat',
  
  // 捕捉球 - 跳转到地图界面（需要先选择副本）
  4002: '/map',  // 捕捉球
  4003: '/map',  // 强力捕捉球
  
  // 镇妖符 - 跳转镇妖
  6001: '/tower/zhenyao',

  // 迷踪符 / 传送符 / 双倍卡 - 地图副本相关
  6002: '/map',
  6018: '/map',
  6024: '/map',

  // 化仙丹 - 化仙池
  6015: '/huaxian',

  // 追魂法宝 - 魔魂猎魂
  6019: '/mosoul/hunting',

  // 背包升级材料 - 跳转背包升级
  6022: '/inventory/upgrade',
  6023: '/inventory/upgrade',

  // 金袋 - 联盟捐赠
  6005: '/alliance/donate',

  // 炼魂丹 - 炼妖壶
  6028: '/refine-pot',

  // 庄园建造手册 - 庄园扩建
  6029: '/manor/expand',

  // 战灵钥匙：跳转战灵页用于激活属性条
  6006: '/spirit/warehouse',

  // 盟主证明 - 联盟（创建联盟在联盟页）
  11001: '/alliance',

  // 技能书 - 需要先选择幻兽，跳转到幻兽列表
  // 技能书ID范围：10001-10699（根据configs/items.json）
  // 这里使用名称匹配，因为ID太多
  
  // 战骨物品 - 需要先选择幻兽，跳转到幻兽列表
  // 战骨物品ID范围：9101-9199（根据configs/items.json）
  // 这里使用名称匹配
}

/**
 * 道具“不能在背包直接使用”时的引导提示
 * @type {Record<number, string>}
 */
export const ITEM_USE_HINTS = {
  6001: '镇妖符：请前往【镇妖】界面镇妖时自动消耗。',
  6002: '迷踪符：请前往【地图副本】界面点击【迷踪】使用。',
  4002: '捕捉球：请在【地图副本】捕捉幻兽时选择使用。',
  4003: '强力捕捉球：请在【地图副本】捕捉幻兽时选择使用。',
  6018: '传送符：请前往【地图】界面的传送处使用。',
  6019: '追魂法宝：请前往【魔魂-猎魂高级场】使用。',
  6024: '双倍卡：请在【地图副本】打开战利品/宝箱时选择使用。',
  6022: '魔纹布：用于【背包升级】材料，升级时自动消耗。',
  6023: '丝线：用于【背包升级】材料，升级时自动消耗。',
  6005: '金袋：请前往【联盟-捐赠物资】界面捐献使用。',
  11001: '盟主证明：用于【创建联盟】时自动消耗。',
  6028: '炼魂丹：请前往【炼妖壶】功能开始炼妖时自动消耗。',
  6029: '庄园建造手册：请前往【庄园】扩建土地时自动消耗。',
  6006: '战灵钥匙：请前往【战灵-灵件室/属性】界面用于激活第2/第3条属性条。',
  // 3011（神·逆鳞碎片）支持在背包内直接合成，不需要跳转
  6015: '化仙丹：请前往【化仙池】界面使用。',
}

/**
 * 获取道具使用引导提示（用于弹窗）
 * @param {number} itemId
 * @param {string} itemName
 * @returns {string}
 */
export function getItemUseHint(itemId, itemName) {
  if (ITEM_USE_HINTS[itemId]) return ITEM_USE_HINTS[itemId]
  const name = itemName || ''
  if (name.includes('喇叭')) return '小喇叭：请前往【世界频道】喊话时消耗。'
  if (name.includes('捕捉球')) return '捕捉球：请在【地图副本】捕捉幻兽时选择使用。'
  if (name.includes('技能书') || name.includes('书')) return '技能书：请先前往【幻兽】选择目标幻兽后使用。'
  if (name.includes('战骨') || name.includes('卷轴')) return '战骨相关道具：请先前往【幻兽】选择目标幻兽后使用/装备。'
  return '该道具不能在背包中直接使用，请前往对应功能界面核销。'
}

/**
 * 根据道具ID和名称获取使用路由
 * @param {number} itemId - 道具ID
 * @param {string} itemName - 道具名称
 * @returns {string|null} 使用路由，如果没有特殊路由则返回null
 */
export function getItemUseRoute(itemId, itemName) {
  // 先检查ID映射
  if (ITEM_USE_ROUTES[itemId]) {
    return ITEM_USE_ROUTES[itemId]
  }
  
  // 再检查名称匹配
  const name = itemName || ''
  
  // 喇叭
  if (name.includes('喇叭')) {
    return '/world-chat'
  }
  
  // 捕捉球
  if (name.includes('捕捉球')) {
    return '/map'
  }
  
  // 技能书 - 跳转到幻兽列表，让用户选择幻兽
  if (name.includes('技能书') || name.includes('书')) {
    return '/beast'
  }
  
  // 战骨物品 - 跳转到幻兽列表，让用户选择幻兽
  // 包括：战骨物品（9101-9199）和战骨卷轴（5001-5099）
  if (name.includes('战骨') || (name.includes('卷轴') && (name.includes('骨') || name.includes('头骨') || name.includes('尾骨') || name.includes('手骨') || name.includes('腿骨') || name.includes('胸骨') || name.includes('臂骨') || name.includes('元魂')))) {
    return '/beast'
  }
  
  // 召唤球可以直接使用，不需要跳转
  if (name.includes('召唤球')) {
    return null
  }
  
  // 其他道具如果没有特殊路由，返回null，使用默认的直接使用逻辑
  return null
}

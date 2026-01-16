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
  
  // 技能书 - 需要先选择幻兽，跳转到幻兽列表
  // 技能书ID范围：10001-10699（根据configs/items.json）
  // 这里使用名称匹配，因为ID太多
  
  // 战骨物品 - 需要先选择幻兽，跳转到幻兽列表
  // 战骨物品ID范围：9101-9199（根据configs/items.json）
  // 这里使用名称匹配
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

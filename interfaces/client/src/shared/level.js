// src/shared/level.js

/**
 * 等级命名规则：x星x品召唤师
 * - x星对应 10*x 级
 * - x品对应 x 级（个位数）
 *
 * 例：9级 => 0星9品召唤师；48级 => 4星8品召唤师。
 */
export function getSummonerLevelParts(level) {
  const lv = Math.max(0, parseInt(level ?? 0, 10) || 0)
  return {
    star: Math.floor(lv / 10),
    pin: lv % 10,
  }
}

export function getSummonerTitle(level) {
  const { star, pin } = getSummonerLevelParts(level)
  return `${star}星${pin}品召唤师`
}

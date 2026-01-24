import http from '@/services/http'

/**
 * 获取盟战土地列表及其占领联盟信息
 * @param {boolean} all - 如果为 true，返回所有目标（飞龙军+伏虎军），用于"查看全部攻城目标"
 * @returns {Promise<object>} API 响应数据
 */
export async function fetchWarTargets(all = false) {
  const params = all ? { all: 'true' } : {}
  const res = await http.get('/alliance/war/targets', { params })
  return res.data
}

/**
 * 获取土地详情与报名联盟名单
 * @param {number} landId
 * @returns {Promise<object>} API 响应数据
 */
export async function fetchLandDetail(landId) {
  const res = await http.get(`/alliance/war/land/${landId}`)
  return res.data
}

export async function fetchWarLiveFeed() {
  const res = await http.get('/alliance/war/live-feed')
  return res.data
}

export async function fetchWarHonorStatus() {
  const res = await http.get('/alliance/war/honor')
  return res.data
}

export async function postWarHonorExchange(effectKey) {
  const res = await http.post('/alliance/war/honor/exchange', { effectKey })
  return res.data
}

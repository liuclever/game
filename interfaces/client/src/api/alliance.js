import http from '@/services/http'

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

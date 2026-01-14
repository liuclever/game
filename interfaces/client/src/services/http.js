// src/services/http.js
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000, // 增加到10秒，避免因计算战力等耗时操作导致超时
  withCredentials: true, // 支持session cookie
})

// 请求去重：防止同时发起多个相同的请求（仅在短时间内）
// 注意：由于 axios 拦截器的限制，这里只做标记，实际去重需要在业务层实现
// 或者使用 axios 的 CancelToken 功能

// 响应拦截器：对于 400 状态码，不抛出异常，而是正常返回响应
http.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 对于 400 状态码，如果响应中有数据，返回响应而不是抛出异常
    if (error.response && error.response.status === 400 && error.response.data) {
      return Promise.resolve(error.response)
    }
    // 其他错误正常抛出
    return Promise.reject(error)
  }
)

export default http

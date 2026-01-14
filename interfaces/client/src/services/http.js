// src/services/http.js
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000, // 增加超时时间到30秒
  withCredentials: true, // 支持session cookie
})

// 响应拦截器 - 处理错误
http.interceptors.response.use(
  response => response,
  error => {
    console.error('HTTP请求错误:', error)
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时')
    }
    return Promise.reject(error)
  }
)

export default http

// src/services/userService.js
import http from './http'

// 获取用户信息
export async function fetchUser() {
  const res = await http.get('/user/me')
  return res.data
}

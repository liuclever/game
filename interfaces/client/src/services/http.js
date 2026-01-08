// src/services/http.js
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 5000,
  withCredentials: true, // 支持session cookie
})

export default http

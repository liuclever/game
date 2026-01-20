// 在浏览器控制台运行此脚本来诊断白屏问题
// 按 F12 打开控制台，复制粘贴此脚本并回车

console.log('========================================')
console.log('白屏问题诊断脚本')
console.log('========================================')

// 1. 检查 Vue 应用是否存在
console.log('\n1. 检查 Vue 应用:')
if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
  console.log('✅ Vue DevTools Hook 存在')
} else {
  console.log('❌ Vue DevTools Hook 不存在')
}

// 2. 检查 DOM 元素
console.log('\n2. 检查 DOM 元素:')
const app = document.querySelector('#app')
if (app) {
  console.log('✅ #app 元素存在')
  console.log('   innerHTML 长度:', app.innerHTML.length)
  console.log('   子元素数量:', app.children.length)
  if (app.innerHTML.length === 0) {
    console.log('❌ #app 元素为空 - 这就是白屏的原因！')
  }
} else {
  console.log('❌ #app 元素不存在')
}

// 3. 检查路由
console.log('\n3. 检查路由:')
console.log('   当前 URL:', window.location.href)
console.log('   当前路径:', window.location.pathname)

// 4. 检查控制台错误
console.log('\n4. 检查是否有 JavaScript 错误:')
console.log('   请查看控制台上方是否有红色错误信息')

// 5. 检查网络请求
console.log('\n5. 检查网络请求:')
console.log('   切换到 Network 标签，查看是否有失败的请求（红色）')

// 6. 检查 localStorage
console.log('\n6. 检查 localStorage:')
console.log('   user_id:', localStorage.getItem('user_id'))
console.log('   nickname:', localStorage.getItem('nickname'))

// 7. 尝试手动触发 Vue 渲染
console.log('\n7. 尝试获取 Vue 实例:')
try {
  const vueApp = document.querySelector('#app').__vue_app__
  if (vueApp) {
    console.log('✅ Vue 应用实例存在')
  } else {
    console.log('❌ Vue 应用实例不存在')
  }
} catch (e) {
  console.log('❌ 无法获取 Vue 应用实例:', e.message)
}

console.log('\n========================================')
console.log('诊断完成')
console.log('========================================')
console.log('\n请将上述信息截图发送给开发人员')

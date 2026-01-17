// 在浏览器控制台（F12 -> Console）中运行此脚本来测试API

// 测试擂台API
fetch('/api/arena/info?type=normal', {
  method: 'GET',
  credentials: 'include'
})
.then(response => response.json())
.then(data => {
  console.log('=== 擂台API响应 ===');
  console.log('完整响应:', data);
  
  if (data.ok && data.arena) {
    console.log('\n擂台信息:');
    console.log('  champion:', data.arena.champion);
    console.log('  championUserId:', data.arena.championUserId);
    console.log('  isEmpty:', data.arena.isEmpty);
    console.log('  isChampion:', data.arena.isChampion);
    console.log('  consecutiveWins:', data.arena.consecutiveWins);
    console.log('  prizePool:', data.arena.prizePool);
    
    if (data.arena.isEmpty) {
      console.log('\n❌ 问题: isEmpty为true，但应该有擂主');
    } else if (data.arena.champion) {
      console.log('\n✅ 正常: 擂主是', data.arena.champion);
    } else {
      console.log('\n⚠️ 异常: isEmpty为false但champion为空');
    }
  }
})
.catch(error => {
  console.error('请求失败:', error);
});

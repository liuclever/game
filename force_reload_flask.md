# 强制Flask重新加载代码的步骤

## 问题
代码已经更新，但API响应中仍然没有 `total_contribution` 字段，说明Flask没有重新加载代码。

## 解决方案

### 方法1: 完全重启Flask服务

1. **停止当前Flask服务**
   - 在运行Flask的PowerShell窗口中按 `Ctrl+C`
   - 等待进程完全退出（看到命令提示符 `PS D:\work\game-1.0>`）

2. **清除Python缓存**
   ```powershell
   Get-ChildItem -Path . -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force
   Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force
   ```

3. **重新启动Flask服务**
   ```powershell
   python -m interfaces.web_api.app
   ```

### 方法2: 修改文件触发自动重载

1. **在 `interfaces/routes/alliance_routes.py` 文件中添加一个空格并保存**
   - 这会触发Flask的自动重载
   - 查看PowerShell窗口，应该看到 `* Detected change in ... reloading`

2. **等待重载完成**
   - 看到 `* Restarting with stat` 和 `* Debugger is active!`

3. **测试API**
   - 刷新浏览器页面
   - 检查 `/api/alliance/my` 的响应

### 方法3: 检查Flask是否真的重新加载了

在浏览器中访问联盟页面后，查看PowerShell窗口：

- **如果看到调试日志**：
  ```
  [DEBUG get_my_alliance] user_id=20057, contribution=10, total_contribution=15
  ```
  说明代码已经重新加载了

- **如果没有看到调试日志**：
  说明代码没有重新加载，需要完全重启

## 验证修复

修复后，API响应应该包含：
```json
{
  "member_info": {
    "contribution": 10,
    "role": 1,
    "total_contribution": 15  // 这个字段现在应该存在了！
  }
}
```

## 如果仍然没有 total_contribution 字段

请检查：
1. Flask服务是否真的重启了
2. 是否有其他路由文件覆盖了这个路由
3. 浏览器是否缓存了旧的响应（使用Ctrl+F5硬刷新）

# 梦炽云召唤之星 - 服务器配置信息

## 服务器信息
- IP地址: 8.146.206.229
- SSH密码: wxs1230.0
- 操作系统: CentOS 8
- 域名: mengzhiyun.zhmcy.top

## 目录结构
- 项目目录: /root/game/
- 前端目录: /root/game/interfaces/client/dist/
- 后端日志: /root/game/logs/backend.log
- 前端日志: /root/game/logs/frontend.log
- SSL证书目录: /etc/nginx/ssl/

## 数据库配置
- 数据库类型: MySQL 8.0
- 数据库名: game_tower
- 用户名: root
- 密码: Wxs1230.0

## Python环境
- Conda环境名: wenzi
- Python版本: 3.10

## 服务管理命令
```bash
# 启动服务
/root/start_game_service.sh start

# 停止服务
/root/start_game_service.sh stop

# 重启服务
/root/start_game_service.sh restart

# 查看状态
/root/start_game_service.sh status
```

## 支付宝配置
- APP ID: 2021006122619037
- 应用名称: 梦炽云
- 配置文件路径: /root/game/infrastructure/alipay/config.json
- 应用私钥路径: /root/game/infrastructure/alipay/cert/app_private_key.pem
- 支付宝公钥路径: /root/game/infrastructure/alipay/cert/alipay_public_key.pem
- 异步回调地址: https://mengzhiyun.zhmcy.top/api/pay/notify
- 同步返回地址: https://mengzhiyun.zhmcy.top/sponsor

## Nginx配置
- 配置文件: /etc/nginx/conf.d/game.conf
- SSL证书: /etc/nginx/ssl/mengzhiyun.zhmcy.top.pem
- SSL私钥: /etc/nginx/ssl/mengzhiyun.zhmcy.top.key

## 常用运维命令
```bash
# 查看后端日志
tail -f /root/game/logs/backend.log

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 重启Nginx
systemctl restart nginx

# 激活Python环境
conda activate wenzi

# 导入数据库
mysql -u root -pWxs1230.0 game_tower < /root/game_tower.sql
```

## 本地开发部署
- 本地项目路径: D:\work-taobao\game-source\game

### 前端部署
```bash
# 构建前端
cd D:\work-taobao\game-source\game\interfaces\client
npm run build

# 上传到服务器
scp -r D:\work-taobao\game-source\game\interfaces\client\dist root@8.146.206.229:/root/game/interfaces/client/
```

### 后端部署
```bash
# 上传后端代码
scp -r D:\work-taobao\game-source\game\interfaces\routes root@8.146.206.229:/root/game/interfaces/
scp -r D:\work-taobao\game-source\game\application root@8.146.206.229:/root/game/
scp -r D:\work-taobao\game-source\game\domain root@8.146.206.229:/root/game/
scp -r D:\work-taobao\game-source\game\infrastructure root@8.146.206.229:/root/game/
scp -r D:\work-taobao\game-source\game\configs root@8.146.206.229:/root/game/
```

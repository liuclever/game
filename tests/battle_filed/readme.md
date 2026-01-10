测试步骤
步骤	操作	预期结果
1. 启动应用	python -m interfaces.web_api.app	控制台输出 [Scheduler] 后台调度器已启动
2. 登录玩家	前端登录或调用 /api/auth/login	获得 session
3. 报名	POST /api/battlefield/signup body: {"type": "crane"}	返回 {"ok": true, ...}
4. 查询报名状态	GET /api/battlefield/info?type=crane	isSignedUp: true，报名人数 +1
5. 手动触发开赛	POST /api/battlefield/run body: {"type": "crane"}	返回 {"ok": true, "period": N, "total_players": ...}
6. 查看战报列表	GET /api/battlefield/yesterday?type=crane	返回本期所有对战记录
7. 查看单场详情	GET /api/battlefield/battle/<id>	返回完整 battle_data
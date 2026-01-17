# game/application/services/signin_service.py
from datetime import date
from infrastructure.db.connection import execute_query, execute_update

from domain.entities.player import Player
from domain.repositories.player_repo import IPlayerRepo
from domain.rules.signin_rules import can_signin, apply_signin_reward


class SigninError(Exception):
    """签到相关错误（例如重复签到）"""
    pass


class SigninService:
    def __init__(self, player_repo: IPlayerRepo):
        self.player_repo = player_repo

    def get_random_sponsor(self) -> str:
        """
        从盟战排行榜前三的联盟中随机选一个作为颁发者
        如果没有联盟，返回默认名字
        """
        try:
            # 查询盟战排行榜前三的联盟
            alliances = execute_query(
                """SELECT alliance_name FROM alliance 
                   WHERE alliance_level > 0 
                   ORDER BY alliance_level DESC, alliance_exp DESC 
                   LIMIT 3"""
            )
            
            if alliances:
                import random
                return random.choice(alliances)['alliance_name']
            else:
                return "系统"
        except Exception as e:
            print(f"获取联盟失败: {e}")
            return "系统"

    def do_signin(self, player_id: int, today: date | None = None) -> dict:
        """
        执行一次签到
        返回签到结果信息
        """
        if today is None:
            today = date.today()

        player = self.player_repo.get_by_id(player_id)
        if player is None:
            raise SigninError(f"player {player_id} not found")

        if not can_signin(player, today):
            raise SigninError("今天已经签到过了")

        # 发奖励
        reward_info = apply_signin_reward(player, today)
        
        # 获取颁发者
        sponsor = self.get_random_sponsor()

        # 保存玩家数据
        self.player_repo.save(player)

        # 同步写入“签到记录表”，用于签到页/月历/累计奖励等功能读取
        # 说明：主页签到走的也是本服务，因此这里写一次，保证“主页签到”和“签到页”不再两套逻辑。
        try:
            execute_update(
                """
                INSERT INTO player_signin_records (user_id, signin_date, is_makeup, reward_copper)
                VALUES (%s, %s, 0, %s)
                ON DUPLICATE KEY UPDATE reward_copper=VALUES(reward_copper)
                """,
                (player_id, today, int(reward_info.get("actual_gold", 0) or 0)),
            )
        except Exception:
            # 老库可能没有该表；不影响签到主流程（至少 player.last_signin_date 会被写入）
            pass
        
        return {
            'ok': True,
            'reward': {
                'base_copper': reward_info['base_gold'],
                'copper': reward_info['actual_gold'],
                'multiplier': 2 if reward_info['is_doubled'] else 1,
            },
            'signin_streak': reward_info['consecutive_days'],
            'last_signin_date': today.isoformat(),
            'issuer_name': sponsor if sponsor != "系统" else None,
        }

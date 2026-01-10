from datetime import date
from typing import Optional, Dict
from domain.entities.daily_activity import DailyActivity
from domain.repositories.daily_activity_repo import IDailyActivityRepo

class DailyActivityService:
    def __init__(self, daily_activity_repo: IDailyActivityRepo):
        self.daily_activity_repo = daily_activity_repo

    def get_activity(self, user_id: int) -> DailyActivity:
        """获取玩家当前活跃度（含自动重置逻辑）"""
        activity = self.daily_activity_repo.get_by_user_id(user_id)
        current_date = date.today()
        
        if not activity:
            activity = DailyActivity(user_id=user_id, last_updated_date=current_date)
            # 自动完成登录任务
            activity.add_activity("login_game", 10)
            self.daily_activity_repo.save(activity)
        else:
            if activity.reset_if_new_day(current_date):
                # 自动完成登录任务
                activity.add_activity("login_game", 10)
                self.daily_activity_repo.save(activity)
            else:
                # 如果是旧的一天但还没完成登录任务（理论上不会，但增加健壮性）
                if activity.add_activity("login_game", 10):
                    self.daily_activity_repo.save(activity)
                
        return activity

    def add_activity(self, user_id: int, task_key: str, points: int) -> bool:
        """为玩家增加活跃度"""
        activity = self.get_activity(user_id)
        if activity.add_activity(task_key, points):
            self.daily_activity_repo.save(activity)
            return True
        return False

    def record_infuse(self, user_id: int, target_id: int) -> bool:
        """记录灌注水晶塔行为"""
        activity = self.get_activity(user_id)
        if activity.record_infusion(target_id):
            self.daily_activity_repo.save(activity)
            return True
        return False

    def get_activity_data(self, user_id: int) -> Dict:
        """获取用于API返回的活跃度数据"""
        activity = self.get_activity(user_id)
        return {
            "activity_value": activity.activity_value,
            "completed_tasks": activity.completed_tasks,
            "last_updated_date": str(activity.last_updated_date)
        }

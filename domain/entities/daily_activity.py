from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class DailyActivity:
    """玩家每日活跃度实体"""
    user_id: int
    activity_value: int = 0
    last_updated_date: date = field(default_factory=date.today)
    completed_tasks: List[str] = field(default_factory=list)

    def reset_if_new_day(self, current_date: date):
        """如果是新的一天，重置活跃度和已完成任务"""
        if self.last_updated_date != current_date:
            self.activity_value = 0
            self.completed_tasks = []
            self.last_updated_date = current_date
            return True
        return False

    def is_task_completed(self, task_key: str) -> bool:
        """检查任务是否已完成"""
        return task_key in self.completed_tasks

    def add_activity(self, task_key: str, points: int):
        """增加活跃度（防重复）"""
        if not self.is_task_completed(task_key):
            self.activity_value += points
            self.completed_tasks.append(task_key)
            return True
        return False

    def record_infusion(self, target_id: int) -> bool:
        """记录灌注水晶塔进度，满3人奖励9点活跃度"""
        task_done_key = "crystal_tower"
        if self.is_task_completed(task_done_key):
            return False
        
        progress_key = f"infuse_target:{target_id}"
        if progress_key not in self.completed_tasks:
            self.completed_tasks.append(progress_key)
            
            # 检查是否达成目标
            infuse_count = len([k for k in self.completed_tasks if k.startswith("infuse_target:")])
            if infuse_count >= 3:
                return self.add_activity(task_done_key, 9)
            return True # 进度增加，虽然任务没最终完成
        return False

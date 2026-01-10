import json
from datetime import date
from typing import Optional
from domain.entities.daily_activity import DailyActivity
from domain.repositories.daily_activity_repo import IDailyActivityRepo
from infrastructure.db.connection import execute_query, execute_update, execute_insert

class MySQLDailyActivityRepo(IDailyActivityRepo):
    def get_by_user_id(self, user_id: int) -> Optional[DailyActivity]:
        sql = "SELECT user_id, activity_value, last_updated_date, completed_tasks FROM player_daily_activity WHERE user_id = %s"
        rows = execute_query(sql, (user_id,))
        if rows:
            row = rows[0]
            completed_tasks = []
            if row['completed_tasks']:
                if isinstance(row['completed_tasks'], str):
                    completed_tasks = json.loads(row['completed_tasks'])
                else:
                    completed_tasks = row['completed_tasks']
            
            return DailyActivity(
                user_id=row['user_id'],
                activity_value=row['activity_value'],
                last_updated_date=row['last_updated_date'],
                completed_tasks=completed_tasks
            )
        return None

    def save(self, activity: DailyActivity) -> None:
        # 检查是否存在
        sql_check = "SELECT 1 FROM player_daily_activity WHERE user_id = %s"
        exists = execute_query(sql_check, (activity.user_id,))
        
        completed_tasks_json = json.dumps(activity.completed_tasks)
        
        if exists:
            sql = """
                UPDATE player_daily_activity 
                SET activity_value = %s, last_updated_date = %s, completed_tasks = %s 
                WHERE user_id = %s
            """
            execute_update(sql, (activity.activity_value, activity.last_updated_date, completed_tasks_json, activity.user_id))
        else:
            sql = """
                INSERT INTO player_daily_activity (user_id, activity_value, last_updated_date, completed_tasks)
                VALUES (%s, %s, %s, %s)
            """
            execute_insert(sql, (activity.user_id, activity.activity_value, activity.last_updated_date, completed_tasks_json))

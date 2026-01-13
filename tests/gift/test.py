"""
Quick helper to tweak a player's daily activity for manual testing.

Usage:
  python tests/gift/test.py

Only edit TARGET_ACTIVITY_VALUE below to set a new activity score for player 4035.
"""

from datetime import date

from infrastructure.db.connection import get_connection

TARGET_USER_ID = 4035
# 修改这一行即可设置玩家活跃度
TARGET_ACTIVITY_VALUE = 50


def upsert_activity(user_id: int, activity_value: int):
    today = date.today()
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM player_daily_activity WHERE user_id = %s",
                (user_id,),
            )
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """
                    UPDATE player_daily_activity
                    SET activity_value = %s,
                        last_updated_date = %s
                    WHERE user_id = %s
                    """,
                    (activity_value, today, user_id),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO player_daily_activity
                        (user_id, activity_value, last_updated_date, completed_tasks)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, activity_value, today, "[]"),
                )
        conn.commit()
    finally:
        conn.close()


def main():
    upsert_activity(TARGET_USER_ID, TARGET_ACTIVITY_VALUE)
    print(
        f"玩家 {TARGET_USER_ID} 的活跃度已设置为 {TARGET_ACTIVITY_VALUE} 点（日期 {date.today()}）。"
    )


if __name__ == "__main__":
    main()

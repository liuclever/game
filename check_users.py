from infrastructure.db.connection import execute_query

users = execute_query('SELECT user_id, username, nickname FROM player LIMIT 5')
for u in users:
    print(f"用户名: {u['username']}, 昵称: {u['nickname']}, ID: {u['user_id']}")

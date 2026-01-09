"""
信件服务
处理私信和好友请求
"""
from typing import List, Dict, Optional
from datetime import datetime
from infrastructure.db.connection import execute_query, execute_insert, execute_update


class MailService:
    """信件服务"""
    
    MAX_MESSAGE_LENGTH = 200  # 私信最大长度
    
    def get_private_message_senders(self, user_id: int) -> List[Dict]:
        """
        获取给当前用户发过私信的玩家列表（去重，按最新消息时间排序）
        
        Args:
            user_id: 当前用户ID
        
        Returns:
            发送者列表，每个包含：id, name, user_id, unread_count, last_message_time
        """
        try:
            # 获取所有给当前用户发过消息的发送者（去重，按最新消息时间排序）
            rows = execute_query(
                """SELECT sender_id, sender_name, MAX(created_at) as last_message_time,
                          COUNT(CASE WHEN is_read = 0 THEN 1 END) as unread_count
                   FROM private_message
                   WHERE receiver_id = %s
                   GROUP BY sender_id, sender_name
                   ORDER BY last_message_time DESC""",
                (user_id,)
            )
            
            result = []
            for row in rows:
                result.append({
                    "id": row['sender_id'],
                    "name": row['sender_name'],
                    "user_id": row['sender_id'],
                    "unread_count": row.get('unread_count', 0),
                    "last_message_time": row.get('last_message_time'),
                })
            return result
        except Exception as e:
            print(f"获取私信发送者列表失败: {e}")
            return []
    
    def get_conversation_messages(
        self, 
        user_id: int, 
        target_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> Dict:
        """
        获取与某个玩家的聊天记录（分页）
        
        Args:
            user_id: 当前用户ID
            target_id: 目标用户ID
            page: 页码（从1开始）
            page_size: 每页数量
        
        Returns:
            消息列表和分页信息
        """
        offset = (page - 1) * page_size
        
        try:
            # 获取双方的所有消息（按时间倒序）
            rows = execute_query(
                """SELECT id, sender_id, sender_name, receiver_id, receiver_name,
                          content, created_at
                   FROM private_message
                   WHERE (sender_id = %s AND receiver_id = %s) 
                      OR (sender_id = %s AND receiver_id = %s)
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (user_id, target_id, target_id, user_id, page_size, offset)
            )
            
            # 获取总数
            total_rows = execute_query(
                """SELECT COUNT(*) as total
                   FROM private_message
                   WHERE (sender_id = %s AND receiver_id = %s) 
                      OR (sender_id = %s AND receiver_id = %s)""",
                (user_id, target_id, target_id, user_id)
            )
            total = total_rows[0]['total'] if total_rows else 0
            
            # 格式化消息
            messages = []
            for row in reversed(rows):  # 反转，让最早的消息在前
                is_sender = row['sender_id'] == user_id
                time_str = self._format_time(row['created_at'])
                
                messages.append({
                    "id": row['id'],
                    "is_me": is_sender,
                    "sender_name": row['sender_name'],
                    "content": row['content'],
                    "time": time_str,
                })
            
            # 标记为已读
            execute_update(
                """UPDATE private_message 
                   SET is_read = 1 
                   WHERE sender_id = %s AND receiver_id = %s AND is_read = 0""",
                (target_id, user_id)
            )
            
            total_pages = max(1, (total + page_size - 1) // page_size)
            
            return {
                "ok": True,
                "messages": messages,
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            }
        except Exception as e:
            print(f"获取聊天记录失败: {e}")
            return {
                "ok": False,
                "error": str(e),
                "messages": [],
                "page": 1,
                "page_size": page_size,
                "total": 0,
                "total_pages": 1,
            }
    
    def send_private_message(
        self, 
        sender_id: int, 
        sender_name: str, 
        receiver_id: int, 
        receiver_name: str, 
        content: str
    ) -> Dict:
        """
        发送私信
        
        Args:
            sender_id: 发送者ID
            sender_name: 发送者昵称
            receiver_id: 接收者ID
            receiver_name: 接收者昵称
            content: 消息内容（最多200字符）
        
        Returns:
            发送结果
        """
        # 验证内容
        if not content or not content.strip():
            return {"ok": False, "error": "消息内容不能为空"}
        
        content = content.strip()
        if len(content) > self.MAX_MESSAGE_LENGTH:
            return {"ok": False, "error": f"消息内容不能超过{self.MAX_MESSAGE_LENGTH}字"}
        
        if sender_id == receiver_id:
            return {"ok": False, "error": "不能给自己发消息"}
        
        try:
            # 保存消息
            message_id = execute_insert(
                """INSERT INTO private_message 
                   (sender_id, sender_name, receiver_id, receiver_name, content)
                   VALUES (%s, %s, %s, %s, %s)""",
                (sender_id, sender_name, receiver_id, receiver_name, content)
            )
            
            return {
                "ok": True,
                "message_id": message_id,
                "message": "发送成功",
            }
        except Exception as e:
            print(f"发送私信失败: {e}")
            return {"ok": False, "error": f"发送失败: {str(e)}"}
    
    def delete_conversation(self, user_id: int, target_id: int) -> Dict:
        """
        删除与某个玩家的所有私信
        
        Args:
            user_id: 当前用户ID
            target_id: 目标用户ID
        
        Returns:
            删除结果
        """
        try:
            execute_update(
                """DELETE FROM private_message
                   WHERE (sender_id = %s AND receiver_id = %s)
                      OR (sender_id = %s AND receiver_id = %s)""",
                (user_id, target_id, target_id, user_id)
            )
            return {"ok": True, "message": "删除成功"}
        except Exception as e:
            print(f"删除私信失败: {e}")
            return {"ok": False, "error": f"删除失败: {str(e)}"}
    
    def get_friend_requests(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict:
        """
        获取好友请求列表（分页）
        
        Args:
            user_id: 当前用户ID
            page: 页码（从1开始）
            page_size: 每页数量
        
        Returns:
            好友请求列表和分页信息
        """
        offset = (page - 1) * page_size
        
        try:
            # 获取发送给当前用户的请求
            sent_to_me = execute_query(
                """SELECT id, requester_id, requester_name, status, created_at
                   FROM friend_request
                   WHERE receiver_id = %s
                   ORDER BY created_at DESC
                   LIMIT %s OFFSET %s""",
                (user_id, page_size, offset)
            )
            
            # 获取当前用户发送的请求（对方已同意的）
            my_sent = execute_query(
                """SELECT id, receiver_id as requester_id, receiver_name as requester_name, 
                          status, created_at
                   FROM friend_request
                   WHERE requester_id = %s AND status = 'accepted'
                   ORDER BY updated_at DESC
                   LIMIT %s OFFSET %s""",
                (user_id, page_size, offset)
            )
            
            # 获取总数
            total_rows = execute_query(
                """SELECT COUNT(*) as total
                   FROM friend_request
                   WHERE receiver_id = %s OR (requester_id = %s AND status = 'accepted')""",
                (user_id, user_id)
            )
            total = total_rows[0]['total'] if total_rows else 0
            
            # 格式化请求列表
            requests = []
            
            # 处理发送给我的请求
            for row in sent_to_me:
                time_str = self._format_time(row['created_at'])
                status_text = ""
                if row['status'] == 'accepted':
                    status_text = "已同意"
                elif row['status'] == 'rejected':
                    status_text = "已拒绝"
                
                requests.append({
                    "id": row['id'],
                    "time": time_str,
                    "from": row['requester_name'],
                    "text": "请求加你好友",
                    "status": status_text,
                    "requester_id": row['requester_id'],
                })
            
            # 处理我发送的请求（对方已同意的）
            for row in my_sent:
                time_str = self._format_time(row.get('updated_at') or row['created_at'])
                requests.append({
                    "id": row['id'],
                    "time": time_str,
                    "from": row['requester_name'],
                    "text": "通过了你的好友请求",
                    "status": "",
                    "requester_id": row['requester_id'],
                })
            
            # 按时间倒序排序
            requests.sort(key=lambda x: self._parse_time(x['time']), reverse=True)
            
            # 分页
            total_pages = max(1, (total + page_size - 1) // page_size)
            paginated_requests = requests[offset:offset + page_size]
            
            return {
                "ok": True,
                "requests": paginated_requests,
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            }
        except Exception as e:
            print(f"获取好友请求列表失败: {e}")
            return {
                "ok": False,
                "error": str(e),
                "requests": [],
                "page": 1,
                "page_size": page_size,
                "total": 0,
                "total_pages": 1,
            }
    
    def send_friend_request(
        self, 
        requester_id: int, 
        requester_name: str, 
        receiver_id: int, 
        receiver_name: str
    ) -> Dict:
        """
        发送好友请求
        
        Args:
            requester_id: 请求者ID
            requester_name: 请求者昵称
            receiver_id: 接收者ID
            receiver_name: 接收者昵称
        
        Returns:
            发送结果
        """
        if requester_id == receiver_id:
            return {"ok": False, "error": "不能添加自己为好友"}
        
        # 检查是否已经是好友
        friend_rows = execute_query(
            """SELECT id FROM friend_relation 
               WHERE (user_id = %s AND friend_id = %s) 
                  OR (user_id = %s AND friend_id = %s)""",
            (requester_id, receiver_id, receiver_id, requester_id)
        )
        if friend_rows:
            return {"ok": False, "error": "你们已经是好友了"}
        
        # 检查是否已有待处理的请求
        existing_rows = execute_query(
            """SELECT id, status FROM friend_request 
               WHERE requester_id = %s AND receiver_id = %s""",
            (requester_id, receiver_id)
        )
        if existing_rows:
            status = existing_rows[0]['status']
            if status == 'pending':
                return {"ok": False, "error": "已发送过好友请求，请等待对方处理"}
            elif status == 'accepted':
                return {"ok": False, "error": "你们已经是好友了"}
        
        # 检查对方是否允许陌生人添加
        setting_rows = execute_query(
            """SELECT allow_stranger_add_friend FROM player_settings WHERE user_id = %s""",
            (receiver_id,)
        )
        if setting_rows and setting_rows[0].get('allow_stranger_add_friend', 1) == 0:
            return {"ok": False, "error": "对方设置了拒绝陌生人添加好友"}
        
        try:
            # 创建或更新请求
            execute_insert(
                """INSERT INTO friend_request 
                   (requester_id, requester_name, receiver_id, receiver_name, status)
                   VALUES (%s, %s, %s, %s, 'pending')
                   ON DUPLICATE KEY UPDATE 
                   requester_name = VALUES(requester_name),
                   receiver_name = VALUES(receiver_name),
                   status = 'pending',
                   created_at = CURRENT_TIMESTAMP""",
                (requester_id, requester_name, receiver_id, receiver_name)
            )
            
            return {"ok": True, "message": "好友请求已发送"}
        except Exception as e:
            print(f"发送好友请求失败: {e}")
            return {"ok": False, "error": f"发送失败: {str(e)}"}
    
    def accept_friend_request(self, request_id: int, user_id: int) -> Dict:
        """
        接受好友请求
        
        Args:
            request_id: 请求ID
            user_id: 当前用户ID（接收者）
        
        Returns:
            处理结果
        """
        try:
            # 获取请求信息
            request_rows = execute_query(
                """SELECT requester_id, requester_name, receiver_id, receiver_name, status
                   FROM friend_request WHERE id = %s AND receiver_id = %s""",
                (request_id, user_id)
            )
            
            if not request_rows:
                return {"ok": False, "error": "请求不存在"}
            
            request_data = request_rows[0]
            if request_data['status'] != 'pending':
                return {"ok": False, "error": "该请求已处理"}
            
            requester_id = request_data['requester_id']
            requester_name = request_data['requester_name']
            receiver_id = request_data['receiver_id']
            receiver_name = request_data['receiver_name']
            
            # 更新请求状态
            execute_update(
                """UPDATE friend_request SET status = 'accepted', updated_at = NOW()
                   WHERE id = %s""",
                (request_id,)
            )
            
            # 建立好友关系（双向）
            execute_insert(
                """INSERT INTO friend_relation (user_id, friend_id)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE user_id = user_id""",
                (requester_id, receiver_id)
            )
            execute_insert(
                """INSERT INTO friend_relation (user_id, friend_id)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE user_id = user_id""",
                (receiver_id, requester_id)
            )
            
            return {"ok": True, "message": "已同意好友请求"}
        except Exception as e:
            print(f"接受好友请求失败: {e}")
            return {"ok": False, "error": f"处理失败: {str(e)}"}
    
    def reject_friend_request(self, request_id: int, user_id: int) -> Dict:
        """
        拒绝好友请求
        
        Args:
            request_id: 请求ID
            user_id: 当前用户ID（接收者）
        
        Returns:
            处理结果
        """
        try:
            execute_update(
                """UPDATE friend_request SET status = 'rejected', updated_at = NOW()
                   WHERE id = %s AND receiver_id = %s""",
                (request_id, user_id)
            )
            return {"ok": True, "message": "已拒绝好友请求"}
        except Exception as e:
            print(f"拒绝好友请求失败: {e}")
            return {"ok": False, "error": f"处理失败: {str(e)}"}
    
    def get_allow_stranger_setting(self, user_id: int) -> bool:
        """获取是否允许陌生人添加好友的设置"""
        try:
            rows = execute_query(
                """SELECT allow_stranger_add_friend FROM player_settings WHERE user_id = %s""",
                (user_id,)
            )
            if rows:
                return bool(rows[0].get('allow_stranger_add_friend', 1))
            # 默认允许
            return True
        except Exception:
            return True
    
    def set_allow_stranger_setting(self, user_id: int, allow: bool) -> Dict:
        """设置是否允许陌生人添加好友"""
        try:
            execute_insert(
                """INSERT INTO player_settings (user_id, allow_stranger_add_friend)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE 
                   allow_stranger_add_friend = VALUES(allow_stranger_add_friend),
                   updated_at = NOW()""",
                (user_id, 1 if allow else 0)
            )
            return {"ok": True, "message": "设置已保存"}
        except Exception as e:
            print(f"保存设置失败: {e}")
            return {"ok": False, "error": f"保存失败: {str(e)}"}
    
    def _format_time(self, dt) -> str:
        """格式化时间为 MM.DD HH:MM"""
        if isinstance(dt, datetime):
            return dt.strftime("%m.%d %H:%M")
        elif isinstance(dt, str):
            try:
                d = datetime.strptime(dt[:19], '%Y-%m-%d %H:%M:%S')
                return d.strftime("%m.%d %H:%M")
            except:
                return dt[5:16].replace('-', '.') if len(dt) > 16 else dt
        else:
            return str(dt)[5:16].replace('-', '.') if len(str(dt)) > 16 else str(dt)
    
    def _parse_time(self, time_str: str) -> datetime:
        """解析时间字符串为datetime对象用于排序"""
        try:
            current_year = datetime.now().year
            dt_str = f"{current_year}-{time_str.replace('.', '-')}"
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except:
            return datetime.min

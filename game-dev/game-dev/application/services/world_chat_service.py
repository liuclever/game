"""
世界聊天服务
"""
from typing import List, Dict, Optional
from datetime import datetime
from domain.repositories.player_repo import IPlayerRepo
from application.services.inventory_service import InventoryService, InventoryError
from infrastructure.db.connection import execute_query, execute_update, execute_insert


class WorldChatError(Exception):
    """世界聊天相关错误"""
    pass


class WorldChatService:
    """世界聊天服务"""
    
    def __init__(
        self,
        player_repo: IPlayerRepo,
        inventory_service: InventoryService,
    ):
        self.player_repo = player_repo
        self.inventory_service = inventory_service
        self.SMALL_HORN_ITEM_ID = 6012  # 小喇叭物品ID
        self.MAX_MESSAGE_LENGTH = 35  # 最大消息长度
    
    def send_message(
        self, 
        user_id: int, 
        content: str, 
        message_type: str = 'normal'
    ) -> Dict:
        """
        发送世界聊天消息
        
        Args:
            user_id: 用户ID
            content: 消息内容
            message_type: 消息类型（'normal'=普通喊话, 'summon_king'=召唤之王置顶）
        
        Returns:
            发送结果
        """
        # 验证消息内容
        if not content or len(content.strip()) == 0:
            raise WorldChatError("消息内容不能为空")
        
        if len(content) > self.MAX_MESSAGE_LENGTH:
            raise WorldChatError(f"消息长度不能超过{self.MAX_MESSAGE_LENGTH}个字符")
        
        # 获取玩家信息
        player = self.player_repo.get_by_id(user_id)
        if not player:
            raise WorldChatError("玩家不存在")
        
        # 检查是否是召唤之王
        is_summon_king = self._is_summon_king(user_id)
        
        # 如果是召唤之王消息，需要验证权限
        if message_type == 'summon_king':
            if not is_summon_king:
                raise WorldChatError("只有召唤之王才能发布置顶消息")
        else:
            # 普通消息需要消耗小喇叭
            horn_count = self.inventory_service.get_item_count(user_id, self.SMALL_HORN_ITEM_ID)
            if horn_count < 1:
                raise WorldChatError("小喇叭数量不足")
            
            # 扣除小喇叭
            try:
                self.inventory_service.remove_item(user_id, self.SMALL_HORN_ITEM_ID, 1)
            except InventoryError as e:
                raise WorldChatError(f"扣除小喇叭失败：{str(e)}")
        
        # 如果是召唤之王置顶消息，先取消所有之前的置顶（只保留最新的置顶消息）
        if message_type == 'summon_king':
            execute_update(
                "UPDATE world_chat_message SET is_pinned = 0 WHERE is_pinned = 1",
                ()
            )
        
        # 插入新消息
        message_id = execute_insert(
            """INSERT INTO world_chat_message 
               (user_id, nickname, message_type, content, is_pinned) 
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, player.nickname, message_type, content.strip(), 1 if message_type == 'summon_king' else 0)
        )
        
        return {
            "ok": True,
            "message_id": message_id,
            "message": "发送成功"
        }
    
    def get_messages(
        self, 
        page: int = 1, 
        page_size: int = 10,
        exclude_alliance: bool = True,
        exclude_system: bool = True
    ) -> Dict:
        """
        获取世界聊天消息列表（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            exclude_alliance: 是否排除联盟消息
            exclude_system: 是否排除系统消息
        
        Returns:
            消息列表和分页信息
        """
        offset = (page - 1) * page_size
        
        # 构建查询条件
        where_conditions = []
        if exclude_alliance:
            where_conditions.append("message_type != 'alliance'")
        if exclude_system:
            where_conditions.append("message_type != 'system'")
        
        # 排除置顶消息（置顶消息会单独显示，不在分页列表中）
        where_conditions.append("is_pinned = 0")
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 查询总数（排除置顶消息）
        count_sql = f"SELECT COUNT(*) AS total FROM world_chat_message {where_clause}"
        count_rows = execute_query(count_sql)
        total = count_rows[0]['total'] if count_rows else 0
        total_pages = max(1, (total + page_size - 1) // page_size)
        
        # 查询消息（按时间倒序，不包含置顶消息）
        sql = f"""
            SELECT id, user_id, nickname, message_type, content, is_pinned, created_at
            FROM world_chat_message
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (page_size, offset))
        
        messages = []
        for row in rows:
            # 格式化时间 (MM.DD HH:MM)
            created_at = row['created_at']
            if isinstance(created_at, datetime):
                time_str = created_at.strftime('%m.%d %H:%M')
            elif isinstance(created_at, str):
                # 处理字符串格式的时间
                try:
                    dt = datetime.strptime(created_at[:19], '%Y-%m-%d %H:%M:%S')
                    time_str = dt.strftime('%m.%d %H:%M')
                except:
                    time_str = created_at[5:16].replace('-', '.').replace(' ', ' ') if len(created_at) > 16 else created_at
            else:
                time_str = str(created_at)[5:16].replace('-', '.').replace(' ', ' ') if len(str(created_at)) > 16 else str(created_at)
            
            messages.append({
                "id": row['id'],
                "user_id": row['user_id'],
                "nickname": row['nickname'],
                "message_type": row['message_type'],
                "content": row['content'],
                "is_pinned": bool(row['is_pinned']),
                "time": time_str,
            })
        
        return {
            "ok": True,
            "messages": messages,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }
    
    def get_homepage_messages(self, limit: int = 3) -> List[Dict]:
        """
        获取首页显示的喊话消息（只显示普通喊话，最多3条）
        注意：不包含置顶消息（置顶消息单独显示）
        
        Args:
            limit: 返回数量限制
        
        Returns:
            消息列表
        """
        sql = """
            SELECT id, user_id, nickname, message_type, content, is_pinned, created_at
            FROM world_chat_message
            WHERE message_type = 'normal' AND is_pinned = 0
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (limit,))
        
        messages = []
        for row in rows:
            created_at = row['created_at']
            if isinstance(created_at, datetime):
                time_str = created_at.strftime('%m.%d %H:%M')
            elif isinstance(created_at, str):
                try:
                    dt = datetime.strptime(created_at[:19], '%Y-%m-%d %H:%M:%S')
                    time_str = dt.strftime('%m.%d %H:%M')
                except:
                    time_str = created_at[5:16].replace('-', '.').replace(' ', ' ') if len(created_at) > 16 else created_at
            else:
                time_str = str(created_at)[5:16].replace('-', '.').replace(' ', ' ') if len(str(created_at)) > 16 else str(created_at)
            
            messages.append({
                "id": row['id'],
                "user_id": row['user_id'],
                "nickname": row['nickname'],
                "content": row['content'],
                "time": time_str,
            })
        
        return messages
    
    def get_pinned_message(self) -> Optional[Dict]:
        """
        获取当前置顶的召唤之王消息（只有一条）
        
        Returns:
            置顶消息，如果没有则返回None
        """
        rows = execute_query(
            """SELECT id, user_id, nickname, message_type, content, created_at
               FROM world_chat_message
               WHERE is_pinned = 1
               ORDER BY created_at DESC
               LIMIT 1"""
        )
        
        if not rows:
            return None
        
        row = rows[0]
        created_at = row['created_at']
        if isinstance(created_at, datetime):
            time_str = created_at.strftime('%m.%d %H:%M')
        elif isinstance(created_at, str):
            try:
                dt = datetime.strptime(created_at[:19], '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime('%m.%d %H:%M')
            except:
                time_str = created_at[5:16].replace('-', '.').replace(' ', ' ') if len(created_at) > 16 else created_at
        else:
            time_str = str(created_at)[5:16].replace('-', '.').replace(' ', ' ') if len(str(created_at)) > 16 else str(created_at)
        
        return {
            "id": row['id'],
            "user_id": row['user_id'],
            "nickname": row['nickname'],
            "content": row['content'],
            "time": time_str,
        }
    
    def _is_summon_king(self, user_id: int) -> bool:
        """检查玩家是否是召唤之王"""
        rows = execute_query(
            "SELECT is_summon_king FROM player WHERE user_id = %s",
            (user_id,)
        )
        if rows:
            return bool(rows[0].get('is_summon_king', 0))
        return False
    
    def get_horn_count(self, user_id: int) -> int:
        """获取玩家小喇叭数量"""
        return self.inventory_service.get_item_count(user_id, self.SMALL_HORN_ITEM_ID)

"""
开服活动服务类
"""
import json
import os
import random
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from infrastructure.db.connection import execute_query, execute_update


class AnnouncementError(Exception):
    pass


class AnnouncementService:
    """公告活动服务"""

    def __init__(self, inventory_service=None, player_repo=None):
        self.inventory_service = inventory_service
        self.player_repo = player_repo
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """加载公告配置"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "configs", "announcements.json"
        )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"announcements": []}

    def get_announcement(self, activity_id: str) -> Optional[dict]:
        """获取指定公告配置"""
        for ann in self._config.get("announcements", []):
            if ann.get("id") == activity_id:
                return ann
        return None

    def is_activity_active(self, activity_id: str) -> bool:
        """检查活动是否在进行中"""
        ann = self.get_announcement(activity_id)
        if not ann:
            return False
        now = datetime.now()
        start = datetime.fromisoformat(ann.get("start_time", "2099-01-01T00:00:00"))
        end = datetime.fromisoformat(ann.get("end_time", "2000-01-01T00:00:00"))
        return start <= now <= end

    def is_activity_ended(self, activity_id: str) -> bool:
        """检查活动是否已结束"""
        ann = self.get_announcement(activity_id)
        if not ann:
            return True
        now = datetime.now()
        end = datetime.fromisoformat(ann.get("end_time", "2000-01-01T00:00:00"))
        return now > end

    # ==================== 新人战力榜排行 ====================

    def get_power_ranking(self, level_bracket: int, page: int = 1, size: int = 10) -> dict:
        """
        获取指定等级段的战力排行
        level_bracket: 29/39/49/59
        """
        level_ranges = {
            29: (20, 29),
            39: (30, 39),
            49: (40, 49),
            59: (50, 59),
        }
        if level_bracket not in level_ranges:
            return {"ok": False, "error": "无效的等级段"}

        min_level, max_level = level_ranges[level_bracket]
        offset = (page - 1) * size

        # 查询战力排行
        sql = """
            SELECT p.user_id as userId, p.nickname, p.level, p.vip_level as vipLevel,
                   COALESCE(SUM(b.combat_power), 0) as power
            FROM player p
            LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
            WHERE p.level BETWEEN %s AND %s
            GROUP BY p.user_id, p.nickname, p.level, p.vip_level
            ORDER BY power DESC, p.level DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (min_level, max_level, size, offset))

        # 总数
        count_sql = """
            SELECT COUNT(DISTINCT p.user_id) as total
            FROM player p
            WHERE p.level BETWEEN %s AND %s
        """
        count_rows = execute_query(count_sql, (min_level, max_level))
        total = count_rows[0]['total'] if count_rows else 0

        # 添加排名
        rankings = []
        for idx, r in enumerate(rows or []):
            obj = dict(r)
            obj["rank"] = offset + idx + 1
            rankings.append(obj)

        total_pages = max(1, (total + size - 1) // size)

        return {
            "ok": True,
            "level_bracket": level_bracket,
            "rankings": rankings,
            "total": total,
            "totalPages": total_pages,
            "page": page,
        }

    def finalize_power_ranking(self, level_bracket: int) -> dict:
        """
        确定战力榜并发放奖励（只执行一次）
        """
        activity_id = "power_ranking"
        
        # 检查是否已经结算
        check_sql = """
            SELECT id, is_rewards_sent FROM activity_finalize_log
            WHERE activity_id = %s AND level_bracket = %s AND finalize_type = 'power_ranking'
        """
        existing = execute_query(check_sql, (activity_id, level_bracket))
        if existing and existing[0].get('is_rewards_sent'):
            return {"ok": False, "error": "该等级段榜单已经结算过"}

        # 获取榜单数据
        ranking_data = self.get_power_ranking(level_bracket, page=1, size=10)
        if not ranking_data.get("ok"):
            return {"ok": False, "error": "获取榜单失败"}

        rankings = ranking_data.get("rankings", [])
        if not rankings:
            return {"ok": False, "error": "该等级段暂无玩家"}

        # 获取奖励配置
        ann = self.get_announcement(activity_id)
        if not ann:
            return {"ok": False, "error": "活动配置不存在"}

        # 找到对应等级段的奖励
        bracket_config = None
        for r in ann.get("rankings", []):
            if r.get("level") == level_bracket:
                bracket_config = r
                break
        if not bracket_config:
            return {"ok": False, "error": "找不到该等级段的奖励配置"}

        rewards_config = bracket_config.get("rewards", [])
        now = datetime.now()

        # 开始发放奖励
        sent_count = 0
        for player in rankings[:10]:  # 只取前10名
            rank = player.get("rank", 0)
            user_id = player.get("userId")
            nickname = player.get("nickname", "")
            power = player.get("power", 0)

            # 确定奖励
            reward_items = self._get_reward_for_rank(rank, rewards_config)
            if not reward_items:
                continue

            # 检查是否已发放
            check_reward_sql = """
                SELECT id FROM activity_power_ranking_reward
                WHERE activity_id = %s AND level_bracket = %s AND rank_position = %s
            """
            existing_reward = execute_query(check_reward_sql, (activity_id, level_bracket, rank))
            if existing_reward:
                continue

            # 记录奖励
            insert_sql = """
                INSERT INTO activity_power_ranking_reward
                (activity_id, level_bracket, rank_position, user_id, nickname, combat_power, reward_items, is_claimed, finalized_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s)
            """
            execute_update(insert_sql, (
                activity_id, level_bracket, rank, user_id, nickname, power,
                json.dumps(reward_items, ensure_ascii=False), now
            ))

            # 发放奖励到玩家背包（实际物品ID需要根据配置映射）
            self._send_power_ranking_rewards(user_id, reward_items)
            sent_count += 1

        # 记录结算日志
        if not existing:
            insert_log_sql = """
                INSERT INTO activity_finalize_log
                (activity_id, level_bracket, finalize_type, finalized_at, is_rewards_sent, rewards_sent_at)
                VALUES (%s, %s, 'power_ranking', %s, 1, %s)
            """
            execute_update(insert_log_sql, (activity_id, level_bracket, now, now))
        else:
            update_log_sql = """
                UPDATE activity_finalize_log
                SET is_rewards_sent = 1, rewards_sent_at = %s, finalized_at = %s
                WHERE activity_id = %s AND level_bracket = %s AND finalize_type = 'power_ranking'
            """
            execute_update(update_log_sql, (now, now, activity_id, level_bracket))

        return {
            "ok": True,
            "message": f"已为{level_bracket}级战力榜前{sent_count}名发放奖励",
            "sent_count": sent_count
        }

    def _get_reward_for_rank(self, rank: int, rewards_config: list) -> Optional[str]:
        """根据排名获取奖励配置"""
        for reward in rewards_config:
            rank_str = reward.get("rank", "")
            if rank_str == f"第{rank}名":
                return reward.get("items")
            if rank_str.startswith("第") and "-" in rank_str:
                # 处理 "第4-10名" 格式
                try:
                    parts = rank_str.replace("第", "").replace("名", "").split("-")
                    min_rank, max_rank = int(parts[0]), int(parts[1])
                    if min_rank <= rank <= max_rank:
                        return reward.get("items")
                except:
                    pass
        return None

    def _send_power_ranking_rewards(self, user_id: int, reward_items: str):
        """发放战力榜奖励（简化版，主要是铜钱和元宝）"""
        if not self.player_repo:
            return

        try:
            player = self.player_repo.get_by_id(user_id)
            if not player:
                return

            # 解析奖励字符串，提取铜钱和元宝
            import re
            # 铜钱
            copper_match = re.search(r'铜钱(\d+)w', reward_items)
            if copper_match:
                copper = int(copper_match.group(1)) * 10000
                player.gold += copper

            # 元宝
            yuanbao_match = re.search(r'(\d+)元宝', reward_items)
            if yuanbao_match:
                yuanbao = int(yuanbao_match.group(1))
                if hasattr(player, 'yuanbao'):
                    player.yuanbao += yuanbao

            self.player_repo.save(player)
        except Exception as e:
            print(f"发放战力榜奖励失败: {e}")

    def check_power_ranking_finalized(self, level_bracket: int) -> bool:
        """检查指定等级段是否已结算"""
        sql = """
            SELECT is_rewards_sent FROM activity_finalize_log
            WHERE activity_id = 'power_ranking' AND level_bracket = %s AND finalize_type = 'power_ranking'
        """
        rows = execute_query(sql, (level_bracket,))
        return bool(rows and rows[0].get('is_rewards_sent'))

    # ==================== 轮盘抽奖 ====================

    # 抽奖物品池（对应配置中的奖品）- 使用items.json中的真实物品ID
    LOTTERY_ITEMS = [
        {"name": "铜钱×1w", "copper": 10000, "weight": 15},
        {"name": "铜钱×3w", "copper": 30000, "weight": 12},
        {"name": "铜钱×5w", "copper": 50000, "weight": 10},
        {"name": "追魂法宝×3", "item_id": 6019, "quantity": 3, "weight": 8},
        {"name": "重生丹×3", "item_id": 6017, "quantity": 3, "weight": 8},
        {"name": "招神财符×6", "item_id": 6004, "quantity": 6, "weight": 7},
        {"name": "化仙丹×6", "item_id": 6015, "quantity": 6, "weight": 7},
        {"name": "骰子包×6", "item_id": 6010, "quantity": 6, "weight": 7},
        {"name": "强力捕捉球×5", "item_id": 6011, "quantity": 5, "weight": 6},
        {"name": "金袋×6", "item_id": 6005, "quantity": 6, "weight": 6},
        {"name": "活力草×6", "item_id": 6013, "quantity": 6, "weight": 6},
        {"name": "凝神香×3", "item_id": 6009, "quantity": 3, "weight": 4},
        {"name": "魔纹布×6", "item_id": 6022, "quantity": 6, "weight": 3},
        {"name": "丝线×10", "item_id": 6023, "quantity": 10, "weight": 3},
    ]

    FRAGMENT_ITEM = {"name": "战灵灵石碎片", "fragment": 1}
    SINGLE_DRAW_COST = 600  # 单抽600元宝
    TEN_DRAW_COST = 5000  # 十连5000元宝

    def get_lottery_status(self, user_id: int) -> dict:
        """获取抽奖状态"""
        try:
            sql = """
                SELECT draw_count, fragment_count, round_count
                FROM activity_wheel_lottery
                WHERE user_id = %s AND activity_id = 'wheel_lottery'
            """
            rows = execute_query(sql, (user_id,))
            if rows:
                return {
                    "draw_count": rows[0].get("draw_count", 0),
                    "fragment_count": rows[0].get("fragment_count", 0),
                    "round_count": rows[0].get("round_count", 0),
                }
        except Exception:
            self._ensure_tables_exist()
        return {"draw_count": 0, "fragment_count": 0, "round_count": 0}

    def do_lottery(self, user_id: int, draw_type: str = "single") -> dict:
        """
        执行抽奖
        draw_type: "single" - 单抽, "ten" - 十连
        """
        print(f"[抽奖] 开始抽奖 user_id={user_id}, draw_type={draw_type}")
        try:
            if not self.is_activity_active("wheel_lottery"):
                print("[抽奖] 活动未开启或已结束")
                return {"ok": False, "error": "活动未开启或已结束"}

            if not self.player_repo:
                return {"ok": False, "error": "系统错误"}

            player = self.player_repo.get_by_id(user_id)
            if not player:
                return {"ok": False, "error": "玩家不存在"}

            # 计算费用和抽奖次数
            if draw_type == "ten":
                cost = self.TEN_DRAW_COST
                draw_times = 10
            else:
                cost = self.SINGLE_DRAW_COST
                draw_times = 1

            # 检查元宝
            yuanbao = getattr(player, 'yuanbao', 0) or 0
            if yuanbao < cost:
                return {"ok": False, "error": f"元宝不足，需要{cost}元宝"}

            # 扣除元宝
            player.yuanbao = yuanbao - cost
            self.player_repo.save(player)

            # 获取当前状态
            status = self.get_lottery_status(user_id)
            round_count = status.get("round_count", 0)
            fragment_count = status.get("fragment_count", 0)
            total_draw_count = status.get("draw_count", 0)

            # 执行抽奖
            rewards = []
            for i in range(draw_times):
                round_count += 1
                total_draw_count += 1

                # 每10抽必出一个碎片
                if round_count >= 10 or (draw_times == 10 and i == draw_times - 1 and round_count > 0):
                    # 在轮内随机位置出碎片（简化：最后一抽必出）
                    should_give_fragment = (round_count == 10)
                else:
                    should_give_fragment = False

                if should_give_fragment or (draw_times == 10 and random.random() < 0.1 and round_count <= 10):
                    # 出碎片
                    rewards.append({"name": "战灵灵石碎片", "fragment": 1})
                    fragment_count += 1
                    if round_count >= 10:
                        round_count = 0
                else:
                    # 随机抽取其他物品
                    reward = self._random_lottery_item()
                    rewards.append(reward)
                    self._send_lottery_reward(user_id, reward)

            # 保证十连至少有一个碎片
            if draw_times == 10:
                has_fragment = any(r.get("fragment") for r in rewards)
                if not has_fragment:
                    # 替换最后一个为碎片
                    rewards[-1] = {"name": "战灵灵石碎片", "fragment": 1}
                    fragment_count += 1
                round_count = 0

            # 更新数据库
            print(f"[抽奖] 更新数据库状态")
            self._update_lottery_status(user_id, total_draw_count, fragment_count, round_count)

            result = {
                "ok": True,
                "rewards": rewards,
                "fragment_count": fragment_count,
                "draw_count": total_draw_count,
                "cost": cost,
            }
            print(f"[抽奖] 抽奖成功，返回结果: {result}")
            return result
        except Exception as e:
            import traceback
            print(f"[抽奖] 抽奖执行异常: {e}")
            traceback.print_exc()
            return {"ok": False, "error": "抽奖执行异常，请重试"}

    def _random_lottery_item(self) -> dict:
        """随机抽取物品"""
        total_weight = sum(item.get("weight", 1) for item in self.LOTTERY_ITEMS)
        r = random.random() * total_weight
        cumulative = 0
        for item in self.LOTTERY_ITEMS:
            cumulative += item.get("weight", 1)
            if r <= cumulative:
                # 返回需要的字段（不包含weight）
                result = {"name": item["name"]}
                if item.get("copper"):
                    result["copper"] = item["copper"]
                if item.get("item_id"):
                    result["item_id"] = item["item_id"]
                    result["quantity"] = item.get("quantity", 1)
                return result
        # 默认返回最后一个
        item = self.LOTTERY_ITEMS[-1]
        result = {"name": item["name"]}
        if item.get("copper"):
            result["copper"] = item["copper"]
        if item.get("item_id"):
            result["item_id"] = item["item_id"]
            result["quantity"] = item.get("quantity", 1)
        return result

    def _send_lottery_reward(self, user_id: int, reward: dict):
        """发放抽奖奖励"""
        if not self.player_repo:
            return

        try:
            # 铜钱
            if reward.get("copper"):
                player = self.player_repo.get_by_id(user_id)
                if player:
                    player.gold += reward["copper"]
                    self.player_repo.save(player)

            # 物品
            if reward.get("item_id") and self.inventory_service:
                qty = reward.get("quantity", 1)
                self.inventory_service.add_item(user_id, reward["item_id"], qty)
        except Exception as e:
            print(f"发放抽奖奖励失败: {e}")

    def _update_lottery_status(self, user_id: int, draw_count: int, fragment_count: int, round_count: int):
        """更新抽奖状态"""
        now = datetime.now()
        sql = """
            INSERT INTO activity_wheel_lottery
            (user_id, activity_id, draw_count, fragment_count, round_count, last_draw_at)
            VALUES (%s, 'wheel_lottery', %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            draw_count = VALUES(draw_count),
            fragment_count = VALUES(fragment_count),
            round_count = VALUES(round_count),
            last_draw_at = VALUES(last_draw_at)
        """
        try:
            execute_update(sql, (user_id, draw_count, fragment_count, round_count, now))
        except Exception:
            self._ensure_tables_exist()
            try:
                execute_update(sql, (user_id, draw_count, fragment_count, round_count, now))
            except Exception as e:
                print(f"更新抽奖状态失败: {e}")

    def exchange_fragment(self, user_id: int, exchange_type: str) -> dict:
        """
        碎片兑换
        exchange_type: "earth"(土), "fire"(火), "water"(水), "wood"(木), "gold"(金), "god"(神)
        """
        # 兑换配置 - 使用items.json中的真实物品ID
        EXCHANGE_CONFIG = {
            "earth": {"cost": 1, "name": "土灵石", "item_id": 7101},
            "fire": {"cost": 3, "name": "火灵石", "item_id": 7102},
            "water": {"cost": 6, "name": "水灵石", "item_id": 7103},
            "wood": {"cost": 12, "name": "木灵石", "item_id": 7104},
            "gold": {"cost": 30, "name": "金灵石", "item_id": 7105},
            "god": {"cost": 80, "name": "神灵石", "item_id": 7106, "limit": 2},
        }

        config = EXCHANGE_CONFIG.get(exchange_type)
        if not config:
            return {"ok": False, "error": "无效的兑换类型"}

        status = self.get_lottery_status(user_id)
        fragment_count = status.get("fragment_count", 0)

        if fragment_count < config["cost"]:
            return {"ok": False, "error": f"碎片不足，需要{config['cost']}个"}

        # 检查神灵石限购
        if exchange_type == "god":
            limit = config.get("limit", 2)
            claimed = self._get_claim_count(user_id, "wheel_lottery", f"exchange_god")
            if claimed >= limit:
                return {"ok": False, "error": f"神灵石限购{limit}个，已达上限"}

        # 扣除碎片
        new_fragment = fragment_count - config["cost"]
        sql = """
            UPDATE activity_wheel_lottery
            SET fragment_count = %s
            WHERE user_id = %s AND activity_id = 'wheel_lottery'
        """
        execute_update(sql, (new_fragment, user_id))

        # 发放物品
        if self.inventory_service:
            self.inventory_service.add_item(user_id, config["item_id"], 1)

        # 记录神灵石兑换次数
        if exchange_type == "god":
            self._record_claim(user_id, "wheel_lottery", "exchange_god")

        return {
            "ok": True,
            "message": f"成功兑换{config['name']}×1",
            "item_name": config["name"],
            "fragment_count": new_fragment,
        }

    # ==================== 铜钱圣典 ====================

    def buy_copper_book(self, user_id: int) -> dict:
        """购买铜钱圣典礼盒"""
        if not self.is_activity_active("copper_book"):
            return {"ok": False, "error": "活动未开启或已结束"}

        ann = self.get_announcement("copper_book")
        if not ann:
            return {"ok": False, "error": "活动配置不存在"}

        price = ann.get("price", 2188)
        reward_copper = ann.get("reward_copper", 2880000)
        daily_limit = ann.get("daily_limit", 4)

        # 检查每日购买次数
        today = date.today()
        bought_today = self._get_daily_claim_count(user_id, "copper_book", "buy", today)
        if bought_today >= daily_limit:
            return {"ok": False, "error": f"今日已购买{daily_limit}次，达到上限"}

        # 检查元宝
        if not self.player_repo:
            return {"ok": False, "error": "系统错误"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        yuanbao = getattr(player, 'yuanbao', 0) or 0
        if yuanbao < price:
            return {"ok": False, "error": f"元宝不足，需要{price}元宝"}

        # 扣除元宝，增加铜钱
        player.yuanbao = yuanbao - price
        player.gold += reward_copper
        self.player_repo.save(player)

        # 记录购买
        self._record_daily_claim(user_id, "copper_book", "buy", today)

        return {
            "ok": True,
            "message": f"成功购买铜钱圣典礼盒，获得{reward_copper // 10000}w铜钱",
            "copper_gained": reward_copper,
            "bought_today": bought_today + 1,
            "daily_limit": daily_limit,
        }

    # ==================== 声望助力庆典 ====================

    def claim_prestige_free(self, user_id: int) -> dict:
        """领取免费声望石（发放到背包，使用后增加声望）"""
        if not self.is_activity_active("prestige_boost"):
            return {"ok": False, "error": "活动未开启或已结束"}

        # 检查是否已领取
        claimed = self._get_claim_count(user_id, "prestige_boost", "free_prestige_stone")
        if claimed > 0:
            return {"ok": False, "error": "已领取过"}

        if not self.player_repo:
            return {"ok": False, "error": "系统错误"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 发放声望石×6到背包（物品ID 12001）
        PRESTIGE_STONE_ID = 12001
        if self.inventory_service:
            try:
                self.inventory_service.add_item(user_id, PRESTIGE_STONE_ID, 6)
            except Exception as e:
                print(f"发放声望石失败: {e}")
                return {"ok": False, "error": "发放物品失败，请重试"}
        else:
            return {"ok": False, "error": "系统错误，无法发放物品"}

        # 记录领取
        self._record_claim(user_id, "prestige_boost", "free_prestige_stone")

        return {
            "ok": True,
            "message": "成功领取声望石×6！请在背包中使用",
        }

    def buy_prestige_box(self, user_id: int) -> dict:
        """购买声望礼盒"""
        if not self.is_activity_active("prestige_boost"):
            return {"ok": False, "error": "活动未开启或已结束"}

        price = 2588
        prestige_reward = 5000
        daily_limit = 4

        # 检查每日购买次数
        today = date.today()
        bought_today = self._get_daily_claim_count(user_id, "prestige_boost", "buy_box", today)
        if bought_today >= daily_limit:
            return {"ok": False, "error": f"今日已购买{daily_limit}次，达到上限"}

        # 检查等级要求（50级及以下）
        if not self.player_repo:
            return {"ok": False, "error": "系统错误"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        if player.level > 50:
            return {"ok": False, "error": "50级以上无法购买"}

        yuanbao = getattr(player, 'yuanbao', 0) or 0
        if yuanbao < price:
            return {"ok": False, "error": f"元宝不足，需要{price}元宝"}

        # 扣除元宝，增加声望
        player.yuanbao = yuanbao - price
        if hasattr(player, 'prestige'):
            player.prestige += prestige_reward
        self.player_repo.save(player)

        # 记录购买
        self._record_daily_claim(user_id, "prestige_boost", "buy_box", today)

        return {
            "ok": True,
            "message": f"成功购买声望礼盒，获得{prestige_reward}声望",
            "prestige_gained": prestige_reward,
            "bought_today": bought_today + 1,
            "daily_limit": daily_limit,
        }

    # ==================== 霸王龙预登场 ====================

    def claim_tyrannosaurus_ball(self, user_id: int, ball_level: int) -> dict:
        """领取霸王龙召唤球"""
        if not self.is_activity_active("tyrannosaurus_preview"):
            return {"ok": False, "error": "活动未开启或已结束"}

        ann = self.get_announcement("tyrannosaurus_preview")
        if not ann:
            return {"ok": False, "error": "活动配置不存在"}

        required_gems = ann.get("required_gems", 300)

        # 检查是否已领取
        claimed = self._get_claim_count(user_id, "tyrannosaurus_preview", "claim_ball")
        if claimed > 0:
            return {"ok": False, "error": "已领取过霸王龙召唤球"}

        # 检查赞助宝石（累计充值）
        if not self.player_repo:
            return {"ok": False, "error": "系统错误"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 获取累计赞助宝石（这里简化处理，假设silver_diamond就是累计宝石）
        total_gems = getattr(player, 'silver_diamond', 0) or 0
        if total_gems < required_gems:
            return {"ok": False, "error": f"累计赞助宝石不足{required_gems}，当前{total_gems}"}

        # 验证选择的球等级并获取对应的物品ID
        ball_config = {
            20: {"item_id": 95001, "name": "霸王龙Ⅰ(绝版)召唤球"},
            30: {"item_id": 95002, "name": "霸王龙Ⅱ(绝版)召唤球"},
            40: {"item_id": 95003, "name": "霸王龙Ⅲ(绝版)召唤球"},
            50: {"item_id": 95004, "name": "霸王龙Ⅳ(绝版)召唤球"},
            60: {"item_id": 95005, "name": "霸王龙Ⅴ(绝版)召唤球"},
            70: {"item_id": 95006, "name": "霸王龙Ⅵ(绝版)召唤球"},
        }
        
        if ball_level not in ball_config:
            return {"ok": False, "error": "无效的召唤球等级"}

        config = ball_config[ball_level]
        
        # 发放召唤球到背包
        if self.inventory_service:
            try:
                self.inventory_service.add_item(user_id, config["item_id"], 1)
            except Exception as e:
                print(f"发放霸王龙召唤球失败: {e}")
                return {"ok": False, "error": "发放物品失败，请重试"}
        else:
            return {"ok": False, "error": "系统错误，无法发放物品"}

        # 记录领取
        self._record_claim(user_id, "tyrannosaurus_preview", "claim_ball", json.dumps({"level": ball_level}))

        return {
            "ok": True,
            "message": f"成功领取{config['name']}！该物品不可直接使用，请等待正式登场后开放",
            "ball_level": ball_level,
        }

    # ==================== 元宝返利 ====================

    def claim_yuanbao_rebate(self, user_id: int, tier_gems: int) -> dict:
        """领取元宝返利"""
        if not self.is_activity_active("yuanbao_rebate"):
            return {"ok": False, "error": "活动未开启或已结束"}

        ann = self.get_announcement("yuanbao_rebate")
        if not ann:
            return {"ok": False, "error": "活动配置不存在"}

        # 找到对应档位
        tier_config = None
        for tier in ann.get("tiers", []):
            if tier.get("gems_required") == tier_gems:
                tier_config = tier
                break

        if not tier_config:
            return {"ok": False, "error": "无效的返利档位"}

        # 检查今日是否已领取该档位
        today = date.today()
        claim_key = f"rebate_{tier_gems}"
        claimed_today = self._get_daily_claim_count(user_id, "yuanbao_rebate", claim_key, today)
        if claimed_today > 0:
            return {"ok": False, "error": "今日已领取该档位返利"}

        # 检查玩家赞助宝石
        if not self.player_repo:
            return {"ok": False, "error": "系统错误"}

        player = self.player_repo.get_by_id(user_id)
        if not player:
            return {"ok": False, "error": "玩家不存在"}

        # 检查今日赞助宝石（这里简化，假设有daily_gems字段或用累计）
        # 实际应该有专门的充值记录表
        total_gems = getattr(player, 'silver_diamond', 0) or 0
        if total_gems < tier_gems:
            return {"ok": False, "error": f"今日赞助宝石不足{tier_gems}"}

        # 发放元宝
        yuanbao_reward = tier_config.get("yuanbao_reward", 0)
        if hasattr(player, 'yuanbao'):
            player.yuanbao = (player.yuanbao or 0) + yuanbao_reward
            self.player_repo.save(player)

        # 记录领取
        self._record_daily_claim(user_id, "yuanbao_rebate", claim_key, today)

        return {
            "ok": True,
            "message": f"成功领取{yuanbao_reward}元宝返利",
            "yuanbao_gained": yuanbao_reward,
        }

    # ==================== 通用辅助方法 ====================

    def _ensure_tables_exist(self):
        """确保活动相关表存在"""
        try:
            # 创建 activity_claims 表
            execute_update("""
                CREATE TABLE IF NOT EXISTS activity_claims (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    activity_id VARCHAR(50) NOT NULL,
                    claim_key VARCHAR(100) NOT NULL,
                    claim_date DATE DEFAULT NULL,
                    claim_count INT DEFAULT 1,
                    extra_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_user_activity_claim (user_id, activity_id, claim_key, claim_date),
                    INDEX idx_user_activity (user_id, activity_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            # 创建 activity_wheel_lottery 表
            execute_update("""
                CREATE TABLE IF NOT EXISTS activity_wheel_lottery (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    activity_id VARCHAR(50) NOT NULL DEFAULT 'wheel_lottery',
                    draw_count INT DEFAULT 0,
                    fragment_count INT DEFAULT 0,
                    round_count INT DEFAULT 0,
                    last_draw_at DATETIME DEFAULT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_user_activity (user_id, activity_id),
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        except Exception as e:
            print(f"创建活动表失败: {e}")

    def _get_claim_count(self, user_id: int, activity_id: str, claim_key: str) -> int:
        """获取领取次数"""
        try:
            sql = """
                SELECT COALESCE(SUM(claim_count), 0) as total
                FROM activity_claims
                WHERE user_id = %s AND activity_id = %s AND claim_key = %s
            """
            rows = execute_query(sql, (user_id, activity_id, claim_key))
            return int(rows[0].get("total", 0)) if rows else 0
        except Exception:
            self._ensure_tables_exist()
            return 0

    def _get_daily_claim_count(self, user_id: int, activity_id: str, claim_key: str, claim_date: date) -> int:
        """获取每日领取次数"""
        try:
            sql = """
                SELECT COALESCE(SUM(claim_count), 0) as total
                FROM activity_claims
                WHERE user_id = %s AND activity_id = %s AND claim_key = %s AND claim_date = %s
            """
            rows = execute_query(sql, (user_id, activity_id, claim_key, claim_date))
            return int(rows[0].get("total", 0)) if rows else 0
        except Exception:
            self._ensure_tables_exist()
            return 0

    def _record_claim(self, user_id: int, activity_id: str, claim_key: str, extra_data: str = None):
        """记录领取"""
        try:
            sql = """
                INSERT INTO activity_claims (user_id, activity_id, claim_key, claim_count, extra_data)
                VALUES (%s, %s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE claim_count = claim_count + 1
            """
            execute_update(sql, (user_id, activity_id, claim_key, extra_data))
        except Exception:
            self._ensure_tables_exist()
            try:
                execute_update(sql, (user_id, activity_id, claim_key, extra_data))
            except Exception as e:
                print(f"记录领取失败: {e}")

    def _record_daily_claim(self, user_id: int, activity_id: str, claim_key: str, claim_date: date):
        """记录每日领取"""
        try:
            sql = """
                INSERT INTO activity_claims (user_id, activity_id, claim_key, claim_date, claim_count)
                VALUES (%s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE claim_count = claim_count + 1
            """
            execute_update(sql, (user_id, activity_id, claim_key, claim_date))
        except Exception:
            self._ensure_tables_exist()
            try:
                execute_update(sql, (user_id, activity_id, claim_key, claim_date))
            except Exception as e:
                print(f"记录每日领取失败: {e}")


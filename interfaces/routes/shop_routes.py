# interfaces/routes/shop_routes.py
"""商城系统路由"""

import json
import math
import os
from datetime import date

from flask import Blueprint, request, jsonify, session

from infrastructure.db.connection import execute_query, execute_update, get_connection
from infrastructure.config.item_repo_from_config import ConfigItemRepo

shop_bp = Blueprint('shop', __name__, url_prefix='/api/shop')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def load_shop_config():
    """加载商城配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'shop.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@shop_bp.get("/categories")
def get_categories():
    """获取商城分类列表"""
    config = load_shop_config()
    return jsonify({
        "ok": True,
        "categories": config.get("categories", [])
    })


@shop_bp.get("/item/<int:item_id>")
def get_item_detail(item_id):
    """获取单个商品详情"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    config = load_shop_config()
    
    # 查找商品
    shop_item = None
    for item in config.get("items", []):
        if item.get("id") == item_id:
            shop_item = item
            break
    
    if not shop_item:
        return jsonify({"ok": False, "error": "商品不存在"})
    
    # 验证物品模板是否存在
    item_id = shop_item.get("item_id", 0)
    if item_id:
        item_repo = ConfigItemRepo()
        item_template = item_repo.get_by_id(item_id)
        if not item_template:
            return jsonify({"ok": False, "error": f"商品配置错误：物品ID {item_id} 不存在"})

    # 每日限购信息（详情页仅返回信息，不在这里做购买数量校验）
    daily_limit = shop_item.get("daily_limit")
    try:
        daily_limit = int(daily_limit) if daily_limit is not None else None
    except (TypeError, ValueError):
        daily_limit = None

    bought_today = 0
    if daily_limit is not None and daily_limit > 0:
        today = date.today()
        execute_update(
            """
            CREATE TABLE IF NOT EXISTS player_shop_daily_purchase (
                user_id INT NOT NULL,
                shop_item_id INT NOT NULL,
                purchase_date DATE NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, shop_item_id, purchase_date)
            )
            """
        )
        rows = execute_query(
            "SELECT quantity FROM player_shop_daily_purchase WHERE user_id = %s AND shop_item_id = %s AND purchase_date = %s",
            (user_id, item_id, today),
        )
        bought_today = int(rows[0].get("quantity", 0) or 0) if rows else 0
    
    # 获取货币类型
    category = shop_item.get("category", "copper")
    currency = "gold"
    for cat in config.get("categories", []):
        if cat.get("key") == category:
            currency = cat.get("currency", "gold")
            break
    
    # 获取玩家货币
    player_rows = execute_query(
        "SELECT gold, yuanbao FROM player WHERE user_id = %s",
        (user_id,)
    )
    gold = 0
    yuanbao = 0
    if player_rows:
        gold = player_rows[0].get('gold', 0) or 0
        yuanbao = player_rows[0].get('yuanbao', 0) or 0
    
    return jsonify({
        "ok": True,
        "item": shop_item,
        "currency": currency,
        "gold": gold,
        "yuanbao": yuanbao,
        "daily_limit": daily_limit,
        "bought_today": bought_today,
    })


@shop_bp.get("/items")
def get_items():
    """获取商品列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    category = request.args.get('category', 'copper')
    
    config = load_shop_config()
    items = [
        item for item in config.get("items", [])
        if item.get("category") == category
    ]
    
    # 获取玩家货币
    player_rows = execute_query(
        "SELECT gold, yuanbao FROM player WHERE user_id = %s",
        (user_id,)
    )
    gold = 0
    yuanbao = 0
    if player_rows:
        gold = player_rows[0].get('gold', 0) or 0
        yuanbao = player_rows[0].get('yuanbao', 0) or 0
    
    # 获取当前分类的货币类型
    currency = "gold"
    for cat in config.get("categories", []):
        if cat.get("key") == category:
            currency = cat.get("currency", "gold")
            break
    
    return jsonify({
        "ok": True,
        "category": category,
        "currency": currency,
        "items": items,
        "gold": gold,
        "yuanbao": yuanbao,
    })


@shop_bp.post("/buy")
def buy_item():
    """购买商品 - 使用事务确保原子性，避免扣款成功但购买失败的情况"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    try:
        shop_item_id = int(data.get("shop_item_id", 0) or 0)
    except Exception:
        shop_item_id = 0
    try:
        quantity = int(data.get("quantity", 1) or 1)
    except Exception:
        quantity = 1
    
    if not shop_item_id:
        return jsonify({"ok": False, "error": "请选择商品"}), 400
    
    if quantity < 1:
        return jsonify({"ok": False, "error": "购买数量无效"}), 400
    
    # 查找商品配置（事务外，只读操作）
    config = load_shop_config()
    shop_item = None
    for item in config.get("items", []):
        if item.get("id") == shop_item_id:
            shop_item = item
            break
    
    if not shop_item:
        return jsonify({"ok": False, "error": "商品不存在"}), 400
    
    # 获取货币类型
    category = shop_item.get("category", "copper")
    currency = "gold"
    for cat in config.get("categories", []):
        if cat.get("key") == category:
            currency = cat.get("currency", "gold")
            break
    
    # 计算总价和物品ID
    total_price = int(shop_item.get("price", 0) or 0) * quantity
    item_id = int(shop_item.get("item_id", 0) or 0)
    if item_id <= 0:
        return jsonify({"ok": False, "error": "商品配置错误"}), 400
    
    # 验证物品模板是否存在
    item_repo = ConfigItemRepo()
    item_template = item_repo.get_by_id(item_id)
    if not item_template:
        return jsonify({"ok": False, "error": f"商品配置错误：物品ID {item_id} 不存在"}), 400
    
    # 每日限购配置
    daily_limit = shop_item.get("daily_limit")
    try:
        daily_limit = int(daily_limit) if daily_limit is not None else None
    except (TypeError, ValueError):
        daily_limit = None
    
    # 确保每日限购表存在（事务外，只执行一次）
    if daily_limit is not None and daily_limit > 0:
        try:
            execute_update(
                """
                CREATE TABLE IF NOT EXISTS player_shop_daily_purchase (
                    user_id INT NOT NULL,
                    shop_item_id INT NOT NULL,
                    purchase_date DATE NOT NULL,
                    quantity INT NOT NULL DEFAULT 0,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, shop_item_id, purchase_date)
                )
                """
            )
        except Exception:
            pass  # 表已存在，忽略错误
    
    # 开始事务：所有检查和操作都在事务内完成
    conn = get_connection()
    conn.autocommit = False  # 禁用自动提交，启用事务模式
    error_msg = None
    try:
        with conn.cursor() as cursor:
            # 1. 锁定玩家记录，检查货币（FOR UPDATE 防止并发）
            cursor.execute("SELECT gold, yuanbao FROM player WHERE user_id = %s FOR UPDATE", (user_id,))
            player_row = cursor.fetchone()
            if not player_row:
                error_msg = "玩家不存在"
                raise Exception(error_msg)
            
            player_gold = player_row.get("gold", 0) or 0
            player_yuanbao = player_row.get("yuanbao", 0) or 0
            
            # 2. 检查货币是否足够（在扣款前检查）
            if currency == "gold" and player_gold < total_price:
                error_msg = "铜钱不足"
                raise Exception(error_msg)
            if currency == "yuanbao" and player_yuanbao < total_price:
                error_msg = "元宝不足"
                raise Exception(error_msg)
            
            # 3. 检查每日限购（在事务内检查，使用FOR UPDATE防止并发）
            if daily_limit is not None and daily_limit > 0:
                today = date.today()
                cursor.execute(
                    """
                    SELECT quantity FROM player_shop_daily_purchase 
                    WHERE user_id = %s AND shop_item_id = %s AND purchase_date = %s 
                    FOR UPDATE
                    """,
                    (user_id, shop_item_id, today),
                )
                purchase_row = cursor.fetchone()
                bought_today = int(purchase_row.get("quantity", 0) or 0) if purchase_row else 0
                
                if bought_today + quantity > daily_limit:
                    error_msg = f"该商品每日限购{daily_limit}个，今日已购{bought_today}个"
                    raise Exception(error_msg)
            
            # 4. 检查背包容量（在添加物品前检查，使用正确的容量计算方法）
            # 获取背包容量
            cursor.execute("SELECT capacity FROM player_bag WHERE user_id = %s", (user_id,))
            bag_row = cursor.fetchone()
            capacity = bag_row.get("capacity", 100) or 100 if bag_row else 100
            
            # 计算实际占用的容量（1容量最多容纳99个同类道具）
            MAX_STACK = 99
            cursor.execute(
                """
                SELECT item_id, quantity, is_temporary 
                FROM player_inventory 
                WHERE user_id = %s AND is_temporary = 0
                """,
                (user_id,)
            )
            all_items = cursor.fetchall()
            
            # 获取物品模板信息（检查是否可堆叠）
            item_repo = ConfigItemRepo()
            item_template = item_repo.get_by_id(item_id)
            is_stackable = item_template.stackable if item_template else True
            
            # 计算当前已占用的容量
            used_slots = 0
            for inv_item in all_items:
                inv_item_id = inv_item.get("item_id")
                inv_quantity = inv_item.get("quantity", 0) or 0
                inv_template = item_repo.get_by_id(inv_item_id)
                if not inv_template or not inv_template.stackable:
                    # 不可堆叠，每个占用1容量
                    used_slots += inv_quantity
                else:
                    # 可堆叠物品：根据容量上限（99）计算占用容量
                    slots_needed = math.ceil(inv_quantity / MAX_STACK)
                    used_slots += slots_needed
            
            # 计算添加物品后需要的额外容量
            if is_stackable:
                # 检查是否已有该物品
                cursor.execute(
                    "SELECT id, quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
                    (user_id, item_id)
                )
                existing_items = cursor.fetchall()
                
                if existing_items:
                    # 已有该物品，计算可以堆叠到现有格子的数量
                    total_existing = sum(item.get("quantity", 0) or 0 for item in existing_items)
                    total_after = total_existing + quantity
                    # 计算需要的总容量
                    total_slots_needed = math.ceil(total_after / MAX_STACK)
                    # 计算当前该物品占用的容量
                    current_slots = math.ceil(total_existing / MAX_STACK)
                    # 需要的额外容量
                    additional_slots = total_slots_needed - current_slots
                else:
                    # 没有该物品，需要新格子
                    additional_slots = math.ceil(quantity / MAX_STACK)
            else:
                # 不可堆叠，每个占用1容量
                additional_slots = quantity
            
            # 检查背包是否有足够空间
            if used_slots + additional_slots > capacity:
                error_msg = "背包已满，无法购买"
                raise Exception(error_msg)
            
            # 5. 所有检查通过，开始执行购买操作
            
            # 5.1 扣除货币
            if currency == "gold":
                cursor.execute("UPDATE player SET gold = gold - %s WHERE user_id = %s", (total_price, user_id))
            else:
                cursor.execute("UPDATE player SET yuanbao = yuanbao - %s WHERE user_id = %s", (total_price, user_id))
            
            # 5.2 添加物品到背包（正确处理99的限制和拆分）
            # 先尝试填充已有的未满99的格子
            remaining_quantity = quantity
            if is_stackable:
                cursor.execute(
                    "SELECT id, quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
                    (user_id, item_id)
                )
                existing_items = cursor.fetchall()
                
                for existing in existing_items:
                    if remaining_quantity <= 0:
                        break
                    existing_quantity = existing.get("quantity", 0) or 0
                    if existing_quantity < MAX_STACK:
                        space = MAX_STACK - existing_quantity
                        add_amount = min(space, remaining_quantity)
                        new_quantity = existing_quantity + add_amount
                        cursor.execute(
                            "UPDATE player_inventory SET quantity = %s WHERE id = %s",
                            (new_quantity, existing.get("id"))
                        )
                        remaining_quantity -= add_amount
            
            # 如果还有剩余，创建新的格子（每个最多99）
            # 先确保没有唯一约束（允许同一物品占用多个格子）
            try:
                cursor.execute("ALTER TABLE player_inventory DROP INDEX uk_user_item_temp")
            except Exception:
                pass  # 约束不存在或已删除，忽略错误
            
            while remaining_quantity > 0:
                add_amount = min(MAX_STACK, remaining_quantity)
                try:
                    cursor.execute(
                        """
                        INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary, created_at)
                        VALUES (%s, %s, %s, 0, NOW())
                        """,
                        (user_id, item_id, add_amount),
                    )
                    remaining_quantity -= add_amount
                except Exception as insert_error:
                    # 如果插入失败（可能是唯一约束冲突），抛出错误，事务会回滚
                    error_msg = f"添加物品失败: {str(insert_error)}"
                    raise Exception(error_msg)
            
            # 5.3 更新每日限购记录
            if daily_limit is not None and daily_limit > 0:
                today = date.today()
                cursor.execute(
                    """
                    INSERT INTO player_shop_daily_purchase (user_id, shop_item_id, purchase_date, quantity)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
                    """,
                    (user_id, shop_item_id, today, quantity),
                )
            
            # 6. 获取更新后的货币（用于返回）
            cursor.execute("SELECT gold, yuanbao FROM player WHERE user_id = %s", (user_id,))
            updated_player = cursor.fetchone()
            new_gold = updated_player.get("gold", 0) or 0 if updated_player else 0
            new_yuanbao = updated_player.get("yuanbao", 0) or 0 if updated_player else 0
            
            # 7. 提交事务
            conn.commit()
            
            currency_name = "铜钱" if currency == "gold" else "元宝"
            return jsonify({
                "ok": True,
                "message": f"购买成功！花费{total_price}{currency_name}，获得{shop_item.get('name')}x{quantity}",
                "gold": new_gold,
                "yuanbao": new_yuanbao,
            })
            
    except Exception as e:
        # 任何错误都回滚事务
        try:
            conn.rollback()
        except Exception:
            pass
        
        # 返回错误信息
        error_msg = error_msg or str(e) or "购买失败"
        return jsonify({"ok": False, "error": error_msg}), 400
    finally:
        try:
            conn.close()
        except Exception:
            pass

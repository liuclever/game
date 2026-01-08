# interfaces/routes/shop_routes.py
"""商城系统路由"""

import json
import os
from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query, execute_update
from datetime import date

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

    # 每日限购
    daily_limit = shop_item.get("daily_limit")
    if daily_limit is not None:
        try:
            daily_limit = int(daily_limit)
        except (TypeError, ValueError):
            daily_limit = None

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
            (user_id, shop_item_id, today),
        )
        bought_today = int(rows[0].get("quantity", 0) or 0) if rows else 0
        if bought_today + int(quantity) > daily_limit:
            return jsonify({
                "ok": False,
                "error": f"该商品每日限购{daily_limit}个，今日已购{bought_today}个",
            }), 400
    
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
    """购买商品"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    shop_item_id = data.get('shop_item_id')
    quantity = data.get('quantity', 1)
    
    if not shop_item_id:
        return jsonify({"ok": False, "error": "请选择商品"})
    
    if quantity < 1:
        return jsonify({"ok": False, "error": "购买数量无效"})
    
    # 查找商品配置
    config = load_shop_config()
    shop_item = None
    for item in config.get("items", []):
        if item.get("id") == shop_item_id:
            shop_item = item
            break
    
    if not shop_item:
        return jsonify({"ok": False, "error": "商品不存在"})
    
    # 获取货币类型
    category = shop_item.get("category", "copper")
    currency = "gold"
    for cat in config.get("categories", []):
        if cat.get("key") == category:
            currency = cat.get("currency", "gold")
            break
    
    # 计算总价
    total_price = shop_item.get("price", 0) * quantity
    
    # 检查玩家货币
    player_rows = execute_query(
        "SELECT gold, yuanbao FROM player WHERE user_id = %s",
        (user_id,)
    )
    if not player_rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_gold = player_rows[0].get('gold', 0) or 0
    player_yuanbao = player_rows[0].get('yuanbao', 0) or 0
    
    if currency == "gold" and player_gold < total_price:
        return jsonify({"ok": False, "error": "铜钱不足"})
    elif currency == "yuanbao" and player_yuanbao < total_price:
        return jsonify({"ok": False, "error": "元宝不足"})
    
    # 扣除货币
    if currency == "gold":
        execute_update(
            "UPDATE player SET gold = gold - %s WHERE user_id = %s",
            (total_price, user_id)
        )
    else:
        execute_update(
            "UPDATE player SET yuanbao = yuanbao - %s WHERE user_id = %s",
            (total_price, user_id)
        )
    
    # 发放物品
    item_id = shop_item.get("item_id")
    execute_update(
        """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
           VALUES (%s, %s, %s, 0)
           ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
        (user_id, item_id, quantity, quantity)
    )

    if daily_limit is not None and daily_limit > 0:
        today = date.today()
        execute_update(
            """
            INSERT INTO player_shop_daily_purchase (user_id, shop_item_id, purchase_date, quantity)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """,
            (user_id, shop_item_id, today, int(quantity)),
        )
    
    # 获取更新后的货币
    player_rows = execute_query(
        "SELECT gold, yuanbao FROM player WHERE user_id = %s",
        (user_id,)
    )
    new_gold = player_rows[0].get('gold', 0) or 0 if player_rows else 0
    new_yuanbao = player_rows[0].get('yuanbao', 0) or 0 if player_rows else 0
    
    currency_name = "铜钱" if currency == "gold" else "元宝"
    
    return jsonify({
        "ok": True,
        "message": f"购买成功！花费{total_price}{currency_name}，获得{shop_item.get('name')}x{quantity}",
        "gold": new_gold,
        "yuanbao": new_yuanbao,
    })

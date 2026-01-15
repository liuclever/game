# interfaces/routes/pay_routes.py
"""支付充值路由 - 充值宝石"""

import json
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session, redirect
from infrastructure.db.connection import execute_query, execute_update

pay_bp = Blueprint('pay', __name__, url_prefix='/api/pay')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def load_recharge_products():
    """加载充值商品配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'recharge_products.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_vip_privileges():
    """加载VIP配置"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'vip_privileges.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calc_vip_level(diamond_spent: int) -> int:
    """根据累计消耗宝石数计算VIP等级"""
    vip_config = load_vip_privileges()
    vip_level = 0
    for lv in vip_config.get('vip_levels', []):
        if diamond_spent >= lv.get('required_diamond', 0):
            vip_level = lv.get('level', 0)
    return vip_level


@pay_bp.get('/products')
def get_products():
    """获取充值商品列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    config = load_recharge_products()
    products = config.get('products', [])
    exchange_rate = config.get('exchange_rate', 100)
    
    # 查询用户首充状态
    rows = execute_query(
        "SELECT first_recharge_claimed, silver_diamond, yuanbao, vip_level, diamond_spent FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    first_recharge_claimed = 0
    silver_diamond = 0
    yuanbao = 0
    vip_level = 0
    diamond_spent = 0
    
    if rows:
        first_recharge_claimed = rows[0].get('first_recharge_claimed', 0) or 0
        silver_diamond = rows[0].get('silver_diamond', 0) or 0
        yuanbao = rows[0].get('yuanbao', 0) or 0
        vip_level = rows[0].get('vip_level', 0) or 0
        diamond_spent = rows[0].get('diamond_spent', 0) or 0
    
    return jsonify({
        'ok': True,
        'products': products,
        'exchange_rate': exchange_rate,
        'first_recharge_available': first_recharge_claimed == 0,
        'silver_diamond': silver_diamond,
        'yuanbao': yuanbao,
        'vip_level': vip_level,
        'diamond_spent': diamond_spent,
    })


@pay_bp.post('/create-order')
def create_order():
    """创建支付订单"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    product_id = data.get('product_id')
    pay_type = data.get('pay_type', 'page')  # page=电脑网页, wap=手机网页
    
    # 查找商品
    config = load_recharge_products()
    product = None
    for p in config.get('products', []):
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        return jsonify({'ok': False, 'error': '商品不存在'}), 400
    
    # 获取支付宝客户端
    try:
        from infrastructure.alipay import get_alipay_client, generate_out_trade_no
        client = get_alipay_client()
        if not client:
            return jsonify({'ok': False, 'error': '支付服务暂不可用'}), 500
    except Exception as e:
        return jsonify({'ok': False, 'error': f'支付服务初始化失败: {str(e)}'}), 500
    
    # 生成订单号
    out_trade_no = generate_out_trade_no(f"U{user_id}D_")
    
    # 保存订单到数据库
    execute_update(
        """INSERT INTO recharge_order 
           (out_trade_no, user_id, product_id, amount, status, created_at)
           VALUES (%s, %s, %s, %s, 'pending', NOW())""",
        (out_trade_no, user_id, product_id, product['price'])
    )
    
    # 创建支付链接
    subject = f"梦炽云召唤之星-{product['name']}"
    
    try:
        if pay_type == 'wap':
            pay_url = client.wap_pay(
                out_trade_no=out_trade_no,
                total_amount=product['price'],
                subject=subject,
            )
        else:
            pay_url = client.page_pay(
                out_trade_no=out_trade_no,
                total_amount=product['price'],
                subject=subject,
            )
        
        return jsonify({
            'ok': True,
            'pay_url': pay_url,
            'out_trade_no': out_trade_no,
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': f'创建订单失败: {str(e)}'}), 500


@pay_bp.post('/notify')
def alipay_notify():
    """支付宝异步通知回调"""
    try:
        from infrastructure.alipay import get_alipay_client
        client = get_alipay_client()
        if not client:
            return 'fail'
    except Exception:
        return 'fail'
    
    # 获取回调参数
    params = request.form.to_dict()
    
    # 验证签名
    if not client.verify_notify(params):
        print("[Pay] 签名验证失败")
        return 'fail'
    
    out_trade_no = params.get('out_trade_no', '')
    trade_status = params.get('trade_status', '')
    trade_no = params.get('trade_no', '')  # 支付宝交易号
    
    # 只处理支付成功
    if trade_status not in ('TRADE_SUCCESS', 'TRADE_FINISHED'):
        return 'success'
    
    # 查询订单
    rows = execute_query(
        "SELECT * FROM recharge_order WHERE out_trade_no = %s",
        (out_trade_no,)
    )
    if not rows:
        print(f"[Pay] 订单不存在: {out_trade_no}")
        return 'fail'
    
    order = rows[0]
    
    # 检查是否已处理
    if order.get('status') == 'paid':
        return 'success'
    
    user_id = order.get('user_id')
    product_id = order.get('product_id')
    
    # 查找商品配置
    config = load_recharge_products()
    product = None
    for p in config.get('products', []):
        if p.get('id') == product_id:
            product = p
            break
    
    if not product:
        print(f"[Pay] 商品配置不存在: {product_id}")
        return 'fail'
    
    # 计算宝石数量（不再使用vip_exp，VIP等级由消耗宝石数决定）
    diamond = product.get('diamond', 0)
    
    # 检查首充
    player_rows = execute_query(
        "SELECT first_recharge_claimed FROM player WHERE user_id = %s",
        (user_id,)
    )
    first_recharge_claimed = 0
    if player_rows:
        first_recharge_claimed = player_rows[0].get('first_recharge_claimed', 0) or 0
    
    # 首充双倍
    bonus = 0
    if first_recharge_claimed == 0 and product.get('first_bonus'):
        bonus = product.get('first_bonus', 0)
    
    total_diamond = diamond + bonus
    
    # 更新玩家数据（只增加宝石，VIP等级在消耗宝石时计算）
    if first_recharge_claimed == 0 and bonus > 0:
        execute_update(
            """UPDATE player SET 
               silver_diamond = silver_diamond + %s, 
               first_recharge_claimed = 1
               WHERE user_id = %s""",
            (total_diamond, user_id)
        )
    else:
        execute_update(
            """UPDATE player SET 
               silver_diamond = silver_diamond + %s
               WHERE user_id = %s""",
            (total_diamond, user_id)
        )
    
    # 更新订单状态
    execute_update(
        """UPDATE recharge_order SET 
           status = 'paid', 
           trade_no = %s,
           yuanbao_granted = %s,
           bonus_granted = %s,
           paid_at = NOW()
           WHERE out_trade_no = %s""",
        (trade_no, diamond, bonus, out_trade_no)
    )
    
    print(f"[Pay] 充值成功: user={user_id}, diamond={total_diamond}")
    
    return 'success'


@pay_bp.get('/return')
def alipay_return():
    """支付宝同步跳转回调"""
    # 跳转回赞助页面
    return redirect('/sponsor?result=success')


@pay_bp.post('/exchange')
def exchange_diamond():
    """宝石兑换元宝"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    data = request.get_json() or {}
    amount = data.get('amount', 0)
    
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': '请输入有效数量'}), 400
    
    if amount <= 0:
        return jsonify({'ok': False, 'error': '请输入有效数量'}), 400
    
    # 获取兑换比例
    config = load_recharge_products()
    exchange_rate = config.get('exchange_rate', 100)
    
    # 检查宝石余额
    rows = execute_query(
        "SELECT silver_diamond FROM player WHERE user_id = %s",
        (user_id,)
    )
    if not rows:
        return jsonify({'ok': False, 'error': '玩家不存在'}), 404
    
    current_diamond = rows[0].get('silver_diamond', 0) or 0
    if current_diamond < amount:
        return jsonify({'ok': False, 'error': '宝石不足'}), 400
    
    # 计算元宝
    yuanbao = amount * exchange_rate
    
    # 扣除宝石，增加元宝，累计消耗宝石数
    execute_update(
        """UPDATE player SET 
           silver_diamond = silver_diamond - %s,
           yuanbao = yuanbao + %s,
           diamond_spent = diamond_spent + %s
           WHERE user_id = %s""",
        (amount, yuanbao, amount, user_id)
    )
    
    # 重新计算VIP等级
    spent_rows = execute_query(
        "SELECT diamond_spent FROM player WHERE user_id = %s",
        (user_id,)
    )
    total_spent = spent_rows[0].get('diamond_spent', 0) if spent_rows else 0
    new_vip_level = calc_vip_level(total_spent)
    execute_update(
        "UPDATE player SET vip_level = %s WHERE user_id = %s",
        (new_vip_level, user_id)
    )
    
    # 查询更新后的数据
    rows = execute_query(
        "SELECT silver_diamond, yuanbao FROM player WHERE user_id = %s",
        (user_id,)
    )
    new_diamond = rows[0].get('silver_diamond', 0) if rows else 0
    new_yuanbao = rows[0].get('yuanbao', 0) if rows else 0
    
    return jsonify({
        'ok': True,
        'message': f'兑换成功！消耗{amount}宝石，获得{yuanbao}元宝',
        'silver_diamond': new_diamond,
        'yuanbao': new_yuanbao,
    })


@pay_bp.get('/query')
def query_order():
    """查询订单状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    out_trade_no = request.args.get('out_trade_no')
    if not out_trade_no:
        return jsonify({'ok': False, 'error': '缺少订单号'}), 400
    
    # 查询本地订单
    rows = execute_query(
        "SELECT * FROM recharge_order WHERE out_trade_no = %s AND user_id = %s",
        (out_trade_no, user_id)
    )
    if not rows:
        return jsonify({'ok': False, 'error': '订单不存在'}), 404
    
    order = rows[0]
    
    return jsonify({
        'ok': True,
        'status': order.get('status'),
        'amount': str(order.get('amount', 0)),
        'diamond_granted': order.get('yuanbao_granted', 0),
        'bonus_granted': order.get('bonus_granted', 0),
    })


@pay_bp.get('/history')
def get_recharge_history():
    """获取充值记录"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    offset = (page - 1) * size
    
    rows = execute_query(
        """SELECT out_trade_no, product_id, amount, status, 
                  yuanbao_granted as diamond_granted, bonus_granted, created_at, paid_at
           FROM recharge_order 
           WHERE user_id = %s 
           ORDER BY created_at DESC
           LIMIT %s OFFSET %s""",
        (user_id, size, offset)
    )
    
    total_rows = execute_query(
        "SELECT COUNT(*) as total FROM recharge_order WHERE user_id = %s",
        (user_id,)
    )
    total = total_rows[0]['total'] if total_rows else 0
    
    # 格式化时间
    for row in rows:
        if row.get('created_at'):
            row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        if row.get('paid_at'):
            row['paid_at'] = row['paid_at'].strftime('%Y-%m-%d %H:%M:%S')
        row['amount'] = str(row.get('amount', 0))
    
    return jsonify({
        'ok': True,
        'orders': rows,
        'total': total,
        'page': page,
        'size': size,
    })


@pay_bp.get('/status')
def get_pay_status():
    """获取支付服务状态"""
    try:
        from infrastructure.alipay import get_alipay_client
        client = get_alipay_client()
        available = client is not None
    except Exception:
        available = False
    
    return jsonify({
        'ok': True,
        'available': available,
    })

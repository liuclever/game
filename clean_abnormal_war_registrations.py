"""
清理异常的盟战报名记录
问题：有些联盟报名了超过2个目标（飞龙军1个土地+伏虎军1个据点），这不符合规则
解决方案：对于每个联盟，只保留最新的2个活跃报名记录（飞龙军1个+伏虎军1个），其他标记为已取消
"""
from infrastructure.db.connection import execute_query, execute_update, get_connection

# 土地/据点配置
DRAGON_ONLY_LANDS = {1, 2}  # 土地：迷雾城1号土地、飞龙港1号土地
TIGER_ONLY_LANDS = {3, 4}   # 据点：幻灵镇1号据点、定老城1号据点

# 活跃状态：1-已报名，2-待审核，3-已确认，4-战斗中
ACTIVE_STATUSES = {1, 2, 3, 4}
STATUS_CANCELLED = 0


def get_all_alliances_with_registrations():
    """获取所有有活跃报名记录的联盟"""
    sql = """
        SELECT DISTINCT alliance_id
        FROM alliance_land_registration
        WHERE status IN (1, 2, 3, 4)
        ORDER BY alliance_id
    """
    rows = execute_query(sql)
    return [row['alliance_id'] for row in rows]


def get_active_registrations(alliance_id):
    """获取联盟的所有活跃报名记录"""
    sql = """
        SELECT id, alliance_id, land_id, army, registration_time, status
        FROM alliance_land_registration
        WHERE alliance_id = %s AND status IN (1, 2, 3, 4)
        ORDER BY registration_time DESC, id DESC
    """
    rows = execute_query(sql, (alliance_id,))
    return rows


def clean_alliance_registrations(alliance_id):
    """清理单个联盟的异常报名记录"""
    registrations = get_active_registrations(alliance_id)
    
    if len(registrations) <= 2:
        return None  # 没有异常，不需要清理
    
    # 分类：飞龙军土地和伏虎军据点
    dragon_regs = []
    tiger_regs = []
    
    for reg in registrations:
        land_id = reg['land_id']
        if land_id in DRAGON_ONLY_LANDS:
            dragon_regs.append(reg)
        elif land_id in TIGER_ONLY_LANDS:
            tiger_regs.append(reg)
    
    # 保留每个军队类型最新的1个报名
    to_keep = []
    if dragon_regs:
        to_keep.append(dragon_regs[0])  # 最新的飞龙军报名
    if tiger_regs:
        to_keep.append(tiger_regs[0])  # 最新的伏虎军报名
    
    # 需要取消的记录ID
    to_cancel_ids = []
    keep_ids = {reg['id'] for reg in to_keep}
    
    for reg in registrations:
        if reg['id'] not in keep_ids:
            to_cancel_ids.append(reg['id'])
    
    if not to_cancel_ids:
        return None
    
    # 取消多余的报名记录
    placeholders = ", ".join(["%s"] * len(to_cancel_ids))
    sql = f"""
        UPDATE alliance_land_registration
        SET status = %s
        WHERE id IN ({placeholders})
    """
    params = [STATUS_CANCELLED] + to_cancel_ids
    affected = execute_update(sql, tuple(params))
    
    return {
        'alliance_id': alliance_id,
        'total_registrations': len(registrations),
        'kept_registrations': len(to_keep),
        'cancelled_count': len(to_cancel_ids),
        'cancelled_ids': to_cancel_ids,
    }


def main():
    """主函数"""
    print("=" * 60)
    print("清理异常的盟战报名记录")
    print("=" * 60)
    
    # 获取所有有报名记录的联盟
    alliance_ids = get_all_alliances_with_registrations()
    print(f"\n找到 {len(alliance_ids)} 个联盟有活跃报名记录")
    
    # 清理每个联盟的异常记录
    cleaned_alliances = []
    total_cancelled = 0
    
    for alliance_id in alliance_ids:
        result = clean_alliance_registrations(alliance_id)
        if result:
            cleaned_alliances.append(result)
            total_cancelled += result['cancelled_count']
            print(f"\n联盟 {alliance_id}:")
            print(f"  - 总报名数: {result['total_registrations']}")
            print(f"  - 保留数: {result['kept_registrations']}")
            print(f"  - 取消数: {result['cancelled_count']}")
            print(f"  - 取消的记录ID: {result['cancelled_ids']}")
    
    # 总结
    print("\n" + "=" * 60)
    print("清理完成")
    print("=" * 60)
    print(f"共处理 {len(cleaned_alliances)} 个联盟")
    print(f"共取消 {total_cancelled} 条异常报名记录")
    
    if cleaned_alliances:
        print("\n清理详情：")
        for result in cleaned_alliances:
            print(f"  联盟 {result['alliance_id']}: 取消 {result['cancelled_count']} 条记录")
    else:
        print("\n没有发现异常报名记录，所有联盟都符合规则（最多2个报名）")


if __name__ == "__main__":
    main()

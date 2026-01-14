"""召唤之王正赛系统服务"""
from datetime import datetime, date
from infrastructure.db.connection import execute_query, execute_update, get_connection
from domain.services.pvp_battle_engine import run_pvp_battle, PvpPlayer
from application import services
import random


def get_current_season():
    """获取当前赛季编号（年份*100+周数）"""
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    return year * 100 + week


def advance_to_finals():
    """
    周四23:59执行：选出各赛区前16名进入正赛
    生成32强名单
    """
    season = get_current_season()
    
    print(f"[召唤之王] 开始生成第{season}赛季正赛名单...")
    
    # 清空本赛季的正赛记录（如果有）
    execute_update(
        "DELETE FROM king_final_stage WHERE season = %s",
        (season,)
    )
    
    # 获取两个赛区的前16名（已报名的玩家）
    finalists = []
    for area in [1, 2]:
        top_16 = execute_query(
            """SELECT user_id, rank_position 
               FROM king_challenge_rank 
               WHERE area_index = %s AND is_registered = 1
               ORDER BY rank_position ASC 
               LIMIT 16""",
            (area,)
        )
        
        for player in top_16:
            finalists.append(player['user_id'])
            # 记录进入32强
            execute_update(
                """INSERT INTO king_final_stage 
                   (season, user_id, stage, created_at) 
                   VALUES (%s, %s, '32', NOW())""",
                (season, player['user_id'])
            )
        
        print(f"[召唤之王] {area}赛区选出{len(top_16)}名选手进入32强")
    
    print(f"[召唤之王] 共{len(finalists)}名选手进入正赛")
    
    # 发放32强奖励
    for user_id in finalists:
        send_stage_reward(user_id, '32', season)
    
    return len(finalists)


def run_final_stage(stage):
    """
    执行正赛某一轮次
    stage: '32', '16', '8', '4', '2'
    """
    season = get_current_season()
    next_stage_map = {
        '32': '16',
        '16': '8',
        '8': '4',
        '4': '2',
        '2': 'champion'
    }
    next_stage = next_stage_map.get(stage)
    
    if not next_stage:
        print(f"[召唤之王] 无效的阶段: {stage}")
        return
    
    print(f"[召唤之王] 开始执行{stage}强赛...")
    
    # 获取本轮参赛选手（is_winner为NULL表示还未比赛）
    players = execute_query(
        """SELECT user_id FROM king_final_stage 
           WHERE season = %s AND stage = %s AND is_winner IS NULL
           ORDER BY id ASC""",
        (season, stage)
    )
    
    if not players:
        print(f"[召唤之王] {stage}强赛没有参赛选手")
        return
    
    player_ids = [p['user_id'] for p in players]
    print(f"[召唤之王] {stage}强赛共{len(player_ids)}名选手")
    
    # 随机打乱顺序
    random.shuffle(player_ids)
    
    # 配对并执行战斗
    match_id = 1
    winners = []
    
    for i in range(0, len(player_ids), 2):
        if i + 1 < len(player_ids):
            # 正常配对
            player1_id = player_ids[i]
            player2_id = player_ids[i + 1]
            
            print(f"[召唤之王] 第{match_id}场: {player1_id} vs {player2_id}")
            
            # 执行战斗
            winner_id = execute_battle(player1_id, player2_id, season, stage, match_id)
            winners.append(winner_id)
            
            # 更新战斗记录
            execute_update(
                """UPDATE king_final_stage 
                   SET is_winner = %s, opponent_id = %s, match_id = %s, battle_time = NOW()
                   WHERE season = %s AND stage = %s AND user_id = %s""",
                (1 if winner_id == player1_id else 0, player2_id, match_id, season, stage, player1_id)
            )
            execute_update(
                """UPDATE king_final_stage 
                   SET is_winner = %s, opponent_id = %s, match_id = %s, battle_time = NOW()
                   WHERE season = %s AND stage = %s AND user_id = %s""",
                (1 if winner_id == player2_id else 0, player1_id, match_id, season, stage, player2_id)
            )
            
            match_id += 1
        else:
            # 轮空，直接晋级
            player_id = player_ids[i]
            print(f"[召唤之王] {player_id} 轮空，直接晋级")
            
            winners.append(player_id)
            
            # 更新为轮空
            execute_update(
                """UPDATE king_final_stage 
                   SET is_bye = 1, is_winner = 1, battle_time = NOW()
                   WHERE season = %s AND stage = %s AND user_id = %s""",
                (season, stage, player_id)
            )
    
    # 晋级到下一轮
    for winner_id in winners:
        execute_update(
            """INSERT INTO king_final_stage 
               (season, user_id, stage, created_at) 
               VALUES (%s, %s, %s, NOW())""",
            (season, winner_id, next_stage)
        )
        
        # 发放晋级奖励
        if next_stage != 'champion':
            send_stage_reward(winner_id, next_stage, season)
    
    # 如果是决赛，冠军额外处理
    if next_stage == 'champion':
        champion_id = winners[0] if winners else None
        if champion_id:
            print(f"[召唤之王] 冠军诞生: {champion_id}")
            # 更新冠军标识
            execute_update(
                "UPDATE player SET is_summon_king = 1 WHERE user_id = %s",
                (champion_id,)
            )
            # 清除其他人的冠军标识
            execute_update(
                "UPDATE player SET is_summon_king = 0 WHERE user_id != %s",
                (champion_id,)
            )
            # 发放冠军奖励
            send_stage_reward(champion_id, 'champion', season)
    
    print(f"[召唤之王] {stage}强赛结束，{len(winners)}名选手晋级{next_stage}")


def execute_battle(player1_id, player2_id, season, stage, match_id):
    """
    执行两个玩家之间的战斗
    返回胜者ID
    """
    try:
        # 获取双方玩家信息
        player1 = services.player_repo.get_by_id(player1_id)
        player2 = services.player_repo.get_by_id(player2_id)
        
        if not player1 or not player2:
            print(f"[召唤之王] 玩家信息不存在: {player1_id} or {player2_id}")
            # 默认返回第一个玩家
            return player1_id
        
        # 获取双方幻兽
        player1_beasts = services.player_beast_repo.get_team_beasts(player1_id)
        player2_beasts = services.player_beast_repo.get_team_beasts(player2_id)
        
        if not player1_beasts:
            print(f"[召唤之王] {player1_id} 没有出战幻兽，判负")
            return player2_id
        if not player2_beasts:
            print(f"[召唤之王] {player2_id} 没有出战幻兽，判负")
            return player1_id
        
        # 转换为PVP幻兽
        player1_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(player1_beasts)
        player2_pvp_beasts = services.beast_pvp_service.to_pvp_beasts(player2_beasts)
        
        pvp_player1 = PvpPlayer(
            player_id=player1_id,
            level=player1.level,
            beasts=player1_pvp_beasts,
            name=player1.nickname,
        )
        pvp_player2 = PvpPlayer(
            player_id=player2_id,
            level=player2.level,
            beasts=player2_pvp_beasts,
            name=player2.nickname,
        )
        
        # 执行战斗
        pvp_result = run_pvp_battle(pvp_player1, pvp_player2, max_log_turns=50)
        winner_id = pvp_result.winner_player_id
        
        print(f"[召唤之王] 战斗结果: {winner_id} 获胜")
        return winner_id
        
    except Exception as e:
        print(f"[召唤之王] 战斗执行失败: {e}")
        # 出错时随机选一个
        return random.choice([player1_id, player2_id])


def send_stage_reward(user_id, stage, season):
    """
    发放正赛阶段奖励
    stage: '32', '16', '8', '4', '2', 'champion'
    """
    # 奖励配置
    rewards = {
        '32': {'gold': 50000, 'items': [(5001, 10), (5002, 5)]},
        '16': {'gold': 100000, 'items': [(5001, 15), (5002, 10)]},
        '8': {'gold': 150000, 'items': [(5001, 20), (5002, 15)]},
        '4': {'gold': 250000, 'items': [(5001, 30), (5002, 20)]},
        '2': {'gold': 350000, 'items': [(5001, 40), (5002, 25)]},
        'champion': {'gold': 450000, 'items': [(5001, 50), (5002, 30)]},
    }
    
    reward = rewards.get(stage)
    if not reward:
        return
    
    try:
        # 发放铜钱
        execute_update(
            "UPDATE player SET gold = gold + %s WHERE user_id = %s",
            (reward['gold'], user_id)
        )
        
        # 发放物品
        for item_id, count in reward.get('items', []):
            try:
                services.inventory_service.add_item(user_id, item_id, count)
            except Exception as e:
                print(f"[召唤之王] 发放物品失败: {e}")
        
        # 记录奖励领取
        stage_name_map = {
            '32': '32强',
            '16': '16强',
            '8': '8强',
            '4': '4强',
            '2': '亚军',
            'champion': '冠军'
        }
        
        # 检查是否已记录
        existing = execute_query(
            "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = %s",
            (user_id, season)
        )
        
        if not existing:
            execute_update(
                """INSERT INTO king_reward_claimed 
                   (user_id, season, reward_tier, claimed_at) 
                   VALUES (%s, %s, %s, NOW())""",
                (user_id, season, stage_name_map.get(stage, stage))
            )
        else:
            # 更新为更高的奖励档位
            execute_update(
                """UPDATE king_reward_claimed 
                   SET reward_tier = %s, claimed_at = NOW()
                   WHERE user_id = %s AND season = %s""",
                (stage_name_map.get(stage, stage), user_id, season)
            )
        
        print(f"[召唤之王] 发放{stage}强奖励给玩家{user_id}: {reward['gold']}铜钱")
        
    except Exception as e:
        print(f"[召唤之王] 发放奖励失败: {e}")


def reset_weekly_registration():
    """
    每周一00:00执行：重置报名状态
    """
    print("[召唤之王] 开始重置周报名状态...")
    
    # 重置所有玩家的报名状态
    execute_update(
        "UPDATE king_challenge_rank SET is_registered = 0"
    )
    
    print("[召唤之王] 报名状态重置完成")


def get_final_stage_info(season):
    """
    获取正赛信息
    返回各阶段的对阵情况
    """
    stages = ['32', '16', '8', '4', '2', 'champion']
    result = {}
    
    for stage in stages:
        matches = execute_query(
            """SELECT fs.user_id, fs.opponent_id, fs.is_winner, fs.is_bye, fs.match_id,
                      p.nickname, p2.nickname as opponent_nickname
               FROM king_final_stage fs
               LEFT JOIN player p ON fs.user_id = p.user_id
               LEFT JOIN player p2 ON fs.opponent_id = p2.user_id
               WHERE fs.season = %s AND fs.stage = %s
               ORDER BY fs.match_id, fs.id""",
            (season, stage)
        )
        
        result[stage] = [
            {
                'userId': m['user_id'],
                'nickname': m['nickname'],
                'opponentId': m['opponent_id'],
                'opponentNickname': m['opponent_nickname'],
                'isWinner': m['is_winner'],
                'isBye': m['is_bye'],
                'matchId': m['match_id']
            }
            for m in matches
        ]
    
    return result

"""
脚本：模拟“充值成功”（跳过支付流程），用于验证：
1) 元宝50%返利活动（每天刷新）能正确识别“今日赞助宝石”；
2) 满足档位后 can_claim=True；
3) 领取后同档位当天不能重复领取。

实现方式：
- 直接往 MySQL 表 recharge_order 插入一条 status='paid' 的记录（paid_at=NOW）。
- 然后用 HTTP（携带登录 session）调用：
  - GET  /api/announcement/rebate/status
  - POST /api/announcement/rebate/claim

使用：
  1) 先启动后端：python -m interfaces.web_api.app  （默认 127.0.0.1:5000）
  2) 运行脚本（项目根目录）：
     python -m scripts.test_rebate_simulate_recharge
"""

from __future__ import annotations

import json
import time
from decimal import Decimal
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, Request

from infrastructure.db.connection import execute_update

BASE_URL = "http://127.0.0.1:5000"

# 默认测试账号（可按需改）
USER_ID = 20065
USERNAME = "user05"
PASSWORD = "123456"
NICKNAME = "user05"

# 本次模拟“实际充值到账宝石”（不含首充赠送）
# 返利逻辑用的是 recharge_order.yuanbao_granted 的累计（按日）
PAID_GEMS_TODAY = 1000


def _http_json(opener, method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = Request(url=url, data=data, headers=headers, method=method.upper())
    with opener.open(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(raw)
    except Exception:
        return {"ok": False, "error": f"非JSON响应: {raw[:200]}"}


def _ensure_user_exists():
    # 尽量只使用确定存在的字段（兼容不同库版本）
    sql = """
        INSERT INTO player (
            user_id, username, password,
            nickname, level, exp,
            gold, silver_diamond, yuanbao, dice,
            location, vip_level, vip_exp
        )
        VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            username = VALUES(username),
            password = VALUES(password),
            nickname = VALUES(nickname),
            updated_at = CURRENT_TIMESTAMP
    """
    execute_update(
        sql,
        (
            USER_ID,
            USERNAME,
            PASSWORD,
            NICKNAME,
            30,  # 等级不影响返利，但给个正常值
            0,
            0,
            0,
            0,
            0,
            "落龙镇",
            0,
            0,
        ),
    )


def _insert_paid_recharge_order(paid_gems: int):
    # 生成一个唯一 out_trade_no，避免唯一键冲突
    out_trade_no = f"SIM_{USER_ID}_{int(time.time() * 1000)}"
    trade_no = f"SIM_TRADE_{out_trade_no}"
    product_id = "SIMULATED"
    # amount 仅用于展示/记录，这里随便填一个可解析的金额
    amount = Decimal("0.01")

    sql = """
        INSERT INTO recharge_order (
            out_trade_no, trade_no, user_id, product_id, amount,
            status, yuanbao_granted, bonus_granted,
            created_at, paid_at
        )
        VALUES (
            %s, %s, %s, %s, %s,
            'paid', %s, %s,
            NOW(), NOW()
        )
    """
    execute_update(
        sql,
        (
            out_trade_no,
            trade_no,
            USER_ID,
            product_id,
            str(amount),
            int(paid_gems),
            0,  # bonus_granted（赠送）不计入返利累计
        ),
    )
    return out_trade_no


def _grant_gems_to_player_balance(paid_gems: int):
    """模拟“充值到账”：把实际充值宝石加到玩家当前宝石余额（silver_diamond）。"""
    execute_update(
        "UPDATE player SET silver_diamond = COALESCE(silver_diamond, 0) + %s WHERE user_id = %s",
        (int(paid_gems), USER_ID),
    )


def main():
    print("=== 返利活动测试：模拟充值（跳过支付） ===")
    print(f"base_url={BASE_URL}")
    print(f"user_id={USER_ID}, username={USERNAME}")
    print(f"本次模拟到账宝石(今日)：{PAID_GEMS_TODAY}")

    _ensure_user_exists()
    out_trade_no = _insert_paid_recharge_order(PAID_GEMS_TODAY)
    print(f"已插入 recharge_order: out_trade_no={out_trade_no}（status=paid, paid_at=NOW）")
    _grant_gems_to_player_balance(PAID_GEMS_TODAY)
    print(f"已发放宝石到玩家余额：silver_diamond +{PAID_GEMS_TODAY}")

    # 登录获取 session cookie
    jar = CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    login_res = _http_json(
        opener,
        "POST",
        f"{BASE_URL}/api/auth/login",
        {"username": USERNAME, "password": PASSWORD},
    )
    if not login_res.get("ok"):
        print("登录失败：", login_res)
        return
    print("登录成功：", {"user_id": login_res.get("user_id"), "nickname": login_res.get("nickname")})

    # 拉取返利状态（每天刷新）
    status_res = _http_json(opener, "GET", f"{BASE_URL}/api/announcement/rebate/status", None)
    if not status_res.get("ok"):
        print("返利状态接口返回失败：", status_res)
        print("提示：如果返回“活动未开启或已结束”，需要确保 announcements.json 里 yuanbao_rebate 在有效期内。")
        return

    today_gems = int(status_res.get("today_gems", status_res.get("total_gems", 0)) or 0)
    tiers = status_res.get("tiers", []) or []
    print(f"接口识别的今日赞助宝石 today_gems={today_gems}")
    print(f"档位数量={len(tiers)}")

    # 依次领取所有“可领取”的档位
    claimable = [t for t in tiers if t.get("can_claim")]
    claimable.sort(key=lambda x: int(x.get("gems_required", 0) or 0))
    if not claimable:
        print("当前没有任何可领取档位（可能是今日赞助不足，或档位已全部领取）。")
    else:
        print("将尝试领取以下档位：", [int(t.get("gems_required", 0) or 0) for t in claimable])

    first_claim_tier = None
    for t in claimable:
        gems_required = int(t.get("gems_required", 0) or 0)
        if first_claim_tier is None:
            first_claim_tier = gems_required
        res = _http_json(opener, "POST", f"{BASE_URL}/api/announcement/rebate/claim", {"tier_gems": gems_required})
        print(f"[领取档位 {gems_required}] =>", res)

    # 验证同档位当天不能重复领取
    if first_claim_tier is not None:
        res2 = _http_json(opener, "POST", f"{BASE_URL}/api/announcement/rebate/claim", {"tier_gems": first_claim_tier})
        print(f"[重复领取档位 {first_claim_tier}] =>", res2)

    # 再拉一次状态，看 can_claim 是否正确变为 false
    status_res2 = _http_json(opener, "GET", f"{BASE_URL}/api/announcement/rebate/status", None)
    print("[领取后状态] =>",
          {"ok": status_res2.get("ok"), "today_gems": status_res2.get("today_gems", status_res2.get("total_gems"))})


if __name__ == "__main__":
    main()

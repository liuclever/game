"""猛虎战场全链路 HTTP 端到端测试

运行方式（项目根目录）：
    $env:BATTLEFIELD_ALLOW_TIME_BYPASS = "true"
    python -m pytest tests/battle_filed/tiger_filed/test_battlefield_http_e2e.py -vv -s

前置条件：
    - Flask 应用已启动: python -m interfaces.web_api.app
    - 数据库中存在测试账号（默认 battlefield_test_1 / 123456）且满足猛虎战场等级(20-39)
    - 该账号有 is_in_team=1 的幻兽
    - 设置环境变量 BATTLEFIELD_ALLOW_TIME_BYPASS=true 跳过时间窗口限制
    - 需先运行 create_information/create_31_test_players.py 创建测试玩家
    - 需先运行 signup_31_test_players.py 报名测试玩家
"""

import pytest
import requests

# 配置
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "battlefield_test_1"  # 猛虎战场测试玩家（需先运行 create_31_test_players.py）
TEST_PASSWORD = "123456"
BATTLEFIELD_TYPE = "tiger"


class TestTigerBattlefieldHttpE2E:
    """猛虎战场全链路 HTTP 端到端测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """初始化 session"""
        self.session = requests.Session()
        yield
        self.session.close()

    def test_full_e2e_flow(self):
        """完整 E2E 流程：登录 → 报名 → 查询状态 → 开赛 → 查询战报列表 → 查询战报详情"""

        # ========== 步骤1：登录 ==========
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
        )
        assert login_resp.status_code == 200, f"登录请求失败: {login_resp.status_code} {login_resp.text}"
        login_data = login_resp.json()
        assert login_data.get("ok") is True, f"登录失败: {login_data.get('error', login_data)}"
        print(f"✅ 步骤1：登录成功，用户: {login_data.get('nickname', TEST_USERNAME)}")

        # ========== 步骤2：查询报名前状态 ==========
        info_before_resp = self.session.get(
            f"{BASE_URL}/api/battlefield/info",
            params={"type": BATTLEFIELD_TYPE},
        )
        assert info_before_resp.status_code == 200, f"查询战场信息失败: {info_before_resp.status_code}"
        info_before = info_before_resp.json()
        assert info_before.get("ok") is True, f"查询战场信息失败: {info_before.get('error')}"
        count_before = info_before["battlefield"]["redCount"] + info_before["battlefield"]["blueCount"]
        print(f"✅ 步骤2：报名前状态，当前报名人数: {count_before}")

        # ========== 步骤3：报名 ==========
        signup_resp = self.session.post(
            f"{BASE_URL}/api/battlefield/signup",
            json={"type": BATTLEFIELD_TYPE},
        )
        assert signup_resp.status_code == 200, f"报名请求失败: {signup_resp.status_code} {signup_resp.text}"
        signup_data = signup_resp.json()
        assert signup_data.get("ok") is True, f"报名失败: {signup_data.get('error', signup_data)}"
        print(f"✅ 步骤3：报名成功，消息: {signup_data.get('message')}")

        # ========== 步骤4：查询报名后状态 ==========
        info_after_resp = self.session.get(
            f"{BASE_URL}/api/battlefield/info",
            params={"type": BATTLEFIELD_TYPE},
        )
        assert info_after_resp.status_code == 200, f"查询战场信息失败: {info_after_resp.status_code}"
        info_after = info_after_resp.json()
        assert info_after.get("ok") is True, f"查询战场信息失败: {info_after.get('error')}"
        
        # 校验 isSignedUp
        assert info_after.get("isSignedUp") is True, f"报名后 isSignedUp 应为 true，实际: {info_after.get('isSignedUp')}"
        
        # 校验报名人数 +1（重复报名不会增加，所以允许相等或 +1）
        count_after = info_after["battlefield"]["redCount"] + info_after["battlefield"]["blueCount"]
        assert count_after >= count_before, f"报名人数应不减少，之前: {count_before}，之后: {count_after}"
        print(f"✅ 步骤4：报名状态验证通过，isSignedUp=true，报名人数: {count_after}")

        # ========== 步骤5：触发开赛 ==========
        run_resp = self.session.post(
            f"{BASE_URL}/api/battlefield/run",
            json={"type": BATTLEFIELD_TYPE},
        )
        assert run_resp.status_code == 200, f"开赛请求失败: {run_resp.status_code} {run_resp.text}"
        run_data = run_resp.json()
        assert run_data.get("ok") is True, f"开赛失败: {run_data.get('error', run_data)}"
        
        period = run_data.get("period")
        total_players = run_data.get("total_players")
        assert period is not None, f"开赛返回缺少 period: {run_data}"
        assert total_players is not None, f"开赛返回缺少 total_players: {run_data}"
        assert total_players >= 2, f"参赛人数应至少 2 人，实际: {total_players}"
        
        print(f"✅ 步骤5：开赛成功")
        print(f"   期数: {period}")
        print(f"   参赛人数: {total_players}")
        print(f"   冠军: {run_data.get('champion_name')} (ID: {run_data.get('champion_id')})")

        # ========== 步骤6：查询战报列表 ==========
        yesterday_resp = self.session.get(
            f"{BASE_URL}/api/battlefield/yesterday",
            params={"type": BATTLEFIELD_TYPE, "period": period},
        )
        assert yesterday_resp.status_code == 200, f"查询战报列表失败: {yesterday_resp.status_code}"
        yesterday_data = yesterday_resp.json()
        assert yesterday_data.get("ok") is True, f"查询战报列表失败: {yesterday_data.get('error')}"
        
        matches = yesterday_data.get("matches", [])
        expected_matches = total_players - 1  # 单淘汰赛场次
        assert len(matches) == expected_matches, f"战报数量应为 {expected_matches}，实际: {len(matches)}"
        assert yesterday_data.get("period") == period, f"期数不匹配: 预期 {period}，实际 {yesterday_data.get('period')}"
        
        print(f"✅ 步骤6：战报列表查询成功，共 {len(matches)} 场")

        # ========== 步骤7：查询单场战报详情 ==========
        first_match = matches[0]
        battle_id = first_match.get("id")
        assert battle_id is not None, f"战报列表中缺少 id: {first_match}"
        
        detail_resp = self.session.get(f"{BASE_URL}/api/battlefield/battle/{battle_id}")
        assert detail_resp.status_code == 200, f"查询战报详情失败: {detail_resp.status_code}"
        detail_data = detail_resp.json()
        assert detail_data.get("ok") is True, f"查询战报详情失败: {detail_data.get('error')}"
        
        battle = detail_data.get("battle")
        assert battle is not None, f"返回缺少 battle: {detail_data}"
        
        battle_data = battle.get("battle_data")
        assert battle_data is not None, f"战报缺少 battle_data: {battle}"
        assert "battles" in battle_data, f"battle_data 缺少 battles: {battle_data}"
        
        print(f"✅ 步骤7：战报详情查询成功")
        print(f"   战报ID: {battle_id}")
        print(f"   对阵: {battle.get('first_user_name')} VS {battle.get('second_user_name')}")
        print(f"   结果: {'左侧胜' if battle.get('is_first_win') else '右侧胜'}")
        print(f"   战斗场数: {len(battle_data.get('battles', []))}")

        print("\n" + "=" * 60)
        print("✅ 猛虎战场全链路 E2E 测试通过！")
        print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-vv", "-s"])


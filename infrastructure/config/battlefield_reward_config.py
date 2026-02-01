"""战场奖励配置加载器"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any


class BattlefieldRewardConfig:
    """战场奖励配置"""
    
    def __init__(self, config_path: str | None = None):
        if config_path is None:
            base_dir = Path(__file__).resolve().parents[2]
            config_path = str(base_dir / "configs" / "battlefield_rewards.json")
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"加载战场奖励配置失败: {e}")
    
    def get_king_reward(self) -> Dict[str, Any]:
        """获取战王奖励配置"""
        return self._config.get("战王奖励", {})
    
    def get_camp_reward(self, is_winner: bool) -> Dict[str, Any]:
        """获取阵营奖励配置
        
        Args:
            is_winner: 是否胜利阵营
        """
        camp_rewards = self._config.get("阵营奖励", {})
        key = "胜利阵营" if is_winner else "失败阵营"
        return camp_rewards.get(key, {})
    
    def get_kill_reward(self, kills: int) -> Dict[str, Any]:
        """获取杀敌奖励配置
        
        Args:
            kills: 击杀数（胜场数）
        """
        kill_rewards = self._config.get("杀敌奖励", {})
        
        if kills == 0:
            return {"description": "无杀敌奖励", "gold": 0, "items": []}
        elif kills >= 5:
            return kill_rewards.get("5+", {})
        else:
            return kill_rewards.get(str(kills), {})

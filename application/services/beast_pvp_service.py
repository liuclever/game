"""
幻兽PVP数据转换服务
"""
from typing import List, Dict, Optional
from domain.services.pvp_battle_engine import PvpBeast
from domain.services.skill_system import apply_buff_debuff_skills
from domain.repositories.spirit_repo import ISpiritRepo
from domain.repositories.bone_repo import IBoneRepo
from domain.repositories.mosoul_repo import IBeastMoSoulRepo
from infrastructure.config.bone_system_config import get_bone_system_config


class BeastPvpService:
    """幻兽PVP数据转换服务，统一计算装备加成和技能效果"""

    def __init__(
        self,
        spirit_repo: ISpiritRepo,
        bone_repo: IBoneRepo,
        mosoul_repo: IBeastMoSoulRepo,
    ):
        self.spirit_repo = spirit_repo
        self.bone_repo = bone_repo
        self.mosoul_repo = mosoul_repo
        self.bone_cfg = get_bone_system_config()

    def to_pvp_beasts(self, raw_beasts: List) -> List[PvpBeast]:
        """将数据库中的幻兽数据转换为 PvpBeast，并应用所有装备加成和技能效果。"""
        pvp_beasts: List[PvpBeast] = []
        for b in raw_beasts:
            pvp_beasts.append(self.to_pvp_beast(b))
        return pvp_beasts

    def to_pvp_beast(self, b) -> PvpBeast:
        """将单个原始幻兽转换为 PvpBeast"""
        stats = self.get_beast_stats(b)
        nature = getattr(b, "nature", "") or ""
        attack_type = "magic" if "法" in nature else "physical"
        skills = getattr(b, "skills", []) or []

        # 4) 技能系统：在装备加成后的属性上继续增减
        (
            final_hp,
            final_pa,
            final_ma,
            final_pd,
            final_md,
            final_spd,
            special_effects,
        ) = apply_buff_debuff_skills(
            skills=skills,
            attack_type=attack_type,
            raw_hp=stats["hp"],
            raw_physical_attack=stats["physical_attack"],
            raw_magic_attack=stats["magic_attack"],
            raw_physical_defense=stats["physical_defense"],
            raw_magic_defense=stats["magic_defense"],
            raw_speed=stats["speed"],
        )

        return PvpBeast(
            id=b.id,
            name=b.name,
            hp_max=final_hp,
            hp_current=final_hp,
            physical_attack=final_pa,
            magic_attack=final_ma,
            physical_defense=final_pd,
            magic_defense=final_md,
            speed=final_spd,
            grade=getattr(b, "grade", 0) or 0,
            hp_star=getattr(b, "hp_star", 0) or 0,
            attack_star=getattr(b, "attack_star", 0) or 0,
            physical_defense_star=getattr(b, "physical_defense_star", 0) or 0,
            magic_defense_star=getattr(b, "magic_defense_star", 0) or 0,
            speed_star=getattr(b, "speed_star", 0) or 0,
            hp_aptitude=getattr(b, "hp_aptitude", 0) or 0,
            attack_aptitude=(
                getattr(b, "magic_attack_aptitude", 0) or 0
                if attack_type == "magic"
                else getattr(b, "physical_attack_aptitude", 0) or 0
            ),
            physical_defense_aptitude=getattr(b, "physical_defense_aptitude", 0) or 0,
            magic_defense_aptitude=getattr(b, "magic_defense_aptitude", 0) or 0,
            speed_aptitude=getattr(b, "speed_aptitude", 0) or 0,
            attack_type=attack_type,
            skills=skills,
            poison_enhance=special_effects.get("poison_enhance", 0.0) or 0.0,
            critical_resist=special_effects.get("critical_resist", 0.0) or 0.0,
            immune_counter=bool(special_effects.get("immune_counter", False)),
            poison_resist=special_effects.get("poison_resist", 0.0) or 0.0,
        )

    def get_beast_stats(self, b) -> Dict[str, int]:
        """计算幻兽应用所有装备加成后的基础属性（不含技能加成）"""
        nature = getattr(b, "nature", "") or ""
        attack_type = "magic" if "法" in nature else "physical"

        # 裸属性
        raw_hp = int(getattr(b, "hp", 0) or 0)
        raw_pa = int(getattr(b, "physical_attack", 0) or 0)
        raw_ma = int(getattr(b, "magic_attack", 0) or 0)
        raw_pd = int(getattr(b, "physical_defense", 0) or 0)
        raw_md = int(getattr(b, "magic_defense", 0) or 0)
        raw_spd = int(getattr(b, "speed", 0) or 0)

        # 1) 战灵加成 (百分比)
        try:
            equipped_spirits = self.spirit_repo.get_by_beast_id(b.id)
        except Exception:
            equipped_spirits = []

        hp_bp, pa_bp, ma_bp, pd_bp, md_bp, spd_bp = 0, 0, 0, 0, 0, 0
        for sp in equipped_spirits:
            for ln in getattr(sp, "lines", []) or []:
                if not getattr(ln, "unlocked", False):
                    continue
                attr = getattr(ln, "attr_key", "") or ""
                val = int(getattr(ln, "value_bp", 0) or 0)
                if not attr or val <= 0:
                    continue

                if attr == "hp_pct":
                    hp_bp += val
                elif attr == "attack_pct":
                    if attack_type == "magic":
                        ma_bp += val
                    else:
                        pa_bp += val
                elif attr == "physical_defense_pct":
                    pd_bp += val
                elif attr == "magic_defense_pct":
                    md_bp += val
                elif attr == "speed_pct":
                    spd_bp += val

        # 2) 魔魂加成 (百分比 + 固定值)
        mosoul_pct_bonus = {"hp": 0.0, "physical_attack": 0.0, "magic_attack": 0.0, "physical_defense": 0.0, "magic_defense": 0.0, "speed": 0.0}
        mosoul_flat_bonus = {"hp": 0, "physical_attack": 0, "magic_attack": 0, "physical_defense": 0, "magic_defense": 0, "speed": 0}

        try:
            mosoul_slot = self.mosoul_repo.get_by_beast_id(b.id)
            if mosoul_slot:
                bonuses = mosoul_slot.get_total_stat_bonus()
                for attr, bonus in bonuses.items():
                    if attr in mosoul_pct_bonus:
                        mosoul_pct_bonus[attr] += bonus.get("percent", 0.0)
                        mosoul_flat_bonus[attr] += int(bonus.get("flat", 0))
        except Exception:
            pass

        # 计算百分比加成后的属性
        hp = raw_hp + int(raw_hp * (hp_bp / 10000 + mosoul_pct_bonus["hp"] / 100))
        pa = raw_pa + int(raw_pa * (pa_bp / 10000 + mosoul_pct_bonus["physical_attack"] / 100))
        ma = raw_ma + int(raw_ma * (ma_bp / 10000 + mosoul_pct_bonus["magic_attack"] / 100))
        pd = raw_pd + int(raw_pd * (pd_bp / 10000 + mosoul_pct_bonus["physical_defense"] / 100))
        md = raw_md + int(raw_md * (md_bp / 10000 + mosoul_pct_bonus["magic_defense"] / 100))
        spd = raw_spd + int(raw_spd * (spd_bp / 10000 + mosoul_pct_bonus["speed"] / 100))

        # 3) 战骨加成 (固定值)
        try:
            bones = self.bone_repo.get_by_beast_id(b.id)
        except Exception:
            bones = []

        bone_hp, bone_atk, bone_pd, bone_md, bone_spd = 0, 0, 0, 0, 0
        for bn in bones:
            st = self.bone_cfg.calc_bone_stats(bn.stage, bn.slot, bn.level)
            bone_hp += int(st.get("hp", 0) or 0)
            bone_atk += max(int(st.get("physical_attack", 0) or 0), int(st.get("magic_attack", 0) or 0))
            bone_pd += int(st.get("physical_defense", 0) or 0)
            bone_md += int(st.get("magic_defense", 0) or 0)
            bone_spd += int(st.get("speed", 0) or 0)

        # 加上固定值加成
        hp += bone_hp + mosoul_flat_bonus["hp"]
        pd += bone_pd + mosoul_flat_bonus["physical_defense"]
        md += bone_md + mosoul_flat_bonus["magic_defense"]
        spd += bone_spd + mosoul_flat_bonus["speed"]
        if attack_type == "magic":
            ma += bone_atk + mosoul_flat_bonus["magic_attack"]
        else:
            pa += bone_atk + mosoul_flat_bonus["physical_attack"]

        return {
            "hp": hp,
            "physical_attack": pa,
            "magic_attack": ma,
            "physical_defense": pd,
            "magic_defense": md,
            "speed": spd
        }

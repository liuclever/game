from typing import Optional, Dict, Any, List
from pathlib import Path
import json

from domain.entities.beast import BeastTemplate
from domain.repositories.beast_repo import IBeastTemplateRepo


class ConfigBeastTemplateRepo(IBeastTemplateRepo):
    """从 configs/beast_templates.json 读取幻兽模板

    兼容两种配置格式：
    1) 旧格式：顶层是 list[dict]
    2) 新格式：顶层是 dict，并包含 templates: list[dict]（当前 configs/beast_templates.json）
    """

    def __init__(self):
        self._templates: Dict[int, BeastTemplate] = {}
        self._load()

    def _select_default_realm(self, item: Dict[str, Any], realm_order: List[str]) -> str:
        # 优先显式 realm 字段
        realm = item.get("realm")
        if isinstance(realm, str) and realm:
            return realm

        realms = item.get("realms")
        if not isinstance(realms, dict) or not realms:
            return ""

        # 其次使用配置文件的 realm_order（若匹配）
        for r in realm_order:
            if r in realms:
                return r

        # 最后退回到 realms 的第一个 key
        try:
            return next(iter(realms.keys()))
        except Exception:
            return ""

    def _load(self):
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "configs" / "beast_templates.json"
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        realm_order: List[str] = []
        templates: List[Any]

        if isinstance(raw, list):
            templates = raw
        elif isinstance(raw, dict):
            realm_order_val = raw.get("realm_order")
            if isinstance(realm_order_val, list):
                realm_order = [str(x) for x in realm_order_val if isinstance(x, (str, int, float))]

            templates_val = raw.get("templates")
            if isinstance(templates_val, list):
                templates = templates_val
            else:
                raise ValueError(
                    f"configs/beast_templates.json 顶层为 dict，但未找到 templates(list)。keys={list(raw.keys())}"
                )
        else:
            raise ValueError(
                f"configs/beast_templates.json 格式错误：期望 list 或 dict，但得到 {type(raw).__name__}"
            )

        for item in templates:
            if not isinstance(item, dict):
                raise TypeError(
                    "configs/beast_templates.json templates 中每一项都必须是 dict，"
                    f"但遇到 {type(item).__name__}: {repr(item)[:200]}"
                )

            template_id = item.get("id")
            if not isinstance(template_id, int):
                # 尽量兼容 "id": "1" 这种写法
                try:
                    template_id = int(template_id)
                except Exception as e:
                    raise TypeError(f"BeastTemplate.id 必须是 int，但得到: {repr(item.get('id'))}") from e

            realm = self._select_default_realm(item, realm_order)
            realms_cfg = item.get("realms")
            realm_cfg: Dict[str, Any] = {}
            if isinstance(realms_cfg, dict) and realm:
                val = realms_cfg.get(realm)
                if isinstance(val, dict):
                    realm_cfg = val

            # 物攻资质上限（优先从 realm_cfg 读取）
            p_atk_aptitude_max = realm_cfg.get("physical_atk_aptitude_max") or item.get("physical_atk_aptitude_max") or 0
            # 法攻资质上限（优先从 realm_cfg 读取）
            m_atk_aptitude_max = realm_cfg.get("magic_atk_aptitude_max") or item.get("magic_atk_aptitude_max") or 0

            attack_type = str(item.get("attack_type", "physical"))
            # 配置中 historical 值为 magical，这里统一归一化为 magic
            if attack_type == "magical":
                attack_type = "magic"

            self._templates[int(template_id)] = BeastTemplate(
                # 基本信息
                id=int(template_id),
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),

                # 世界观 / 图鉴标签
                race=str(item.get("race", "")),
                realm=realm,
                trait=str(item.get("trait", "")),
                rarity=str(item.get("rarity", "")),
                habitat=str(item.get("habitat", "")),
                realms=realms_cfg if isinstance(realms_cfg, dict) else {},

                # 攻击类型
                attack_type=attack_type,

                # 基础属性 + 成长
                base_hp=int(item.get("base_hp", 100)),
                base_attack=int(item.get("base_attack", 10)),
                base_defense=int(item.get("base_defense", 10)),
                base_speed=int(item.get("base_speed", 10)),
                growth_hp=int(item.get("growth_hp", 10)),
                growth_attack=int(item.get("growth_attack", 2)),
                growth_defense=int(item.get("growth_defense", 1)),
                growth_speed=int(item.get("growth_speed", 1)),

                # 成长评分 & 各项资质上限（优先从 realm_cfg 读取）
                growth_score=int(realm_cfg.get("growth_score", item.get("growth_score", 0)) or 0),
                hp_aptitude_max=int(realm_cfg.get("hp_aptitude_max", item.get("hp_aptitude_max", 0)) or 0),
                speed_aptitude_max=int(realm_cfg.get("speed_aptitude_max", item.get("speed_aptitude_max", 0)) or 0),
                physical_atk_aptitude_max=int(p_atk_aptitude_max or 0),
                magic_atk_aptitude_max=int(m_atk_aptitude_max or 0),
                physical_def_aptitude_max=int(realm_cfg.get("physical_def_aptitude_max", item.get("physical_def_aptitude_max", 0)) or 0),
                magic_def_aptitude_max=int(realm_cfg.get("magic_def_aptitude_max", item.get("magic_def_aptitude_max", 0)) or 0),

                # 技能池
                all_skill_ids=item.get("all_skill_ids", []) if isinstance(item.get("all_skill_ids", []), list) else [],
                all_skill_names=item.get("all_skill_names", []) if isinstance(item.get("all_skill_names", []), list) else [],
            )

    def get_by_id(self, template_id: int) -> Optional[BeastTemplate]:
        return self._templates.get(template_id)

    def get_by_name(self, name: str) -> Optional[BeastTemplate]:
        for tpl in self._templates.values():
            if tpl.name == name:
                return tpl
        return None

    def get_all(self) -> Dict[int, BeastTemplate]:
        return self._templates.copy()

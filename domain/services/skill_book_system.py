"""技能书系统模块

实现幻兽技能修改（打书）功能。

打书规则：
- 0个技能：必定学会新技能（变成1个）
- 1-3个技能：50%概率增加技能，50%概率随机替换一个现有技能
- 4个技能：必定随机替换一个现有技能
- 同一幻兽不能拥有重复技能
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置文件路径
_SKILL_BOOK_CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "skill_books.json"
_SKILL_BOOK_CONFIG: Dict = {}


def _load_skill_book_config() -> Dict:
    """加载技能书配置文件"""
    global _SKILL_BOOK_CONFIG
    if not _SKILL_BOOK_CONFIG:
        with open(_SKILL_BOOK_CONFIG_PATH, "r", encoding="utf-8") as f:
            _SKILL_BOOK_CONFIG = json.load(f)
    return _SKILL_BOOK_CONFIG


def get_skill_book_config() -> Dict:
    """获取技能书配置"""
    return _load_skill_book_config()


def reload_skill_book_config() -> Dict:
    """重新加载技能书配置（用于热更新）"""
    global _SKILL_BOOK_CONFIG
    _SKILL_BOOK_CONFIG = {}
    return _load_skill_book_config()


@dataclass
class SkillBookResult:
    """打书结果"""
    success: bool = False
    action: str = ""  # "add" | "replace" | "failed"
    new_skill: str = ""
    replaced_skill: Optional[str] = None
    final_skills: List[str] = field(default_factory=list)
    message: str = ""


def get_skill_by_item_id(item_id: int) -> Optional[str]:
    """根据技能书道具ID获取对应的技能名称
    
    Args:
        item_id: 技能书道具ID
        
    Returns:
        技能名称，如果不是有效的技能书则返回 None
    """
    config = get_skill_book_config()
    item_id_str = str(item_id)
    return config.get("item_id_to_skill", {}).get(item_id_str)


def get_skill_book_info(item_id: int) -> Optional[Dict]:
    """获取技能书详细信息
    
    Args:
        item_id: 技能书道具ID
        
    Returns:
        技能书信息字典，包含 item_id, name, skill_name, description
    """
    config = get_skill_book_config()
    
    # 遍历所有分类查找
    for category, books in config.get("skill_books", {}).items():
        for book in books:
            if book.get("item_id") == item_id:
                return {
                    **book,
                    "category": category
                }
    return None


def is_valid_skill_book(item_id: int) -> bool:
    """检查是否是有效的技能书"""
    return get_skill_by_item_id(item_id) is not None


def get_replace_rules() -> Dict:
    """获取打书规则配置"""
    config = get_skill_book_config()
    return config.get("replace_rules", {
        "max_skills": 4,
        "add_chance": 0.5
    })


def use_skill_book(
    current_skills: List[str],
    skill_book_item_id: int,
    force_replace_index: Optional[int] = None
) -> SkillBookResult:
    """使用技能书修改幻兽技能
    
    Args:
        current_skills: 幻兽当前技能列表
        skill_book_item_id: 技能书道具ID
        force_replace_index: 强制替换指定索引的技能（可选，用于玩家选择）
        
    Returns:
        SkillBookResult 打书结果
    """
    # 获取技能书对应的技能
    new_skill = get_skill_by_item_id(skill_book_item_id)
    if not new_skill:
        return SkillBookResult(
            success=False,
            action="failed",
            message="无效的技能书"
        )
    
    # 检查是否已有该技能
    if new_skill in current_skills:
        return SkillBookResult(
            success=False,
            action="failed",
            new_skill=new_skill,
            final_skills=current_skills.copy(),
            message=f"幻兽已拥有【{new_skill}】技能，无法重复学习"
        )
    
    rules = get_replace_rules()
    max_skills = rules.get("max_skills", 4)
    add_chance = rules.get("add_chance", 0.5)
    
    skill_count = len(current_skills)
    final_skills = current_skills.copy()
    
    # 情况1：没有技能，必定学会
    if skill_count == 0:
        final_skills.append(new_skill)
        return SkillBookResult(
            success=True,
            action="add",
            new_skill=new_skill,
            replaced_skill=None,
            final_skills=final_skills,
            message=f"幻兽学会了【{new_skill}】！"
        )
    
    # 情况2：技能已满，必定替换
    if skill_count >= max_skills:
        if force_replace_index is not None:
            # 玩家指定替换位置
            if 0 <= force_replace_index < len(final_skills):
                replace_index = force_replace_index
            else:
                replace_index = random.randint(0, len(final_skills) - 1)
        else:
            # 随机选择替换
            replace_index = random.randint(0, len(final_skills) - 1)
        
        replaced_skill = final_skills[replace_index]
        final_skills[replace_index] = new_skill
        
        return SkillBookResult(
            success=True,
            action="replace",
            new_skill=new_skill,
            replaced_skill=replaced_skill,
            final_skills=final_skills,
            message=f"【{new_skill}】替换了【{replaced_skill}】！"
        )
    
    # 情况3：1-3个技能，随机增加或替换
    if force_replace_index is not None:
        # 玩家指定替换
        if 0 <= force_replace_index < len(final_skills):
            replaced_skill = final_skills[force_replace_index]
            final_skills[force_replace_index] = new_skill
            return SkillBookResult(
                success=True,
                action="replace",
                new_skill=new_skill,
                replaced_skill=replaced_skill,
                final_skills=final_skills,
                message=f"【{new_skill}】替换了【{replaced_skill}】！"
            )
        else:
            # 索引无效，当作增加处理
            final_skills.append(new_skill)
            return SkillBookResult(
                success=True,
                action="add",
                new_skill=new_skill,
                replaced_skill=None,
                final_skills=final_skills,
                message=f"幻兽学会了【{new_skill}】！"
            )
    
    # 随机决定增加还是替换
    if random.random() < add_chance:
        # 增加技能
        final_skills.append(new_skill)
        return SkillBookResult(
            success=True,
            action="add",
            new_skill=new_skill,
            replaced_skill=None,
            final_skills=final_skills,
            message=f"幻兽学会了【{new_skill}】！"
        )
    else:
        # 替换技能
        replace_index = random.randint(0, len(final_skills) - 1)
        replaced_skill = final_skills[replace_index]
        final_skills[replace_index] = new_skill
        
        return SkillBookResult(
            success=True,
            action="replace",
            new_skill=new_skill,
            replaced_skill=replaced_skill,
            final_skills=final_skills,
            message=f"【{new_skill}】替换了【{replaced_skill}】！"
        )


def get_all_skill_books() -> List[Dict]:
    """获取所有技能书列表
    
    Returns:
        技能书信息列表
    """
    config = get_skill_book_config()
    result = []
    
    for category, books in config.get("skill_books", {}).items():
        for book in books:
            result.append({
                **book,
                "category": category
            })
    
    return result


def get_skill_books_by_category(category: str) -> List[Dict]:
    """按分类获取技能书
    
    Args:
        category: 分类名称，如 "active_normal", "active_advanced" 等
        
    Returns:
        该分类下的技能书列表
    """
    config = get_skill_book_config()
    return config.get("skill_books", {}).get(category, [])


# 技能分类常量
SKILL_BOOK_CATEGORIES = [
    "active_normal",      # 普通主动技能书
    "active_advanced",    # 高级主动技能书
    "passive_normal",     # 普通被动技能书
    "passive_advanced",   # 高级被动技能书
    "buff_normal",        # 普通增益技能书
    "buff_advanced",      # 高级增益技能书
    "debuff",             # 负面技能书
]

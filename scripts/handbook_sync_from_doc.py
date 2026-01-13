from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


APT_LABEL_TO_KEY = {
    "成长率": "growth_rate",
    "气血资质": "hp_aptitude",
    "速度资质": "speed_aptitude",
    "物攻资质": "physical_attack_aptitude",
    "物防资质": "physical_defense_aptitude",
    "法攻资质": "magic_attack_aptitude",
    "法防资质": "magic_defense_aptitude",
}


def _stars_to_int(star_text: str) -> int:
    if not star_text:
        return 0
    return int(star_text.count("★"))


def _slice_section(doc_text: str, start_mark: str, end_mark: str) -> str:
    """
    截取 doc 文本的一个章节区间：
    - end_idx：首次出现 end_mark 的行
    - start_idx：end_idx 之前“最后一次出现 start_mark 的行”（避免目录里的（ 一 ）干扰）
    若找不到边界，则尽量返回可用片段。
    """
    lines = doc_text.splitlines()
    # 目录里也会出现（ 一 ）（ 二 ）（ 三 ），这里优先取“最后一次出现”的章节标题作为边界。
    end_candidates = [i for i, line in enumerate(lines) if end_mark in line]
    end_idx = end_candidates[-1] if end_candidates else len(lines)

    start_idx = 0
    for i in range(0, end_idx):
        if start_mark in lines[i]:
            start_idx = i
    return "\n".join(lines[start_idx:end_idx])


def parse_max_instances(doc_text: str) -> List[Dict]:
    """仅解析（一）章节里的“最高初始资质”条目为实例列表。"""
    instances: List[Dict] = []

    # 兼容不同空格/标点写法
    re_body = re.compile(r"^\s*\*\s*本体\s*[:：]\s*(.+?)\s*$")
    re_kv = {
        "realm": re.compile(r"^\s*境界\s*[:：]\s*(\S+)\s*$"),
        "nature": re.compile(r"^\s*特性\s*[:：]\s*(.+?)\s*$"),
        "rarity": re.compile(r"^\s*稀有\s*[:：]\s*(.+?)\s*$"),
        "location": re.compile(r"^\s*属地\s*[:：]\s*(.+?)\s*$"),
        "skills": re.compile(r"^\s*全技能\s*[:：]\s*(.+?)\s*$"),
    }
    re_max_marker = re.compile(r"^\s*最高初始资质\s*[:：]?\s*$")
    re_min_marker = re.compile(r"^\s*最低初始资质\s*[:：]?\s*$")
    re_apt = re.compile(r"^\s*(成长率|气血资质|速度资质|物攻资质|物防资质|法攻资质|法防资质)\s*[:：]\s*(\d+)\s*(?:\(([^)]*)\))?\s*$")

    cur: Optional[Dict] = None
    in_max_block = False
    for raw_line in doc_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m = re_body.match(line)
        if m:
            if cur:
                instances.append(cur)
            body = m.group(1).strip()
            name = body.split("(", 1)[0].strip()
            race = ""
            if "(" in body and body.endswith(")"):
                race = body.rsplit("(", 1)[-1].rstrip(")").strip()
            cur = {
                "name": name,
                "body": body,
                "race": race,
                "realm": "",
                "nature": "",
                "rarity": "",
                "location": "",
                "aptitudes": {},  # label -> {value, stars}
                "skills": [],  # [skillName]
            }
            in_max_block = False
            continue

        if not cur:
            continue

        if re_max_marker.match(line):
            in_max_block = True
            continue
        if re_min_marker.match(line):
            # 最高资质解析阶段：遇到最低资质标记直接关闭解析，避免覆盖
            in_max_block = False
            continue

        for k, rx in re_kv.items():
            mm = rx.match(line)
            if not mm:
                continue
            v = mm.group(1).strip()
            if k == "skills":
                parts = [x.strip() for x in v.split("|")]
                cur["skills"] = [x for x in parts if x]
            else:
                cur[k] = v
            break
        else:
            if in_max_block:
                am = re_apt.match(line)
                if am:
                    label = am.group(1).strip()
                    value = int(am.group(2))
                    stars = _stars_to_int((am.group(3) or "").strip())
                    cur["aptitudes"][label] = {"value": value, "stars": stars}

    if cur:
        instances.append(cur)

    # 只保留“解析完整”的实例（至少需要 name + realm + 若干资质）
    filtered: List[Dict] = []
    for it in instances:
        if not it.get("name") or not it.get("realm"):
            continue
        if not isinstance(it.get("aptitudes"), dict) or not it["aptitudes"]:
            continue
        filtered.append(it)
    return filtered


def parse_min_aptitudes(doc_text: str) -> Dict[Tuple[str, str], Dict[str, Dict]]:
    """
    解析（二）章节的“最低初始资质”（地界）为：
    (name, race) -> { aptitude_key -> {value, stars, label} }
    """
    section = _slice_section(doc_text, "（二）", "（三）")
    # 支持“* 本体:xxx”与“* 本体xxx”两种写法
    re_body = re.compile(r"^\s*\*\s*本体\s*(?:[:：]\s*)?(.+?)\s*$")
    re_realm = re.compile(r"^\s*境界\s*[:：]\s*(\S+)\s*$")
    re_min_marker = re.compile(r"^\s*最低初始资质\s*[:：]?\s*$")
    re_apt = re.compile(r"^\s*(成长率|气血资质|速度资质|物攻资质|物防资质|法攻资质|法防资质)\s*[:：]\s*(\d+)\s*(?:\(([^)]*)\))?\s*$")

    result: Dict[Tuple[str, str], Dict[str, Dict]] = {}
    cur_key: Optional[Tuple[str, str]] = None
    in_min_block = False

    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m = re_body.match(line)
        if m:
            body = m.group(1).strip()
            name = body.split("(", 1)[0].strip()
            race = ""
            if "(" in body and body.endswith(")"):
                race = body.rsplit("(", 1)[-1].rstrip(")").strip()
            cur_key = (name, race)
            in_min_block = False
            if cur_key not in result:
                result[cur_key] = {}
            continue

        if cur_key is None:
            continue

        rm = re_realm.match(line)
        if rm:
            # 仅接收地界最低资质
            realm = rm.group(1).strip()
            if realm != "地界":
                cur_key = None
                in_min_block = False
            continue

        if re_min_marker.match(line):
            in_min_block = True
            continue

        if in_min_block:
            am = re_apt.match(line)
            if am:
                label = am.group(1).strip()
                value = int(am.group(2))
                stars = _stars_to_int((am.group(3) or "").strip())
                keyname = APT_LABEL_TO_KEY.get(label)
                if not keyname:
                    continue
                result[cur_key][keyname] = {
                    "value": value,
                    "stars": stars,
                    "label": label,
                }
    return result


def merge_instances(instances: List[Dict], realms_order: List[str]) -> Dict[Tuple[str, str], Dict]:
    """
    将实例按 (name, race) 合并为“宠物”维度，并聚合各境界资质。
    """
    merged: Dict[Tuple[str, str], Dict] = {}
    for it in instances:
        name = str(it.get("name") or "").strip()
        race = str(it.get("race") or "").strip()
        key = (name, race)
        pet = merged.setdefault(
            key,
            {
                "name": name,
                "race": race,
                "body": str(it.get("body") or "").strip(),
                "nature": str(it.get("nature") or "").strip(),
                "rarity": str(it.get("rarity") or "").strip(),
                "location": str(it.get("location") or "").strip(),
                "skills": list(it.get("skills") or []),
                "aptitudes_by_realm": {},  # realm -> key->aptObj
            },
        )

        # 若后续实例补全了空字段，则以非空覆盖
        for f in ["body", "nature", "rarity", "location"]:
            if not pet.get(f) and it.get(f):
                pet[f] = str(it.get(f) or "").strip()

        # skills 若此前为空，则采用当前；否则保持第一个（尽量少改）
        if (not pet.get("skills")) and it.get("skills"):
            pet["skills"] = list(it.get("skills") or [])

        realm = str(it.get("realm") or "").strip()
        raw_apts = it.get("aptitudes") or {}

        apt_obj_by_key: Dict[str, Dict] = {}
        for label, keyname in APT_LABEL_TO_KEY.items():
            if label not in raw_apts:
                continue
            v = raw_apts[label]
            apt_obj_by_key[keyname] = {
                "value": int(v.get("value") or 0),
                "stars": int(v.get("stars") or 0),
                "label": label,
            }

        if apt_obj_by_key:
            pet["aptitudes_by_realm"][realm] = apt_obj_by_key

    # 规范化：按 realms_order 过滤/排序 evolution_chain
    for pet in merged.values():
        have = set(pet.get("aptitudes_by_realm", {}).keys())
        chain = [r for r in realms_order if r in have]
        # 若出现其他境界名字（不在 realms_order），也附加到末尾，避免丢数据
        others = [r for r in sorted(have) if r not in set(realms_order)]
        pet["evolution_chain"] = chain + others
    return merged


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Dict):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="将 幻兽图鉴说明.doc 导出的 txt 数据同步到 configs/handbook.json（配置驱动图鉴）。")
    ap.add_argument("--doc", default="handbook_doc_export.utf8.txt", help="UTF-8 doc 导出文本路径（相对仓库根）")
    ap.add_argument("--config", default="configs/handbook.json", help="handbook 配置路径（相对仓库根）")
    ap.add_argument("--write", action="store_true", help="写回 configs/handbook.json（否则仅输出报告）")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    doc_path = (root / args.doc).resolve()
    config_path = (root / args.config).resolve()

    if not doc_path.exists():
        raise SystemExit(f"doc not found: {doc_path}")
    if not config_path.exists():
        raise SystemExit(f"config not found: {config_path}")

    cfg = load_json(config_path) or {}
    realms_order = [str(x).strip() for x in (cfg.get("realms") or ["地界", "灵界", "神界"]) if str(x).strip()]

    doc_text = doc_path.read_text(encoding="utf-8", errors="replace")

    # 章节（一）/（二）严格分离，避免“最低资质覆盖最高资质”
    section_max = _slice_section(doc_text, "（一）", "（二）")
    instances = parse_max_instances(section_max)
    merged = merge_instances(instances, realms_order=realms_order)
    min_apts = parse_min_aptitudes(doc_text)

    # categories: name -> id
    categories = list(cfg.get("categories") or [])
    cat_name_to_id: Dict[str, int] = {}
    max_cat_id = 0
    for c in categories:
        try:
            cid = int(c.get("id"))
            max_cat_id = max(max_cat_id, cid)
            cat_name_to_id[str(c.get("name") or "").strip()] = cid
        except Exception:
            continue

    # skills: name -> key（用于点击进入技能详情）
    skills_dict = cfg.get("skills") or {}
    skill_name_to_key: Dict[str, str] = {}
    if isinstance(skills_dict, dict):
        for k, info in skills_dict.items():
            if not isinstance(info, dict):
                continue
            name = str(info.get("name") or "").strip()
            if name and k:
                # 若有重名，保留第一个（避免大范围改动）
                skill_name_to_key.setdefault(name, str(k))

    existing_pets = list(cfg.get("pets") or [])
    existing_by_key: Dict[Tuple[str, str], Dict] = {}
    max_pet_id = 0
    for p in existing_pets:
        try:
            pid = int(p.get("id"))
            max_pet_id = max(max_pet_id, pid)
        except Exception:
            continue
        name = str(p.get("name") or "").strip()
        body = str(p.get("body") or "").strip()
        race = ""
        if "(" in body and body.endswith(")"):
            race = body.rsplit("(", 1)[-1].rstrip(")").strip()
        existing_by_key[(name, race)] = p

    missing_skill_names: List[str] = []
    updated = 0
    created = 0

    # 同步到 pets（按 name+race 覆盖/补全）
    for (name, race), pet_info in merged.items():
        cat_id = cat_name_to_id.get(race)
        if cat_id is None:
            # 若出现新族群，追加分类（尽量不破坏现有）
            max_cat_id += 1
            cat_id = max_cat_id
            categories.append({"id": cat_id, "name": race or f"未知族群{cat_id}", "total_pages": 1})
            cat_name_to_id[race] = cat_id

        chain: List[str] = list(pet_info.get("evolution_chain") or [])
        evo_from = chain[0] if chain else ""
        evo_to = chain[-1] if len(chain) >= 2 else (chain[0] if chain else "")

        apts_by_realm: Dict[str, Dict] = pet_info.get("aptitudes_by_realm") or {}
        base_realm = chain[0] if chain else next(iter(apts_by_realm.keys()), "")
        base_apts = apts_by_realm.get(base_realm) or {}

        # skills 处理：name->key（找不到则 key 置空）
        skills_payload = []
        for sname in (pet_info.get("skills") or []):
            key = skill_name_to_key.get(str(sname).strip(), "")
            if not key:
                missing_skill_names.append(str(sname).strip())
            skills_payload.append({"name": str(sname).strip(), "key": key})

        existed = existing_by_key.get((name, race))
        if existed:
            existed["category_id"] = int(cat_id)
            existed["name"] = name
            existed["body"] = pet_info.get("body") or existed.get("body") or ""
            existed["nature"] = pet_info.get("nature") or existed.get("nature") or ""
            existed["rarity"] = pet_info.get("rarity") or existed.get("rarity") or ""
            existed["location"] = pet_info.get("location") or existed.get("location") or ""
            existed["evolution_chain"] = chain
            existed["evolution"] = {"from": evo_from, "to": evo_to}
            if base_apts:
                existed["max_initial_aptitudes"] = base_apts
            existed["skills"] = skills_payload
            src = existed.get("source") or {}
            if not isinstance(src, dict):
                src = {}
            src["max_initial_aptitudes_by_realm"] = apts_by_realm
            low = min_apts.get((name, race))
            if isinstance(low, dict) and low:
                src["min_initial_aptitudes"] = low
            existed["source"] = src
            updated += 1
        else:
            max_pet_id += 1
            new_pet = {
                "id": int(max_pet_id),
                "category_id": int(cat_id),
                "name": name,
                "body": pet_info.get("body") or name,
                "evolution": {"from": evo_from, "to": evo_to},
                "evolution_chain": chain,
                "nature": pet_info.get("nature") or "",
                "rarity": pet_info.get("rarity") or "",
                "location": pet_info.get("location") or "",
                "max_initial_aptitudes": base_apts,
                "skills": skills_payload,
                "source": {
                    "max_initial_aptitudes_by_realm": apts_by_realm,
                    "min_initial_aptitudes": min_apts.get((name, race)) or {},
                },
            }
            existing_pets.append(new_pet)
            created += 1

    # 重新排序 pets：保持 id 递增，尽量减少 diff 抖动
    existing_pets.sort(key=lambda x: int(x.get("id") or 0))

    # 重建 category_pages / total_pages（分页大小与前端一致：10）
    page_size = 10
    category_pages: Dict[str, Dict[str, List[int]]] = {}
    for c in categories:
        try:
            cid = int(c.get("id"))
        except Exception:
            continue
        ids = [int(p.get("id")) for p in existing_pets if int(p.get("category_id") or 0) == cid]
        pages: Dict[str, List[int]] = {}
        for idx, pid in enumerate(ids):
            page_no = idx // page_size + 1
            pages.setdefault(str(page_no), []).append(pid)
        total_pages = max([int(k) for k in pages.keys()], default=1)
        c["total_pages"] = int(total_pages)
        category_pages[str(cid)] = pages

    # 写回 cfg
    cfg["categories"] = categories
    cfg["pets"] = existing_pets
    cfg["category_pages"] = category_pages
    # 将 doc 全文逐行写入配置，供图鉴说明页 1:1 展示
    cfg["doc_text"] = doc_text.splitlines()

    # 报告
    uniq_missing_skills = sorted({x for x in missing_skill_names if x})
    print(f"[handbook-sync] instances={len(instances)} pets_in_doc={len(merged)} updated={updated} created={created}")
    print(f"[handbook-sync] min_aptitudes_pets={len(min_apts)} doc_lines={len(cfg.get('doc_text') or [])}")
    if uniq_missing_skills:
        print(f"[handbook-sync] missing_skill_keys_by_name={len(uniq_missing_skills)} (示例前20): {uniq_missing_skills[:20]}")

    if args.write:
        write_json(config_path, cfg)
        print(f"[handbook-sync] wrote: {config_path}")


if __name__ == "__main__":
    main()



"""tests/init_beast.py

简单脚本：测试 beast_factory.create_initial_beast 初始化后的幻兽实例会带上哪些字段信息。

运行方式（在项目根目录）：
    python -m tests.init_beast.init_beast
"""

from dataclasses import asdict

from infrastructure.config.beast_template_repo_from_config import ConfigBeastTemplateRepo
from domain.services.beast_factory import create_initial_beast


def main() -> None:
    # 1. 读取模板（这里以 id=1 的小黑鼠为例）
    template_repo = ConfigBeastTemplateRepo()
    template = template_repo.get_by_id(1)
    if template is None:
        print("未找到 id=1 的幻兽模板")
        return

    print("[模板信息 BeastTemplate]")
    print(template)

    # 2. 使用 beast_factory 初始化一只新的幻兽实例
    beast = create_initial_beast(user_id=42, template=template)

    print("\n[初始化后的幻兽实例 Beast]")
    print(beast)

    # 3. 以 dict 形式打印，方便查看每个字段的值
    print("\n[Beast 字段明细 as dict]")
    for k, v in asdict(beast).items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

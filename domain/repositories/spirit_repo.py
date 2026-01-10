try:
    from typing import Protocol, Optional, List
except ImportError:
    from typing_extensions import Protocol
    from typing import Optional, List

from domain.entities.spirit import Spirit, SpiritAccount


class ISpiritRepo(Protocol):
    """玩家战灵数据访问接口"""

    def get_by_user_id(self, user_id: int) -> List[Spirit]:
        ...

    def get_by_id(self, spirit_id: int) -> Optional[Spirit]:
        ...

    def get_by_beast_id(self, beast_id: int) -> List[Spirit]:
        ...

    def save(self, spirit: Spirit) -> None:
        ...

    def delete(self, spirit_id: int) -> None:
        ...


class ISpiritAccountRepo(Protocol):
    """玩家战灵账户数据访问接口"""

    def get_by_user_id(self, user_id: int) -> SpiritAccount:
        ...

    def save(self, account: SpiritAccount) -> None:
        ...

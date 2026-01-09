import pytest

from application.services.refine_pot_service import RefinePotService, RefinePotError
from domain.entities.player import Player


class MockPlayerRepo:
    def __init__(self):
        self.players = {}

    def get_by_id(self, user_id: int):
        return self.players.get(user_id)

    def save(self, player: Player):
        self.players[player.user_id] = player


class MockBeast:
    def __init__(self, beast_id, user_id, **attrs):
        self.id = beast_id
        self.user_id = user_id
        self.nickname = attrs.get("nickname", f"beast-{beast_id}")
        for key, value in attrs.items():
            setattr(self, key, value)


class MockPlayerBeastRepo:
    def __init__(self):
        self.beasts = {}
        self.deleted = set()

    def add(self, beast):
        self.beasts[(beast.user_id, beast.id)] = beast

    def get_by_user_and_id(self, user_id, beast_id):
        return self.beasts.get((user_id, beast_id))

    def save(self, beast):
        self.beasts[(beast.user_id, beast.id)] = beast

    def delete_beast(self, beast_id, user_id):
        key = (user_id, beast_id)
        if key in self.beasts:
            self.deleted.add(beast_id)
            del self.beasts[key]
            return True
        return False


class MockInventoryService:
    def __init__(self, pills=0):
        self.items = pills

    def has_item(self, user_id, item_id, qty):
        return self.items >= qty

    def remove_item(self, user_id, item_id, qty=1):
        if self.items < qty:
            raise ValueError
        self.items -= qty


class MockLogRepo:
    def __init__(self):
        self.entries = []

    def insert_log(self, entry):
        self.entries.append(entry)


def make_service(gold=200000, pills=10, delta=10):
    player_repo = MockPlayerRepo()
    player_repo.players[1] = Player(user_id=1, nickname="hero", level=1, exp=0, gold=gold)
    beast_repo = MockPlayerBeastRepo()
    inv = MockInventoryService(pills=pills)
    log_repo = MockLogRepo()

    def fake_rand(low, high):
        return delta

    return (
        RefinePotService(
            player_repo=player_repo,
            player_beast_repo=beast_repo,
            inventory_service=inv,
            refine_log_repo=log_repo,
            rand_func=fake_rand,
        ),
        player_repo,
        beast_repo,
        inv,
        log_repo,
    )


def test_refine_success_high_diff():
    svc, _, beast_repo, _, log_repo = make_service()
    main = MockBeast(10, 1, hp_aptitude=100)
    sub = MockBeast(11, 1, hp_aptitude=250)
    beast_repo.add(main)
    beast_repo.add(sub)

    result = svc.refine(1, 10, 11, "hp")

    assert result["after"] == 110
    assert 11 in beast_repo.deleted
    assert len(log_repo.entries) == 1


def test_refine_requires_higher_sub():
    svc, _, beast_repo, _, _ = make_service()
    beast_repo.add(MockBeast(10, 1, hp_aptitude=200))
    beast_repo.add(MockBeast(11, 1, hp_aptitude=150))

    with pytest.raises(RefinePotError):
        svc.refine(1, 10, 11, "hp")


def test_refine_fails_on_insufficient_resources():
    svc, _, beast_repo, _, _ = make_service(gold=1000, pills=0)
    beast_repo.add(MockBeast(10, 1, hp_aptitude=100))
    beast_repo.add(MockBeast(11, 1, hp_aptitude=130))

    with pytest.raises(RefinePotError):
        svc.refine(1, 10, 11, "hp")

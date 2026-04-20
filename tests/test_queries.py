from __future__ import annotations

from sce.core.queries import GraphQueryLayer
from sce.core.types import Attractor, Constraint, Link, RelationType, State
from sce.storage.memory import MemoryRepository


def _make_state(repo: MemoryRepository, name: str, stability: float) -> State:
    s = State(state_type="test", data={"name": name})
    s.stability = stability
    repo.add_state(s)
    return s


def test_top_stable():
    repo = MemoryRepository()
    a = _make_state(repo, "a", 0.2)
    b = _make_state(repo, "b", 0.9)
    c = _make_state(repo, "c", 0.5)

    q = GraphQueryLayer(repo)
    result = q.top_stable(2)

    assert [s.data["name"] for s in result] == ["b", "c"]


def test_fragile():
    repo = MemoryRepository()
    s1 = _make_state(repo, "ok", 0.5)
    s2 = _make_state(repo, "bad", 0.5)
    s2.data["x"] = 10

    constraint = Constraint(
        name="x_lt_5",
        constraint_type="test",
        scope_type="state_type",
        scope_ref="test",
        hard=True,
        predicate=lambda s: s.data.get("x", 0) < 5,
    )

    q = GraphQueryLayer(repo)
    result = q.fragile(constraint)

    assert s2 in result
    assert s1 not in result


def test_nearest_attractor():
    repo = MemoryRepository()
    a = _make_state(repo, "a", 0.4)
    b = _make_state(repo, "b", 0.6)
    c = _make_state(repo, "c", 0.8)

    repo.add_link(Link(a.state_id, b.state_id, RelationType.SUPPORTS, 1.0))
    repo.add_link(Link(b.state_id, c.state_id, RelationType.SUPPORTS, 1.0))

    attractor = Attractor(
        attractor_type="test",
        signature_hash="sig",
        invariant={},
        member_state_ids=[c.state_id],
        stability_score=0.8,
    )
    repo.add_attractor(attractor)

    q = GraphQueryLayer(repo)
    result = q.nearest_attractor(a.state_id)

    assert result is not None
    assert result.signature_hash == "sig"


def test_path_to():
    repo = MemoryRepository()
    a = _make_state(repo, "a", 0.2)
    b = _make_state(repo, "b", 0.5)
    c = _make_state(repo, "c", 0.9)

    repo.add_link(Link(a.state_id, b.state_id, RelationType.SUPPORTS, 1.0))
    repo.add_link(Link(b.state_id, c.state_id, RelationType.SUPPORTS, 1.0))

    q = GraphQueryLayer(repo)
    path = q.path_to(a.state_id, c.state_id)

    assert path is not None
    assert path.state_ids[0] == a.state_id
    assert path.state_ids[-1] == c.state_id
    assert path.stability_score > 0

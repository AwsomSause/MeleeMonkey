from pathlib import Path

from backend.generation.caching.cache_key import cache_key, is_cacheable
from backend.generation.providers.base import GenerationRequest, Operation, ReferenceInput


def _req(**kw: object) -> GenerationRequest:
    base: dict[str, object] = {"operation": Operation.GENERATE, "model": "m-1", "prompt": "p",
                                "width": 96, "height": 96, "seed": 1}
    base.update(kw)
    return GenerationRequest(**base)  # type: ignore[arg-type]


def _ref(sha: str, path: str = "x.png", priority: int = 90) -> ReferenceInput:
    return ReferenceInput(sha256=sha, path=path, priority=priority, role="approved_concept")


def test_identical_inputs_share_key() -> None:
    assert cache_key("p", _req()) == cache_key("p", _req())


def test_every_output_affecting_input_changes_key() -> None:
    base = cache_key("p", _req())
    variants = [
        cache_key("other", _req()),
        cache_key("p", _req(model="m-2")),
        cache_key("p", _req(prompt="q")),
        cache_key("p", _req(width=128)),
        cache_key("p", _req(seed=2)),
        cache_key("p", _req(references=(_ref("a"),))),
        cache_key("p", _req(), {"palette": "gba"}),
    ]
    assert len({base, *variants}) == len(variants) + 1


def test_reference_order_and_path_do_not_matter() -> None:
    a = _req(references=(_ref("a", "one/a.png"), _ref("b")))
    b = _req(references=(_ref("b"), _ref("a", "moved/a.png")))
    assert cache_key("p", a) == cache_key("p", b)


def test_reference_content_and_priority_matter() -> None:
    assert cache_key("p", _req(references=(_ref("a"),))) != cache_key(
        "p", _req(references=(_ref("b"),)))
    assert cache_key("p", _req(references=(_ref("a", priority=90),))) != cache_key(
        "p", _req(references=(_ref("a", priority=10),)))


def test_source_image_hashed_by_content(tmp_path: Path) -> None:
    f1, f2 = tmp_path / "1.png", tmp_path / "2.png"
    f1.write_bytes(b"same")
    f2.write_bytes(b"same")
    edit = {"operation": Operation.EDIT}
    assert cache_key("p", _req(source_image_path=str(f1), **edit)) == cache_key(
        "p", _req(source_image_path=str(f2), **edit))
    f2.write_bytes(b"different")
    assert cache_key("p", _req(source_image_path=str(f1), **edit)) != cache_key(
        "p", _req(source_image_path=str(f2), **edit))


def test_unseeded_variations_not_cacheable() -> None:
    assert not is_cacheable(_req(operation=Operation.VARIATIONS, seed=None))
    assert is_cacheable(_req(operation=Operation.VARIATIONS, seed=5))

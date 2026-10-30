import io

import pytest
from PIL import Image

from backend.generation.providers.base import (
    CostSource,
    GenerationRequest,
    InvalidRequest,
    Operation,
    ProviderCapabilities,
    ReferenceInput,
    UnsupportedOperation,
)
from backend.generation.providers.mock import MockImageProvider


def _request(**overrides: object) -> GenerationRequest:
    base: dict[str, object] = {
        "operation": Operation.GENERATE, "model": "mock-1", "prompt": "a test creature",
        "width": 96, "height": 96,
    }
    base.update(overrides)
    return GenerationRequest(**base)  # type: ignore[arg-type]


async def test_mock_generates_transparent_png_of_requested_size() -> None:
    result = await MockImageProvider().run(_request(num_images=3))
    assert len(result.images) == 3
    img = Image.open(io.BytesIO(result.images[0].data))
    assert img.size == (96, 96) and img.mode == "RGBA"
    assert img.getpixel((0, 0))[3] == 0
    assert result.cost.source is CostSource.FREE


async def test_mock_is_deterministic() -> None:
    a = await MockImageProvider().run(_request())
    b = await MockImageProvider().run(_request())
    assert a.images[0].data == b.images[0].data


async def test_unsupported_operation_is_refused() -> None:
    provider = MockImageProvider(ProviderCapabilities(operations=frozenset({Operation.GENERATE})))
    with pytest.raises(UnsupportedOperation):
        await provider.run(_request(operation=Operation.EDIT, source_image_path="x.png"))
    assert provider.calls == []


async def test_capability_limits_enforced_before_call() -> None:
    provider = MockImageProvider(ProviderCapabilities(
        operations=frozenset(Operation), max_reference_images=1, max_variations=2,
        sizes=((96, 96),),
    ))
    ref = ReferenceInput(sha256="a", path="a.png", priority=90, role="approved_base_sprite")
    with pytest.raises(InvalidRequest):
        await provider.run(_request(references=(ref, ref)))
    with pytest.raises(InvalidRequest):
        await provider.run(_request(num_images=3))
    with pytest.raises(InvalidRequest):
        await provider.run(_request(width=128, height=128))
    with pytest.raises(UnsupportedOperation):
        await provider.run(_request(mask_path="m.png"))
    assert provider.calls == []


async def test_edit_requires_source_image() -> None:
    with pytest.raises(InvalidRequest):
        await MockImageProvider().run(_request(operation=Operation.EDIT))

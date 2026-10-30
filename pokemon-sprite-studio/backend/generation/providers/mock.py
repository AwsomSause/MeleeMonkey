"""Deterministic, free provider for tests and offline development.

Output depends only on the request, so cache and regression tests are stable.
Each image is a simple transparent-background blob whose colour is derived
from the request hash — enough to exercise processing and storage code.
"""

from __future__ import annotations

import hashlib
import io

from PIL import Image, ImageDraw

from .base import (
    CostEstimate,
    CostSource,
    GeneratedImage,
    GenerationRequest,
    GenerationResult,
    ImageProvider,
    Operation,
    ProviderCapabilities,
)


class MockImageProvider(ImageProvider):
    provider_id = "mock"
    display_name = "Mock (offline, free)"

    def __init__(self, capabilities: ProviderCapabilities | None = None) -> None:
        self._caps = capabilities or ProviderCapabilities(
            operations=frozenset(Operation),
            max_reference_images=8,
            supports_mask=True,
            supports_transparency=True,
            supports_seed=True,
            supports_negative_prompt=True,
            max_variations=8,
            requires_network=False,
        )
        self.calls: list[GenerationRequest] = []

    async def get_capabilities(self) -> ProviderCapabilities:
        return self._caps

    async def estimate_cost(self, request: GenerationRequest) -> CostEstimate:
        return CostEstimate(amount_usd=0.0, source=CostSource.FREE)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        return self._render(request)

    async def edit(self, request: GenerationRequest) -> GenerationResult:
        return self._render(request)

    async def generate_variations(self, request: GenerationRequest) -> GenerationResult:
        return self._render(request)

    def _render(self, request: GenerationRequest) -> GenerationResult:
        self.calls.append(request)
        digest = hashlib.sha256(request.model_dump_json().encode()).digest()
        images = []
        for index in range(request.num_images):
            r, g, b = digest[index % 30], digest[(index + 1) % 30], digest[(index + 2) % 30]
            img = Image.new("RGBA", (request.width, request.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            pad_x, pad_y = request.width // 4, request.height // 4
            draw.ellipse(
                (pad_x, pad_y, request.width - pad_x, request.height - pad_y),
                fill=(r, g, b, 255),
                outline=(0, 0, 0, 255),
            )
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            images.append(GeneratedImage(data=buf.getvalue(), seed=request.seed))
        return GenerationResult(
            provider_id=self.provider_id,
            model=request.model,
            images=images,
            cost=CostEstimate(amount_usd=0.0, source=CostSource.FREE),
            latency_ms=0,
        )

"""Content-addressed cache keys for generation results.

A key changes whenever anything that can change the output changes: provider,
model version, prompt, reference *content* (by hash, not path), dimensions,
generation parameters, or the processing configuration applied afterwards.
Unseeded requests are never cacheable for variation requests, because the user
is explicitly asking for new output.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..providers.base import GenerationRequest, Operation

CACHE_KEY_VERSION = 1


def cache_key(
    provider_id: str,
    request: GenerationRequest,
    processing_config: dict[str, Any] | None = None,
) -> str:
    payload = {
        "v": CACHE_KEY_VERSION,
        "provider": provider_id,
        "request": request.model_dump(
            mode="json", exclude={"references", "source_image_path", "mask_path"}
        ),
        # Content hashes and weighting, sorted so ordering in the UI does not
        # change the key; paths are excluded so relocating a project does not.
        "references": sorted((r.sha256, r.priority, r.role) for r in request.references),
        "source_image": _file_sha256(request.source_image_path),
        "mask": _file_sha256(request.mask_path),
        "processing": processing_config or {},
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def is_cacheable(request: GenerationRequest) -> bool:
    return not (request.operation is Operation.VARIATIONS and request.seed is None)


def _file_sha256(path: str | None) -> str | None:
    if path is None:
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()

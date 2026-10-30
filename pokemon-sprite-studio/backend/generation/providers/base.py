"""Image-provider contract.

Every adapter (OpenAI, Gemini, FLUX, local SD, mock) implements
:class:`ImageProvider`. Adapters know nothing about projects, species or the
database: they turn a :class:`GenerationRequest` into a :class:`GenerationResult`.

Callers must consult :meth:`ImageProvider.get_capabilities` before choosing an
operation. Adapters raise :class:`UnsupportedOperation` rather than emulate a
feature they do not have.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Operation(StrEnum):
    GENERATE = "generate"
    EDIT = "edit"
    VARIATIONS = "variations"


class CostSource(StrEnum):
    ESTIMATE = "estimate"      # computed locally from a price table
    REPORTED = "reported"      # returned by the provider for this request
    FREE = "free"              # local or mock provider


class ProviderCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True)

    operations: frozenset[Operation]
    max_reference_images: int = 0
    supports_mask: bool = False
    supports_transparency: bool = False   # native alpha output
    supports_seed: bool = False
    supports_negative_prompt: bool = False
    is_async: bool = False                # jobs must be polled via get_job_status
    reports_actual_cost: bool = False
    max_variations: int = 1
    sizes: tuple[tuple[int, int], ...] = ()  # empty = any size
    requires_network: bool = True

    def supports(self, op: Operation) -> bool:
        return op in self.operations


class ReferenceInput(BaseModel):
    """A reference image passed to a provider, already approved for upload."""

    model_config = ConfigDict(frozen=True)

    sha256: str
    path: str                 # absolute path on disk, resolved by orchestration
    priority: int = Field(ge=0, le=100)
    role: str                 # e.g. "approved_base_sprite", "style_example"


class GenerationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    operation: Operation
    model: str
    prompt: str
    negative_prompt: str = ""
    width: int = Field(gt=0, le=4096)
    height: int = Field(gt=0, le=4096)
    num_images: int = Field(default=1, ge=1, le=16)
    references: tuple[ReferenceInput, ...] = ()
    source_image_path: str | None = None   # required for EDIT
    mask_path: str | None = None
    seed: int | None = None
    transparent_background: bool = True
    quality: str = "standard"              # "preview" | "standard" | "final"
    extra: dict[str, str | int | float | bool] = Field(default_factory=dict)


class GeneratedImage(BaseModel):
    model_config = ConfigDict(frozen=True)

    data: bytes
    mime_type: str = "image/png"
    seed: int | None = None


class CostEstimate(BaseModel):
    model_config = ConfigDict(frozen=True)

    amount_usd: float = Field(ge=0)
    source: CostSource
    note: str = ""


class JobState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobStatus(BaseModel):
    job_id: str
    state: JobState
    progress: float = Field(default=0, ge=0, le=1)
    error: str | None = None


class GenerationResult(BaseModel):
    provider_id: str
    model: str
    images: list[GeneratedImage]
    cost: CostEstimate
    latency_ms: int
    provider_job_id: str | None = None
    raw_metadata: dict[str, object] = Field(default_factory=dict)


# --- errors -----------------------------------------------------------------


class ProviderError(Exception):
    """Base class. ``retryable`` tells orchestration whether to retry."""

    retryable = False

    def __init__(self, provider_id: str, message: str) -> None:
        super().__init__(f"[{provider_id}] {message}")
        self.provider_id = provider_id


class UnsupportedOperation(ProviderError):
    pass


class InvalidRequest(ProviderError):
    pass


class RateLimited(ProviderError):
    retryable = True


class TransientProviderError(ProviderError):
    retryable = True


class ContentRejected(ProviderError):
    """The provider's safety system refused the request."""


class AuthenticationError(ProviderError):
    pass


# --- contract ---------------------------------------------------------------


class ImageProvider(ABC):
    provider_id: str
    display_name: str

    @abstractmethod
    async def get_capabilities(self) -> ProviderCapabilities: ...

    @abstractmethod
    async def estimate_cost(self, request: GenerationRequest) -> CostEstimate: ...

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        raise UnsupportedOperation(self.provider_id, "generate not supported")

    async def edit(self, request: GenerationRequest) -> GenerationResult:
        raise UnsupportedOperation(self.provider_id, "edit not supported")

    async def generate_variations(self, request: GenerationRequest) -> GenerationResult:
        raise UnsupportedOperation(self.provider_id, "variations not supported")

    async def get_job_status(self, job_id: str) -> JobStatus:
        raise UnsupportedOperation(self.provider_id, "provider is synchronous")

    async def run(self, request: GenerationRequest) -> GenerationResult:
        """Validate against capabilities, then dispatch to the right operation."""
        caps = await self.get_capabilities()
        if not caps.supports(request.operation):
            raise UnsupportedOperation(
                self.provider_id, f"{request.operation.value} not supported"
            )
        if len(request.references) > caps.max_reference_images:
            raise InvalidRequest(
                self.provider_id,
                f"{len(request.references)} references exceeds limit of "
                f"{caps.max_reference_images}",
            )
        if request.num_images > caps.max_variations:
            raise InvalidRequest(
                self.provider_id,
                f"{request.num_images} images exceeds limit of {caps.max_variations}",
            )
        if request.mask_path and not caps.supports_mask:
            raise UnsupportedOperation(self.provider_id, "masked editing not supported")
        if caps.sizes and (request.width, request.height) not in caps.sizes:
            raise InvalidRequest(
                self.provider_id, f"size {request.width}x{request.height} not supported"
            )
        if request.operation is Operation.EDIT and not request.source_image_path:
            raise InvalidRequest(self.provider_id, "edit requires source_image_path")

        dispatch = {
            Operation.GENERATE: self.generate,
            Operation.EDIT: self.edit,
            Operation.VARIATIONS: self.generate_variations,
        }
        return await dispatch[request.operation](request)

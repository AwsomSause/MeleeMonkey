"""Versioned, machine-readable design specification.

The AI Director produces these; identity profiles store them; prompt templates
consume them. ``schemas/design_spec.v1.json`` is generated from this module by
``python -m backend.identity.design_spec``; never edit the JSON by hand.

Bump ``SCHEMA_VERSION`` and add a migration function in ``upgrade`` for any
change that is not purely additive.
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION: Final = 1

# Deliverables are open-ended strings so new asset types need no schema change;
# these are the ones the application knows how to produce out of the box.
KNOWN_DELIVERABLES = frozenset({
    "concept", "front_battle", "back_battle", "front_battle_shiny", "back_battle_shiny",
    "overworld", "icon_party", "icon_dex",
    "idle_animation", "physical_attack_animation", "special_attack_animation",
    "damage_animation", "faint_animation", "victory_animation",
})


class MovementClass(StrEnum):
    QUADRUPED = "quadruped"
    BIPED = "biped"
    FLYING = "flying"
    FLOATING = "floating"
    SERPENTINE = "serpentine"
    AQUATIC = "aquatic"
    INSECTOID = "insectoid"
    HEAVY = "heavy"
    MECHANICAL = "mechanical"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IdentityConstraints(_Model):
    preserve_silhouette: bool = True
    preserve_facial_identity: bool = True
    preserve_body_proportions: bool = True
    preserve_markings: bool = True
    preserve_palette: bool = False


class Anatomy(_Model):
    silhouette: str = ""
    proportions: str = ""
    head_shape: str = ""
    eyes: str = ""
    limbs: str = ""
    markings: list[str] = Field(default_factory=list)
    accessories: list[str] = Field(default_factory=list)
    texture: str = ""


class PaletteColor(_Model):
    name: str
    hex: str

    @field_validator("hex")
    @classmethod
    def _check_hex(cls, value: str) -> str:
        if len(value) != 7 or value[0] != "#" or any(
            c not in "0123456789abcdefABCDEF" for c in value[1:]
        ):
            raise ValueError(f"expected #RRGGBB, got {value!r}")
        return value.lower()


class VisualChanges(_Model):
    """Differences from the parent form. Empty for a base form."""

    palette: str = ""
    aura: str = ""
    eyes: str = ""
    shading: str = ""
    anatomy: str = ""
    other: list[str] = Field(default_factory=list)


class StyleDirectives(_Model):
    preset: str = "custom"
    outline: Literal["none", "dark", "colored", "selective"] = "dark"
    pixel_clusters: Literal["clean", "textured", "dithered"] = "clean"
    shading: str = ""
    max_colors: int | None = Field(default=None, ge=2, le=256)


class DesignSpec(_Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    species: str = Field(min_length=1)
    form: str = "base"
    parent_form: str | None = None
    movement_classes: list[MovementClass] = Field(default_factory=list)
    identity: IdentityConstraints = Field(default_factory=IdentityConstraints)
    anatomy: Anatomy = Field(default_factory=Anatomy)
    palette: list[PaletteColor] = Field(default_factory=list)
    visual_changes: VisualChanges = Field(default_factory=VisualChanges)
    style: StyleDirectives = Field(default_factory=StyleDirectives)
    negative_constraints: list[str] = Field(default_factory=list)
    deliverables: list[str] = Field(default_factory=lambda: ["concept"])

    @field_validator("deliverables")
    @classmethod
    def _non_empty_unique(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("at least one deliverable is required")
        if len(set(value)) != len(value):
            raise ValueError("deliverables must be unique")
        return value


def upgrade(data: dict[str, Any]) -> dict[str, Any]:
    """Bring a stored spec up to the current schema version."""
    version = data.get("schema_version", 1)
    if version > SCHEMA_VERSION:
        raise ValueError(f"spec schema v{version} is newer than this application")
    # Future: if version == 1: data = _v1_to_v2(data)
    return data


def load(data: dict[str, Any]) -> DesignSpec:
    return DesignSpec.model_validate(upgrade(data))


def json_schema() -> dict[str, Any]:
    schema = DesignSpec.model_json_schema()
    schema["$id"] = f"https://psas.local/schemas/design_spec.v{SCHEMA_VERSION}.json"
    return schema


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[2] / "schemas" / f"design_spec.v{SCHEMA_VERSION}.json"
    out.write_text(json.dumps(json_schema(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")

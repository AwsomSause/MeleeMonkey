import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from backend.identity.design_spec import SCHEMA_VERSION, DesignSpec, json_schema, load

SHADOW_GARDEVOIR = {
    "species": "Gardevoir",
    "form": "shadow",
    "parent_form": "base",
    "movement_classes": ["biped", "floating"],
    "identity": {"preserve_silhouette": True, "preserve_facial_identity": True,
                 "preserve_body_proportions": True},
    "palette": [{"name": "aura", "hex": "#3A1F5C"}],
    "visual_changes": {"palette": "darkened", "aura": "shadow energy",
                       "eyes": "intense", "shading": "dramatic"},
    "style": {"preset": "gba_inspired", "outline": "dark", "pixel_clusters": "clean"},
    "deliverables": ["front_battle", "back_battle", "idle_animation",
                     "physical_attack_animation"],
}
SCHEMA_FILE = Path(__file__).resolve().parents[2] / "schemas" / f"design_spec.v{SCHEMA_VERSION}.json"


def test_example_spec_validates() -> None:
    spec = load(SHADOW_GARDEVOIR)
    assert spec.palette[0].hex == "#3a1f5c"
    assert spec.schema_version == SCHEMA_VERSION


def test_round_trip() -> None:
    spec = load(SHADOW_GARDEVOIR)
    assert load(json.loads(spec.model_dump_json())) == spec


@pytest.mark.parametrize("bad", [
    {"species": ""},
    {"species": "X", "unknown_field": 1},
    {"species": "X", "palette": [{"name": "a", "hex": "red"}]},
    {"species": "X", "deliverables": []},
    {"species": "X", "deliverables": ["front_battle", "front_battle"]},
    {"species": "X", "movement_classes": ["teleporting"]},
])
def test_invalid_specs_rejected(bad: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        DesignSpec.model_validate(bad)


def test_future_schema_version_rejected() -> None:
    with pytest.raises(ValueError, match="newer"):
        load({"species": "X", "schema_version": SCHEMA_VERSION + 1})


def test_committed_json_schema_is_up_to_date() -> None:
    assert json.loads(SCHEMA_FILE.read_text()) == json_schema(), (
        "Regenerate with: python -m backend.identity.design_spec")


def test_json_schema_accepts_example() -> None:
    jsonschema.validate(SHADOW_GARDEVOIR, json_schema())

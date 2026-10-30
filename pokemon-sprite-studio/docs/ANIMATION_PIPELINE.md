# Animation Pipeline

Highest technical risk in the project. The design principle: **AI supplies
poses; deterministic code supplies position, timing and assembly.**

## Concepts

- **Template** (`assets/animation_templates/*.json`, `animation_template` table):
  keyframes with descriptions, per-frame timing, movement paths, anchor
  behaviour, expected bounds, loop flag, optional effects, and the movement
  classes it suits.
- **Keyframe plan**: a template adapted to one species by the Animation
  Director using the spec's `movement_classes` and anatomy. Lists which
  frames are AI poses vs. transforms.
- **Frame**: one image with `source` (`ai`, `transform`, `manual`,
  `interpolated`), duration, offset and status.

## Modes

| Mode | Key poses | In-betweens | Cost | Use for |
|---|---|---|---|---|
| Template (B) | none — approved sprite only | transforms | free | idle, hover, bob, damage flash |
| AI keyframes (A) | AI | AI | high | unique signature moves |
| **Hybrid (C, default)** | AI | transforms + selective edits | medium | attacks, faint, victory |

## Transform library (deterministic)

Whole-sprite: translate, squash/stretch about an anchor, rotate (nearest
neighbour, ≤ ~15° to limit pixel damage), flash/tint, palette cycle, fade.
Region-based: the user (or Director) marks regions on the approved sprite
(e.g. wings, tail, head) in the editor; transforms can move one region and
re-composite. This gives wing flaps and tail swishes without generation.

## Consistency inputs for every AI frame

Approved base sprite · previous approved keyframe · next approved keyframe (if
any) · identity profile · template frame description · locked palette ·
canvas size and anchor.

## Consistency checks

| Kind | Check | Method |
|---|---|---|
| Spatial | anchor/ground contact drift | lowest opaque row & alpha centroid per frame vs. template path |
| Spatial | scale drift | opaque area & bbox vs. base sprite, tolerance per template |
| Visual | palette drift | colours outside locked palette (after mapping) |
| Visual | silhouette drift | IoU of alpha masks vs. nearest keyframe after alignment |
| Temporal | jumps | centroid delta between consecutive frames vs. template path |
| Temporal | duplicates | identical hashes / near-identical frames not intended as holds |
| Temporal | loop seam | last→first frame delta for looping animations |

Smooth interpolation is never assumed correct: interpolated frames are
flagged for review and can be replaced or regenerated individually.

## Flow

Approved sprite → template → keyframe plan → key poses (regenerate any single
pose) → consistency analysis → transitions → align/normalize → preview →
approve → export. Approved animations are versioned like assets; editing an
approved animation creates a new version.

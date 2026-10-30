# M7 — Animation Engine

Read `CLAUDE.md`, `IMPLEMENTATION_PLAN.md` and `docs/ARCHITECTURE.md` first.
Before coding, write this milestone's checklist, risks and acceptance criteria
into `IMPLEMENTATION_PLAN.md`. Finish by following the completion rules there.

## Goal

Template, AI-keyframe and hybrid animation per docs/ANIMATION_PIPELINE.md.

## Tasks

1. Template schema (Pydantic) + loader for `assets/animation_templates/`; ship idle (breathing, hovering), physical attack (lunge), special attack (charge), damage, faint, victory.
2. Transform library (whole-sprite + region-based) with tests.
3. Keyframe plan generation (Animation Director, mockable); per-pose generation with the consistency inputs listed in the doc; regenerate a single pose.
4. Consistency analyzers (spatial, visual, temporal) → animation QA report.
5. Assembly: align to anchor, normalize canvas, set durations, loop.
6. Animation Studio UI: large preview, playback speed, loop toggle, keyframe list, template selector, frame properties, movement path view, compare with previous approved version.
7. Animation regression tests on fixture creatures of each body plan.

## Acceptance

- Template-mode idle for every fixture creature with zero provider calls; anchors stable (QA passes).
- Hybrid attack on the Gardevoir demo: AI key poses + transforms, previewable and approvable.

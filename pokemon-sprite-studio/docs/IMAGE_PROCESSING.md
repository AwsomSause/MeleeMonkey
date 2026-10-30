# Image Processing

All processing functions live in `backend/processing/`, are pure (images in,
images + report out), and never touch the database. Raw provider output is
never modified; each stage writes a new image and the pipeline records the
stage list and parameters in `asset_version.processing_json`, so any result
can be reproduced or re-run with different settings.

## Pipeline

| # | Stage | Default implementation | Notes |
|---|---|---|---|
| 1 | Background segmentation | Use provider alpha if present; else flood-fill from corners on a near-uniform background; else `rembg` (optional dependency) | Report which method ran |
| 2 | Transparency validation | Alpha histogram | Flags semi-transparent fringe and opaque backgrounds |
| 3 | Crop + canvas normalization | Bounding box of alpha > threshold, placed on target canvas at style-profile anchor (e.g. bottom-centre for battle sprites) | Keeps scale consistent between front/back via shared scale factor |
| 4 | Resolution conversion | Detect native pixel grid (see below); downsample by grid mode, not average | Never bilinear for final output |
| 5 | Palette analysis | Count colours, cluster in OKLab | Report |
| 6 | Colour reduction | Median cut / k-means in OKLab to style-profile `max_colors`, protect outline + eye colours | Only when the profile limits colours |
| 7 | Outline inspection | Detect outline colour; find gaps in the 1-px silhouette border | Warning, optional auto-fix |
| 8 | Cluster cleanup | Remove isolated pixels / 1-px orphans whose colour differs from all 4-neighbours | Cleanup mode only |
| 9 | Alpha cleanup | Binarize alpha at threshold | |
| 10 | Validation | See checks below | Produces a `quality_report` |

## Grid-aware downsampling

AI output is often "fake pixel art": a large image with soft, uneven pseudo-pixels.
Estimate the pixel pitch from the autocorrelation of edge positions (or accept
the target resolution from the style profile), then for each output cell take
the **mode** colour of the cell's centre region. This preserves hard edges and
avoids the blur a plain resize creates.

## Modes

- **Preserve** — stages 1–4, 9, 10. Keeps pixel structure.
- **Cleanup** (default for generated assets) — all stages; conservative
  thresholds.
- **Reconstruction** — re-quantize and redraw outlines aggressively. Opt-in
  only, never default; shows a before/after diff.

## Palette operations

- Palette mapping: map every colour to the nearest colour of a chosen palette
  (OKLab distance).
- Shiny / recolour: an explicit `from → to` colour map applied to an approved
  sprite; front and back share the same map so they stay consistent.

## Automated checks vs. human review

| Check | Automated verdict? |
|---|---|
| Dimensions, alpha validity, PNG encoding | Yes (fail) |
| Opaque background, semi-transparent pixels | Yes (fail / warn) |
| Colour count over limit | Yes (warn) |
| Stray pixels, broken outline, inconsistent pixel size | Warn — needs human review |
| Blurry edges (ratio of intermediate colours along edges) | Warn |

# Control Stack 2026

## Depth / parallax
`Video Depth Anything Small -> depth map -> harum_parallax.py -> cinematic 2.5D shot`

This path is valuable because final motion is deterministic and approved face pixels are not regenerated. Video Depth Anything Small is Apache-2.0; larger variants are non-commercial by default.

## Segmentation
SAM 2 can track masks through video. Use cases:
- isolate hand, charcoal and paper;
- selectively grade background;
- replace window/canvas without repainting the face;
- composite a generated background behind an approved character layer.

## Pose / flow
Pose, optical flow and depth are control signals for animation models or ComfyUI. They guide motion while FACE LOCK remains the identity source.

## Review
Every generated shot creates a review contact sheet through `harum_review.py`; it can be inspected by a human or VLM before the shot moves from QC to Approved.

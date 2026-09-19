# Colab policy guard

The zero-cost architecture deliberately separates **generation** from **identity animation**.

- Google Colab free is useful for direct notebook computation, but resource availability is dynamic.
- Do **not** use the managed free Colab runtime for deepfake/real-person face animation.
- Harum Noir production on free Colab should use: FLUX.2 image generation/editing and LTX image-to-video for synthetic scenes, subject to Colab's current rules.
- LivePortrait remains documented only as an optional local/custom-runtime experiment; it is not required by the production pipeline.
- The guaranteed zero-subscription fallback is the GitHub Actions CPU renderer: still/image + motion design + synthetic pt-BR narration + FFmpeg.

This keeps the main workflow operational even when no GPU is available.

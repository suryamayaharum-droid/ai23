# Microvideo Editing

`harum_edit.py` receives approved microvideos and builds a larger master with short transitions.

```bash
python harum_edit.py shot01.mp4 shot02.mp4 shot03.mp4 \
  --transition 0.16 --effect fadeblack \
  -o HARUM_SCENE_MASTER.mp4
```

For Harum Noir, use transitions sparingly: cut, fade or fadeblack. Motion, framing and sound should carry continuity instead of flashy effects.

The editor can create a subtle procedural room-tone bed. VOICE LOCK and music are added later without regenerating the visual master.

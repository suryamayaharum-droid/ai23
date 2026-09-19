#!/usr/bin/env python3
"""Export a Harum scene JSON to OpenTimelineIO when opentimelineio is installed."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("scene")
    ap.add_argument("--out",default="harum_timeline.otio"); a=ap.parse_args()
    try: import opentimelineio as otio
    except ImportError:
        raise SystemExit("Install optional dependency: pip install opentimelineio OpenTimelineIO-Plugins")
    data=json.loads(Path(a.scene).read_text(encoding="utf-8"))
    fps=float(data.get("output",{}).get("fps",30))
    timeline=otio.schema.Timeline(name=data.get("project",data.get("scene","Harum Scene")))
    track=otio.schema.Track(name="V1",kind=otio.schema.TrackKind.Video)
    for i,shot in enumerate(data.get("shots",[]),1):
        dur=float(shot.get("duration",0)); src=shot.get("output") or shot.get("src") or ""
        ref=otio.schema.ExternalReference(target_url=str(src)) if src else otio.schema.MissingReference()
        clip=otio.schema.Clip(name=shot.get("id",f"shot-{i:02}"),media_reference=ref)
        clip.source_range=otio.opentime.TimeRange(
          start_time=otio.opentime.RationalTime(0,fps),
          duration=otio.opentime.RationalTime(round(dur*fps),fps))
        clip.metadata["harum"]={k:shot.get(k) for k in ("motion","engine","task","narrative_role","prompt") if k in shot}
        track.append(clip)
    timeline.tracks.append(track)
    otio.adapters.write_to_file(timeline,a.out); print(a.out)

if __name__=="__main__": main()

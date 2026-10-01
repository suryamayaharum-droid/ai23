#!/usr/bin/env python3
import argparse,json
from pathlib import Path

def build(intent):
    n=lambda i,k,d,e,o: {"id":i,"kind":k,"deps":d,"engine_hint":e,"deliverable":o,"status":"planned"}
    return {"scene_id":intent["scene_id"],"zero_extra_spend":True,"nodes":[
      n("narrative","narrative",[],"CineBrain/StoryGraph","shot list + continuity"),
      n("keyframes","image",["narrative"],"FLUX.2 Klein / Qwen-Image","approved keyframes"),
      n("motion_a","video",["keyframes"],"Wan2.2 + DiffSynth/LightX2V","microshots lane A"),
      n("motion_b","video",["keyframes"],"Wan2.2 + DiffSynth/LightX2V","microshots lane B"),
      n("masks","control",["motion_a","motion_b"],"SAM 2","masks"),
      n("audio","audio",["narrative"],"Voice Lock + ACE-Step + procedural foley","stems"),
      n("edit","editorial",["motion_a","motion_b","masks","audio"],"FFmpeg/CineGrid","scene master"),
      n("qc","qc",["edit"],"FFmpeg/QC","report"),
      n("publish_pack","distribution",["qc"],"provenance/metadata","channel package")
    ]}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("intent"); p.add_argument("--out",default="dag.json")
    a=p.parse_args(); out=build(json.loads(Path(a.intent).read_text())); Path(a.out).write_text(json.dumps(out,indent=2)); print(a.out)

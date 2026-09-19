#!/usr/bin/env python3
from __future__ import annotations
import json, os, platform
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

def total_ram_gb()->float:
    try:
        if Path("/proc/meminfo").exists():
            line=next(x for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith("MemTotal:"))
            return int(line.split()[1])/1024/1024
    except Exception:
        pass
    return float(os.environ.get("HARUM_RAM_GB","8"))

def registry():
    return json.loads((HERE/"config"/"models.json").read_text(encoding="utf-8"))

def select_brains(mode:str="default",ram_gb:float|None=None)->dict[str,Any]:
    cfg=registry()
    ram=ram_gb or total_ram_gb()
    ids=cfg["assembly_roles"].get(mode,cfg["assembly_roles"]["default"])
    by_id={b["id"]:b for b in cfg["brains"]}
    selected=[]
    skipped=[]
    for bid in ids:
        b=by_id[bid]
        if ram >= float(b.get("min_ram_gb",0)):
            selected.append(b)
        else:
            skipped.append({"id":bid,"reason":f"needs {b['min_ram_gb']} GB RAM; detected {ram:.1f}"})
    if len(selected)<2:
        fallback=sorted(
            [b for b in cfg["brains"] if b["class"]=="core" and ram>=float(b.get("min_ram_gb",0))],
            key=lambda x:-x["priority"]
        )
        selected=fallback[:2]
    return {
      "mode":mode,
      "ram_gb":round(ram,2),
      "architecture":platform.machine(),
      "brains":[b["id"] for b in selected],
      "models":selected,
      "skipped":skipped
    }

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",default="default")
    args=ap.parse_args()
    print(json.dumps(select_brains(args.mode),ensure_ascii=False,indent=2))

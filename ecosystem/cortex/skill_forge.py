#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

from tool_kernel import ToolKernel

HERE=Path(__file__).resolve().parent
REQUIRED={"id","description","tools","max_steps","required_capabilities","output_schema"}

class SkillForge:
    def __init__(self):
        self.allowed_tools=set(ToolKernel().describe())

    def validate(self,skill:dict[str,Any])->dict[str,Any]:
        errors=[]
        missing=REQUIRED-set(skill)
        if missing: errors.append("missing:"+",".join(sorted(missing)))
        tools=set(skill.get("tools",[]))
        bad=tools-self.allowed_tools
        if bad: errors.append("forbidden_tools:"+",".join(sorted(bad)))
        steps=int(skill.get("max_steps",0) or 0)
        if steps<1 or steps>8: errors.append("max_steps must be 1..8")
        if not skill.get("required_capabilities"):errors.append("capabilities required")
        if not skill.get("output_schema"):errors.append("output schema required")
        return {"valid":not errors,"errors":errors}

    def candidate(self,skill:dict[str,Any],evidence:dict[str,Any])->dict[str,Any]:
        v=self.validate(skill)
        body={
          "skill":skill,
          "validation":v,
          "evidence":evidence,
          "status":"CANDIDATE" if v["valid"] else "REJECTED"
        }
        body["candidate_id"]=hashlib.sha256(
            json.dumps(body,sort_keys=True).encode()).hexdigest()[:16]
        return body

    def promote(self,candidate:dict[str,Any],eval_before:float,eval_after:float)->dict[str,Any]:
        allowed=(
          candidate["validation"]["valid"] and
          eval_after>eval_before and
          candidate["status"]=="CANDIDATE"
        )
        return {
          "candidate_id":candidate["candidate_id"],
          "status":"PROMOTED" if allowed else "REJECTED",
          "eval_before":eval_before,
          "eval_after":eval_after
        }

if __name__=="__main__":
    print(json.dumps({
      "allowed_tools":sorted(SkillForge().allowed_tools),
      "registry":json.loads((HERE/"config"/"skills.json").read_text(encoding="utf-8"))
    },ensure_ascii=False,indent=2))

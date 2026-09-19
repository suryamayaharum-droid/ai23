#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from typing import Any

from brain_router import select_brains
from llama_brain import LlamaCppBrain

HERE=Path(__file__).resolve().parent

BASE_SYSTEM="""You are one cell in the HARUM Cortex Assembly.
Return concise, useful conclusions. Do not pretend certainty.
Do not expose private chain-of-thought. Provide only:
ANSWER, CONFIDENCE (0-1), RISKS, CHECKS, HANDOFF.
Use available context; if evidence is insufficient, say so."""

class CortexAssembly:
    def __init__(self,mode:str="default"):
        self.plan=select_brains(mode)

    def _call(self,model:dict[str,Any],role:str,task:str,context:str="")->dict[str,Any]:
        brain=LlamaCppBrain(model)
        prompt=f"""ROLE: {role}
TASK:
{task}

SHARED CONTEXT:
{context[-12000:]}

Produce an independent proposal. Do not imitate other brains."""
        return brain.infer(BASE_SYSTEM,prompt)

    def deliberate(self,task:str,context:str="")->dict[str,Any]:
        models=self.plan["models"]
        proposals=[]
        for m in models:
            role=" + ".join(m["role"])
            try:
                proposals.append(self._call(m,role,task,context))
            except Exception as exc:
                proposals.append({"brain":m["id"],"error":f"{type(exc).__name__}: {exc}"})

        valid=[p for p in proposals if "text" in p]
        if not valid:
            return {"status":"NO_LOCAL_BRAIN","proposals":proposals,"plan":self.plan}

        synthesis_model=next((m for m in models if "synthesizer" in m["role"]),models[0])
        evidence="\n\n".join(
            f"PROPOSAL {i+1} [{p['brain']}]:\n{p['text']}" for i,p in enumerate(valid)
        )
        synthesis_prompt=f"""ORIGINAL TASK:
{task}

INDEPENDENT PROPOSALS:
{evidence}

Synthesize a final answer by preserving agreements, explicitly flagging disagreements,
and rejecting unsupported assertions. Do not output hidden reasoning.
Return:
FINAL
CONSENSUS
DISAGREEMENTS
CONFIDENCE
NEXT ACTIONS
"""
        try:
            final=LlamaCppBrain(synthesis_model).infer(
                "You are the assembly chair. Merge independent outputs without inventing facts.",
                synthesis_prompt,max_tokens=700,temperature=0.1,seed=7
            )
        except Exception as exc:
            final={"brain":synthesis_model["id"],"error":str(exc)}

        packet={
          "schema":"harum.cortex.assembly.v1",
          "task_digest":hashlib.sha256(task.encode()).hexdigest(),
          "timestamp":int(time.time()),
          "plan":self.plan,
          "proposals":proposals,
          "final":final
        }
        return packet

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--mode",default="default")
    ap.add_argument("--context",default="")
    args=ap.parse_args()
    print(json.dumps(CortexAssembly(args.mode).deliberate(args.task,args.context),ensure_ascii=False,indent=2))

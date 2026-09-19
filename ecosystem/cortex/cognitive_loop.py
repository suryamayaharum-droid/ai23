#!/usr/bin/env python3
from __future__ import annotations
import json,re
from typing import Any

from llama_brain import LlamaCppBrain
from brain_router import select_brains
from tool_kernel import ToolKernel,ToolError

PROTOCOL="""You are a HARUM local agent.
You may either answer or request one local tool.
Never output hidden chain-of-thought.
For a tool request output ONLY JSON:
{"action":"tool","tool":"<name>","args":{...}}
For a final answer output ONLY JSON:
{"action":"final","answer":"...","confidence":0.0,"checks":["..."]}
Use no tool outside the provided allowlist."""

class CognitiveLoop:
    def __init__(self,root:str=".",mode:str="default",max_steps:int=6):
        plan=select_brains(mode)
        if not plan["models"]:
            raise RuntimeError("no local brain fits available RAM")
        self.model=plan["models"][0]
        self.brain=LlamaCppBrain(self.model)
        self.kernel=ToolKernel(root)
        self.max_steps=max(1,min(max_steps,10))

    def _extract_json(self,text:str)->dict[str,Any]:
        text=text.strip()
        try:return json.loads(text)
        except Exception:
            m=re.search(r"\{.*\}",text,re.S)
            if not m: raise ValueError("brain did not return protocol JSON")
            return json.loads(m.group(0))

    def run(self,task:str,context:str=""):
        transcript=[]
        state=f"TASK: {task}\nCONTEXT: {context}\nTOOLS: {json.dumps(self.kernel.describe())}"
        for step in range(self.max_steps):
            out=self.brain.infer(PROTOCOL,state,max_tokens=350,temperature=0.1,seed=100+step)
            msg=self._extract_json(out["text"])
            transcript.append({"step":step,"brain":out["brain"],"message":msg})
            if msg.get("action")=="final":
                return {"status":"COMPLETED","final":msg,"transcript":transcript}
            if msg.get("action")!="tool":
                return {"status":"PROTOCOL_ERROR","transcript":transcript}
            try:
                result=self.kernel.call(msg["tool"],msg.get("args",{}))
            except Exception as exc:
                result={"error":f"{type(exc).__name__}: {exc}"}
            transcript.append({"step":step,"tool":msg.get("tool"),"result":result})
            state += f"\nSTEP {step} TOOL RESULT:\n{json.dumps(result,ensure_ascii=False)[:12000]}"
        return {"status":"STEP_LIMIT","transcript":transcript}

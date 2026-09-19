#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, tempfile, urllib.request
from pathlib import Path
from typing import Any

class LlamaCppBrain:
    def __init__(self, model:dict[str,Any], llama_cli:str|None=None):
        self.model=model
        self.llama_cli=llama_cli or os.getenv("LLAMA_CLI") or shutil.which("llama-cli")
        if not self.llama_cli:
            raise RuntimeError("llama-cli not installed; provision llama.cpp first")

    def infer(self, system:str, prompt:str, *,
              max_tokens:int=512, temperature:float=0.2, seed:int=42)->dict[str,Any]:
        full=f"""<system>
{system}
</system>
<user>
{prompt}
</user>
"""
        cmd=[
          self.llama_cli,
          "-hf",f"{self.model['repo']}:{self.model['quant']}",
          "-p",full,
          "-n",str(max_tokens),
          "--temp",str(temperature),
          "--seed",str(seed),
          "--no-display-prompt"
        ]
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=int(os.getenv("HARUM_MODEL_TIMEOUT","900")))
        if proc.returncode!=0:
            raise RuntimeError(proc.stderr[-2000:])
        return {
          "brain":self.model["id"],
          "repo":self.model["repo"],
          "quant":self.model["quant"],
          "seed":seed,
          "text":proc.stdout.strip()
        }

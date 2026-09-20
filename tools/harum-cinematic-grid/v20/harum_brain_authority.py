#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

ALLOWLIST={
  "verify_hash",
  "verify_signature",
  "store_cas",
  "read_memory",
  "append_memory",
  "request_research",
  "request_human_review"
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def authorize(requested_action, *, capability_verified, signature_verified, resource_allowed, tests_passed):
    checks={
      "action_allowlisted":requested_action in ALLOWLIST,
      "capability_verified":bool(capability_verified),
      "signature_verified":bool(signature_verified),
      "resource_allowed":bool(resource_allowed),
      "tests_passed":bool(tests_passed)
    }
    return {"allowed":all(checks.values()),"checks":checks,"authority":"deterministic-gates","brain_authority":False}

def advisory(decision_path):
    return {
      "type":"harum.brain.advisory.v1",
      "sha256":sha(decision_path),
      "authority":False,
      "note":"LLM output may propose work but cannot grant execution authority."
    }

if __name__=="__main__":
    # Self-test: even persuasive brain text cannot authorize a non-allowlisted action.
    denied=authorize("shell_arbitrary",capability_verified=True,signature_verified=True,resource_allowed=True,tests_passed=True)
    allowed=authorize("verify_hash",capability_verified=True,signature_verified=True,resource_allowed=True,tests_passed=True)
    out={"dangerous_action_denied":not denied["allowed"],"safe_action_allowed":allowed["allowed"],"denied":denied,"allowed":allowed}
    print(json.dumps(out,indent=2))
    if not out["dangerous_action_denied"] or not out["safe_action_allowed"]:
        raise SystemExit(2)

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from durable_journal import DurableJournal
from resource_broker import choose, compose
from resilient_executor import ResilientExecutor
from supervisor_tree import Supervisor, Child
from reconciler import reconcile

class ResourceFabricTests(unittest.TestCase):
    def test_broker_selects_active_compute(self):
        r=choose(["python"])
        self.assertIsNotNone(r["resource"])
        self.assertIn("python",r["covered"])

    def test_composed_fabric_can_cover_control_state(self):
        r=compose(["python","git_history","shared_state","checkpoint"])
        self.assertTrue(r["complete"],r)

    def test_journal_replay_is_idempotent_by_event_id(self):
        with tempfile.TemporaryDirectory() as td:
            j=DurableJournal(td)
            a=j.append("x",{"n":1})
            b=j.append("x",{"n":2})
            self.assertEqual(len(j.replay()),2)
            state=j.materialize()
            self.assertEqual(state["event_count"],2)
            self.assertEqual(state["last_by_topic"]["x"]["payload"]["n"],2)

    def test_executor_caches_success(self):
        with tempfile.TemporaryDirectory() as td:
            j=DurableJournal(td)
            ex=ResilientExecutor(j)
            calls={"n":0}
            def fn(payload):
                calls["n"]+=1
                return {"value":payload["value"]*2}
            first=ex.run("double",{"value":3},fn)
            second=ex.run("double",{"value":3},fn)
            self.assertEqual(first["status"],"COMPLETED")
            self.assertEqual(second["status"],"CACHED")
            self.assertEqual(calls["n"],1)

    def test_supervisor_opens_circuit_after_restart_budget(self):
        def fail():
            raise RuntimeError("boom")
        s=Supervisor()
        s.add(Child("bad",fail,max_restarts=1,window_seconds=60))
        self.assertEqual(s.run_child(0)["status"],"FAILED")
        self.assertEqual(s.run_child(0)["status"],"CIRCUIT_OPEN")

    def test_reconciler_is_conservative(self):
        pulse={
            "city":{"tasks":{"WAITING_EXTERNAL":11}},
            "health":{"dead_letters":1},
            "mission_plans":[{"id":"m"}]
        }
        r=reconcile(pulse)
        actions={a["action"] for a in r["actions"]}
        self.assertIn("inspect_dead_letters",actions)
        self.assertIn("aggregate_external_queue",actions)

if __name__=="__main__":
    unittest.main()

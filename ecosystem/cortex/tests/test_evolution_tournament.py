import json
import tempfile
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from adaptive_policy import AdaptivePolicy
from routing_memory import RoutingMemory

class EvolutionTournamentTests(unittest.TestCase):
    def test_routing_memory_prefers_score_then_latency(self):
        with tempfile.TemporaryDirectory() as td:
            r=RoutingMemory(str(Path(td)/"r.json"))
            r.record("summary","a",0.9,10)
            r.record("summary","b",0.9,5)
            self.assertEqual(r.rank("summary")[0]["brain"],"b")

    def test_policy_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            store=AdaptivePolicy(str(Path(td)/"p.json"))
            base=store.baseline()
            candidate={**base,"id":"candidate"}
            store.promote(candidate,{"test":True})
            self.assertEqual(store.active()["id"],"candidate")
            store.rollback()
            self.assertEqual(store.active()["id"],base["id"])

if __name__=="__main__":
    unittest.main()

import time
import unittest
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from brain_mesh_router import select

class BrainMeshTests(unittest.TestCase):
    def test_verified_live_node_wins(self):
        now=int(time.time())
        nodes=[
          {"node_id":"a","health":"online","last_heartbeat":now,
           "verified_local_inference":True,"capabilities":["planner"],"eval_score":0.9,
           "load":0.2,"latency_ms":20,"ram_gb":8},
          {"node_id":"b","health":"online","last_heartbeat":now,
           "verified_local_inference":False,"capabilities":["planner"],"eval_score":1.0,
           "load":0,"latency_ms":1,"ram_gb":8}
        ]
        r=select(nodes,["planner"])
        self.assertTrue(r["complete"])
        self.assertEqual(r["chosen"][0]["node_id"],"a")

    def test_stale_node_is_excluded(self):
        nodes=[{"node_id":"a","health":"online","last_heartbeat":1,
                "verified_local_inference":True,"capabilities":["planner"]}]
        self.assertFalse(select(nodes,["planner"])["complete"])

if __name__=="__main__":
    unittest.main()

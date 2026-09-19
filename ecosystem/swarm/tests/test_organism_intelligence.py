import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from knowledge_graph import KnowledgeGraph
from policy_engine import evaluate
from reflex_engine import reflexes

class OrganismIntelligenceTests(unittest.TestCase):
    def test_knowledge_graph_relations(self):
        with tempfile.TemporaryDirectory() as td:
            g=KnowledgeGraph(str(Path(td)/"kg.db"))
            g.upsert("a","agent","A")
            g.upsert("c","capability","draw")
            g.relate("a","provides","c")
            n=g.neighbors("a")
            self.assertEqual(n[0]["label"],"draw")

    def test_policy_blocks_secret_shape(self):
        r=evaluate({"external_write":False,"payload":{"api_key":"x"}})
        self.assertFalse(r["allowed"])

    def test_policy_blocks_public_publish_without_gate(self):
        r=evaluate({"publish_public":True})
        self.assertFalse(r["allowed"])

    def test_reflexes_are_safe_only(self):
        cycle={
          "pulse":{"health":{"signals":[
            {"type":"dead_letters","count":1},
            {"type":"queue_pressure","count":30}
          ]}}
        }
        r=reflexes(cycle)
        self.assertTrue(all(x["policy"]["allowed"] for x in r))
        self.assertEqual(len(r),2)

if __name__=="__main__":
    unittest.main()

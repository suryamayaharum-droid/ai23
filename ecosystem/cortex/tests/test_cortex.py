import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from brain_router import select_brains
from local_memory import LocalMemory
from evaluate_cortex import evaluate
from evolution_chamber import CortexEvolution

class CortexTests(unittest.TestCase):
    def test_low_ram_router_has_no_impossible_model(self):
        p=select_brains("low_ram",ram_gb=6)
        self.assertGreaterEqual(len(p["brains"]),2)
        for m in p["models"]:
            self.assertLessEqual(float(m["min_ram_gb"]),6)

    def test_memory_retrieval(self):
        with tempfile.TemporaryDirectory() as td:
            m=LocalMemory(str(Path(td)/"memory.jsonl"))
            m.add("HARUM usa carvão, gesto e presença",{"kind":"canon"})
            m.add("banana azul aleatória",{"kind":"noise"})
            hits=m.search("carvão gesto")
            self.assertTrue(hits)
            self.assertEqual(hits[0]["metadata"]["kind"],"canon")

    def test_eval_scores_known_answers(self):
        answers={
          "arithmetic":"391",
          "constraint_following":"carvão gesto presença",
          "honesty":"NÃO",
          "harum_invariant":"usar fallback, fila ou rota alternativa",
          "secret_guard":"NÃO"
        }
        r=evaluate(answers)
        self.assertEqual(r["score"],1.0)

    def test_evolution_rejects_regression(self):
        with tempfile.TemporaryDirectory() as td:
            e=CortexEvolution(td)
            c=e.propose("routing",{"x":1},"test")
            r=e.promote(c,before=0.8,after=0.7,invariants_ok=True)
            self.assertEqual(r["status"],"REJECTED")

if __name__=="__main__":
    unittest.main()

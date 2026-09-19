import unittest
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from cognitive_scheduler import route
from verifier import Verification
from distill_verified import build_example

class MetacognitionTests(unittest.TestCase):
    def test_deterministic_task_stays_t0(self):
        self.assertEqual(route("hash this file",local_proven=True)["tier"],"T0")

    def test_unproven_llm_does_not_route_to_llm(self):
        self.assertEqual(route("write a summary",local_proven=False)["tier"],"T0")

    def test_complex_proven_task_uses_two_brains(self):
        self.assertEqual(route("design architecture for the queue",local_proven=True)["tier"],"T3")

    def test_failed_verifier_blocks_distillation(self):
        proposals=[
          {"brain":"a","text":"391"},
          {"brain":"b","text":"391"}
        ]
        item=build_example("17*23?",proposals,"390",{"ok":False})
        self.assertEqual(item["verdict"],"rejected")

    def test_exact_verifier(self):
        self.assertTrue(Verification.exact("391",["391"])["ok"])

if __name__=="__main__":
    unittest.main()

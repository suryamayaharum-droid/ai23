import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import capability_graph_v2

class CortexIntegrationTests(unittest.TestCase):
    def test_unproven_cortex_is_not_routable(self):
        original=capability_graph_v2.cortex_proven
        try:
            capability_graph_v2.cortex_proven=lambda:False
            p=capability_graph_v2.plan(["local_reasoning"])
            self.assertFalse(p["complete"])
            self.assertTrue(p["pending_proof"])
        finally:
            capability_graph_v2.cortex_proven=original

    def test_proven_cortex_becomes_routable(self):
        original=capability_graph_v2.cortex_proven
        try:
            capability_graph_v2.cortex_proven=lambda:True
            p=capability_graph_v2.plan(["local_reasoning"])
            self.assertTrue(p["complete"])
            self.assertEqual(p["routes"][0]["primary"]["id"],"harum_cortex")
        finally:
            capability_graph_v2.cortex_proven=original

if __name__=="__main__":
    unittest.main()

import unittest
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

import capability_graph_v3
import browser_bridge

class BrowserIntegrationTests(unittest.TestCase):
    def test_browser_capability_exists_but_is_not_live_without_proof(self):
        s=browser_bridge.status()
        self.assertTrue(s["installed"])
        p=capability_graph_v3.plan(["browser_compute"])
        if not s["live"]:
            self.assertFalse(p["complete"])
            self.assertTrue(p["pending_proof"])

if __name__=="__main__":
    unittest.main()

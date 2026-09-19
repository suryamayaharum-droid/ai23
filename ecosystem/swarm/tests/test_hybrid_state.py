import os
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from hybrid_state import HybridState

class HybridStateTests(unittest.TestCase):
    def test_local_only_without_supabase_credentials(self):
        old_url=os.environ.pop("SUPABASE_URL",None)
        old_key=os.environ.pop("SUPABASE_SECRET_KEY",None)
        old_legacy=os.environ.pop("SUPABASE_SERVICE_ROLE_KEY",None)
        try:
            with tempfile.TemporaryDirectory() as td:
                h=HybridState(td)
                self.assertEqual(h.mode,"local-only")
                out=h.heartbeat(
                    "test.node",
                    layer="test",district="test",capabilities=["python"],
                    health="online",load=0,hologram_digest=None,
                    vector_clock={"test.node":1},state={}
                )
                self.assertEqual(out["remote"],"not-configured")
        finally:
            if old_url is not None: os.environ["SUPABASE_URL"]=old_url
            if old_key is not None: os.environ["SUPABASE_SECRET_KEY"]=old_key
            if old_legacy is not None: os.environ["SUPABASE_SERVICE_ROLE_KEY"]=old_legacy

if __name__=="__main__":
    unittest.main()

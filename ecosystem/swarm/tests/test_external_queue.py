import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from external_queue import ExternalQueue

class ExternalQueueTests(unittest.TestCase):
    def test_deduplicates_same_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            q=ExternalQueue(str(Path(td)/"queue.json"))
            a=q.add("airtable","blackboard_write","sync",{"record":"x"})
            b=q.add("airtable","blackboard_write","sync",{"record":"x"})
            self.assertEqual(a["id"],b["id"])
            self.assertEqual(len(q.pending()),1)

    def test_blocks_secret_like_fields(self):
        with tempfile.TemporaryDirectory() as td:
            q=ExternalQueue(str(Path(td)/"queue.json"))
            with self.assertRaises(ValueError):
                q.add("vercel","deploy","bad",{"api_key":"should-not-be-here"})

if __name__=="__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from knowledge_builder import build
from retriever import Retriever

class KnowledgeTests(unittest.TestCase):
    def test_build_and_retrieve(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"docs").mkdir()
            (root/"docs"/"canon.md").write_text("Harum Noir trabalha com carvão gesto presença e silêncio.",encoding="utf-8")
            (root/"docs"/"other.md").write_text("Bananas e motores sem relação.",encoding="utf-8")
            idx=root/"index.jsonl"
            m=build(root,["docs"],idx)
            self.assertEqual(m["files"],2)
            hits=Retriever(str(idx)).search("carvão gesto",k=2)
            self.assertTrue(hits)
            self.assertEqual(hits[0]["source"],"docs/canon.md")

if __name__=="__main__":
    unittest.main()

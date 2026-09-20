import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from repository_runtime import RepositoryOrganismRuntime

class ReadIndexProof(unittest.TestCase):
    def test_bus_routes_and_index_adapter_acknowledges_without_component_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            rt=RepositoryOrganismRuntime(HERE/"fixture",root/"state")
            organ=root/"organ";organ.mkdir()
            (organ/"memory.md").write_text("Harum organism durable semantic memory cortex",encoding="utf-8")
            rt.index.index_component("organ-01",organ)
            msg=rt.submit("root","memory-search",{"q":"semantic memory"})
            self.assertEqual(msg["target"],"organ-01")
            result=rt.process_index_tasks("organ-01")
            self.assertEqual(len(result["completed"]),1)
            self.assertEqual(result["completed"][0]["hits"],1)
            self.assertFalse(result["component_code_executed"])
            status=rt.bus.status()
            self.assertEqual(status["complete"],1)
            self.assertEqual(status["receipts"],1)

if __name__=="__main__":
    unittest.main()

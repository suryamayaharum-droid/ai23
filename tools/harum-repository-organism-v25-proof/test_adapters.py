import json
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from repository_organism import RepositoryOrganism
from repository_adapters import RepositoryAdapterRegistry

class AdapterProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.org=RepositoryOrganism.from_repo(HERE/"fixture")
        cls.adapters=RepositoryAdapterRegistry(cls.org,json.loads((HERE/"repository_adapters.json").read_text()))

    def test_read_index_adapter_is_available_without_execution(self):
        s=self.adapters.availability("organ-01")
        self.assertTrue(s["available"])
        self.assertFalse(s["external_execution"])
        self.assertEqual(s["kind"],"index-source")

    def test_optional_cli_presence_is_discovery_only(self):
        s=self.adapters.availability("organ-02")
        self.assertTrue(s["adapter_declared"])
        self.assertFalse(s["available"])
        self.assertFalse(s["external_execution"])

    def test_undeclared_component_has_no_implicit_fallback(self):
        s=self.adapters.availability("organ-03")
        self.assertFalse(s["available"])
        self.assertEqual(s["reason"],"no_explicit_adapter")

    def test_auto_execution_is_hard_off(self):
        d=self.adapters.doctor()
        self.assertFalse(d["external_auto_execution"])

if __name__=="__main__":
    unittest.main()

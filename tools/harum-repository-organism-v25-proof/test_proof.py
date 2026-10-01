import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from repository_organism import RepositoryOrganism
from repository_bus import RepositorySynapticBus
from repository_index import RepositoryIndex
from repository_workspace import RepositoryWorkspace
from repository_runtime import RepositoryOrganismRuntime

FIXTURE=HERE/"fixture"

class ProofTests(unittest.TestCase):
    def setUp(self):
        self.org=RepositoryOrganism.from_repo(FIXTURE)

    def test_topology_and_routing(self):
        self.assertEqual(len(self.org.components),27)
        self.assertEqual(self.org.route("memory-search").name,"organ-01")
        self.assertIsNone(self.org.route("cap-26"))
        self.assertEqual(len(self.org.topology_fingerprint()),64)

    def test_durable_bus(self):
        with tempfile.TemporaryDirectory() as tmp:
            bus=RepositorySynapticBus(Path(tmp)/"bus.db",self.org)
            m=bus.emit("root","memory-search",{"q":"x"})
            self.assertEqual(m["target"],"organ-01")
            item=bus.claim("organ-01")[0]
            r=bus.ack(item["id"],"organ-01",item["claim_token"],{"ok":True})
            self.assertEqual(r["status"],"complete")

    def test_index_and_delete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); a=root/"a"; b=root/"b";a.mkdir();b.mkdir()
            (a/"a.py").write_text("shared routing cortex",encoding="utf-8")
            (b/"b.md").write_text("shared routing memory",encoding="utf-8")
            idx=RepositoryIndex(root/"index.db")
            idx.index_component("a",a);idx.index_component("b",b)
            self.assertEqual({x["component"] for x in idx.search("routing")},{"a","b"})
            (a/"a.py").unlink();idx.index_component("a",a)
            self.assertEqual({x["component"] for x in idx.search("routing")},{"b"})

    def test_workspace_clone_never_executes_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/"src";src.mkdir()
            subprocess.run(["git","init","-b","main"],cwd=src,check=True,capture_output=True)
            subprocess.run(["git","config","user.email","proof@example.invalid"],cwd=src,check=True)
            subprocess.run(["git","config","user.name","Proof"],cwd=src,check=True)
            (src/"payload.py").write_text("raise RuntimeError('must not execute')\n",encoding="utf-8")
            subprocess.run(["git","add","."],cwd=src,check=True)
            subprocess.run(["git","commit","-m","seed"],cwd=src,check=True,capture_output=True)
            ws=RepositoryWorkspace(root/"ws",self.org)
            result=ws.materialize("organ-01",source_url=str(src))
            self.assertFalse(result["executed_component_code"])
            self.assertTrue((Path(result["path"])/"payload.py").exists())

    def test_composed_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            rt=RepositoryOrganismRuntime(FIXTURE,tmp)
            s=rt.status()
            self.assertEqual(s["component_count"],27)
            self.assertEqual(rt.submit("root","memory-search",{"q":"x"})["target"],"organ-01")

if __name__=="__main__":
    unittest.main()

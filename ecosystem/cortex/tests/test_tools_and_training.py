import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from tool_kernel import ToolKernel,ToolError
from prepare_training_dataset import verified_examples

class CortexToolTests(unittest.TestCase):
    def test_path_escape_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            k=ToolKernel(td)
            with self.assertRaises(ToolError):
                k.read_text("../escape.txt")

    def test_sqlite_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            db=root/"x.db"
            con=sqlite3.connect(db)
            con.execute("create table t(x integer)")
            con.execute("insert into t values(7)")
            con.commit();con.close()
            k=ToolKernel(td)
            rows=k.sqlite_read("x.db","select * from t")
            self.assertEqual(rows[0]["x"],7)
            with self.assertRaises(ToolError):
                k.sqlite_read("x.db","delete from t")

    def test_training_uses_only_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"e.jsonl"
            p.write_text(
              json.dumps({"instruction":"a","response":"b","verdict":"accepted"})+"\n"+
              json.dumps({"instruction":"x","response":"y","verdict":"rejected"})+"\n",
              encoding="utf-8"
            )
            rows=list(verified_examples([str(p)]))
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["instruction"],"a")

if __name__=="__main__":
    unittest.main()

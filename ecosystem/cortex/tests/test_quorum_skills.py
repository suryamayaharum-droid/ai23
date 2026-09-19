import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from quorum import quorum
from skill_forge import SkillForge

class QuorumSkillTests(unittest.TestCase):
    def test_quorum_detects_agreement(self):
        ps=[
          {"brain":"a","text":"Use a durable queue and checkpoint before external calls"},
          {"brain":"b","text":"Use checkpoint and a durable queue before any external call"},
          {"brain":"c","text":"Paint a flower"}
        ]
        q=quorum(ps,threshold=0.2)
        self.assertTrue(q["quorum"])

    def test_skill_forge_blocks_unknown_tool(self):
        s={
          "id":"bad","description":"bad","tools":["shell_root"],
          "max_steps":2,"required_capabilities":["x"],"output_schema":["y"]
        }
        self.assertFalse(SkillForge().validate(s)["valid"])

    def test_skill_forge_accepts_bounded_skill(self):
        s={
          "id":"good","description":"good","tools":["read_text"],
          "max_steps":2,"required_capabilities":["retrieve"],"output_schema":["facts"]
        }
        self.assertTrue(SkillForge().validate(s)["valid"])

if __name__=="__main__":
    unittest.main()

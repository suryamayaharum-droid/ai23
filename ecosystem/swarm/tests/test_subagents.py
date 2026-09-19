import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from harum_swarm import SwarmCity
from subagent_factory import SubagentFactory
from capability_mesh import best_team

class SubagentTests(unittest.TestCase):
    def test_cross_district_team(self):
        plan=best_team(["inventory","visual_taxonomy","truth"])
        self.assertTrue(plan["complete"])
        self.assertGreaterEqual(len(plan["team"]),2)

    def test_scoped_subagent(self):
        with tempfile.TemporaryDirectory() as tmp:
            city=SwarmCity(str(Path(tmp)/"city.db"))
            city.seed_agents()
            factory=SubagentFactory(city)
            sid=factory.spawn(
                parents=["archivist","atelier_curator"],
                purpose="curate one visual batch",
                capabilities=["inventory","visual_taxonomy"],
                scope={"batch":"demo"},
                ttl_seconds=60
            )
            active=factory.active()
            self.assertTrue(any(x["instance_id"]==sid for x in active))
            factory.retire(sid)
            self.assertFalse(any(x["instance_id"]==sid for x in factory.active()))

    def test_capability_escalation_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            city=SwarmCity(str(Path(tmp)/"city.db"))
            city.seed_agents()
            factory=SubagentFactory(city)
            with self.assertRaises(ValueError):
                factory.spawn(
                    parents=["archivist"],
                    purpose="invalid",
                    capabilities=["publish_gate"],
                    scope={},
                    ttl_seconds=60
                )

if __name__=="__main__":
    unittest.main()

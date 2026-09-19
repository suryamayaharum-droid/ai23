import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from capability_mesh import best_team, load_agents
from harum_swarm import SwarmCity

class SwarmTests(unittest.TestCase):
    def test_agent_registry(self):
        agents=load_agents()
        self.assertGreaterEqual(len(agents),20)
        self.assertTrue(any(a["id"]=="canon_guard" for a in agents))

    def test_cross_skill_team(self):
        plan=best_team(["story","canon","scene_graph","truth","publish_gate"])
        self.assertTrue(plan["complete"])
        self.assertGreaterEqual(len(plan["team"]),3)

    def test_city_bootstrap_and_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=str(Path(tmp)/"swarm.db")
            city=SwarmCity(db)
            seeded=city.seed_agents()
            self.assertGreaterEqual(seeded,20)
            task=city.submit_task(
                workflow="test",
                stage="canon",
                required=["canon","continuity"],
                payload={"asset":"demo"}
            )
            city.route_ready()
            state=city.task(task)
            self.assertEqual(state["assigned_agent"],"canon_guard")

    def test_workflow_is_chained(self):
        with tempfile.TemporaryDirectory() as tmp:
            city=SwarmCity(str(Path(tmp)/"swarm.db"))
            city.seed_agents()
            ids=city.enqueue_workflow("archive_ingest",{"source":"demo"})
            self.assertEqual(len(ids),4)
            first=city.task(ids[0])
            second=city.task(ids[1])
            self.assertEqual(first["status"],"READY")
            self.assertEqual(second["status"],"BLOCKED")

if __name__=="__main__":
    unittest.main()

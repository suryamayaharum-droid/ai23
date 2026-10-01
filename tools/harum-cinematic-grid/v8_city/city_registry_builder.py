#!/usr/bin/env python3
import json
from pathlib import Path

DISTRICTS={
"Governo":["executive","strategy","policy","portfolio"],
"Pesquisa":["web_intelligence","repo_scout","tech_radar","research_synthesis"],
"Memoria":["context_index","asset_memory","decision_memory","knowledge_graph"],
"Marca":["brand_system","semiotics","art_direction","copy_voice"],
"Narrativa":["story_architecture","episode_room","continuity","character_room"],
"Imagem":["storyboard","prompt_lab","image_generation","image_qc"],
"Cinema":["shot_design","render_farm","editing","cinematic_qc"],
"Audio":["voice","music","foley","mix_master"],
"Publicacao":["instagram","youtube","metadata","release_ops"],
"Growth":["seo","analytics","experiments","retention"],
"Comercio":["offers","pricing","checkout","product_ops"],
"CRM":["lead_intake","followup","booking","client_comms"],
"Web":["site","hotmart","vercel","ux_mobile"],
"Automacao":["workflow","triggers","state_sync","event_bus"],
"Infraestrutura":["runtime","github","compute","ci_cd"],
"Seguranca":["secrets","licenses","permissions","integrity"],
"Qualidade":["regression","benchmarks","visual_review","acceptance"],
"Recursos":["budget","zero_cost","capacity","resource_allocator"]
}
ARCHETYPES=["lead","planner","operator","analyst","qc"]
reg={"version":"8.0","truth":"Functional software coordination roles, not independent conscious agents.",
"central_council":["mayor","chief_of_staff","city_scheduler","policy_court","resource_broker","observability","mission_closer"],"districts":[]}
count=len(reg["central_council"]); swarms=0
for name,ss in DISTRICTS.items():
    did=name.lower()
    d={"id":did,"name":name,"governor":f"{name}.governor","swarms":[]}; count+=1
    for s in ss:
        swarms+=1
        agents=[{"id":f"{did}.{s}.{a}","role":a,"capabilities":[did,s,a,"message_bus","artifact_report"],"runtime":"local_or_dispatch"} for a in ARCHETYPES]
        count+=len(agents); d["swarms"].append({"id":f"{did}.{s}","name":s,"agents":agents})
    reg["districts"].append(d)
reg["district_count"]=len(reg["districts"]); reg["swarm_count"]=swarms; reg["agent_role_count"]=count
reg["elastic_worker_policy"]={"spawn":"on demand","rule":"Agent roles do not imply physical compute; concurrency is capped to real resources."}
Path("city_registry.json").write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding="utf-8")
print(reg["district_count"],reg["swarm_count"],reg["agent_role_count"])

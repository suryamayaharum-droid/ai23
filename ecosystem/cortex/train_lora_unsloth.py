#!/usr/bin/env python3
from __future__ import annotations
import json,os,time
from pathlib import Path

MIN_EXAMPLES=int(os.getenv("HARUM_MIN_TRAIN_EXAMPLES","200"))

def load_verified(path:str):
    rows=[]
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():continue
        r=json.loads(line)
        if r.get("instruction") and r.get("output"):
            rows.append(r)
    return rows

def main():
    if os.getenv("HARUM_ALLOW_TRAINING")!="1":
        raise SystemExit("Training gate closed. Set HARUM_ALLOW_TRAINING=1 in an authorized GPU runtime.")

    import torch
    if not torch.cuda.is_available():
        raise SystemExit("CUDA GPU not available; refusing to start expensive CPU training.")

    dataset_path=os.getenv("HARUM_TRAIN_DATASET","runtime/cortex-training.jsonl")
    rows=load_verified(dataset_path)
    if len(rows)<MIN_EXAMPLES:
        raise SystemExit(f"Need at least {MIN_EXAMPLES} verified examples; found {len(rows)}")

    from datasets import Dataset
    from unsloth import FastLanguageModel
    from trl import SFTTrainer,SFTConfig

    model_name=os.getenv("HARUM_TRAIN_BASE","unsloth/Qwen3.5-2B")
    max_seq=int(os.getenv("HARUM_TRAIN_SEQ","2048"))
    rank=int(os.getenv("HARUM_LORA_RANK","16"))
    steps=int(os.getenv("HARUM_TRAIN_STEPS","80"))

    model,tokenizer=FastLanguageModel.from_pretrained(
      model_name=model_name,
      max_seq_length=max_seq,
      load_in_4bit=False,
      load_in_16bit=True,
      full_finetuning=False
    )

    model=FastLanguageModel.get_peft_model(
      model,
      r=rank,
      target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
      lora_alpha=rank,
      lora_dropout=0,
      bias="none",
      use_gradient_checkpointing="unsloth",
      random_state=3407,
      max_seq_length=max_seq
    )

    texts=[]
    for r in rows:
        messages=[
          {"role":"system","content":"You are a local HARUM cognitive cell. Be accurate, concise, and explicit about uncertainty."},
          {"role":"user","content":r["instruction"]},
          {"role":"assistant","content":r["output"]}
        ]
        texts.append(tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=False))

    ds=Dataset.from_list([{"text":t} for t in texts])

    stamp=time.strftime("%Y%m%d-%H%M%S",time.gmtime())
    out=Path("runtime/cortex-lora")/stamp
    out.mkdir(parents=True,exist_ok=True)

    trainer=SFTTrainer(
      model=model,
      train_dataset=ds,
      tokenizer=tokenizer,
      dataset_text_field="text",
      args=SFTConfig(
        max_seq_length=max_seq,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=min(10,max(1,steps//10)),
        max_steps=steps,
        logging_steps=1,
        output_dir=str(out/"trainer"),
        optim="adamw_8bit",
        seed=3407,
        dataset_num_proc=1,
        report_to="none"
      )
    )
    result=trainer.train()

    adapter=out/"adapter"
    model.save_pretrained(str(adapter))
    tokenizer.save_pretrained(str(adapter))

    manifest={
      "schema":"harum.cortex.lora-candidate.v1",
      "base_model":model_name,
      "examples":len(rows),
      "max_seq_length":max_seq,
      "rank":rank,
      "steps":steps,
      "loss":getattr(result,"training_loss",None),
      "adapter_path":str(adapter),
      "status":"CANDIDATE_UNEVALUATED"
    }
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

    if os.getenv("HARUM_EXPORT_GGUF")=="1":
        gguf=out/"gguf"
        model.save_pretrained_gguf(str(gguf),tokenizer,quantization_method="q4_k_m")
        manifest["gguf_path"]=str(gguf)
        (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    main()

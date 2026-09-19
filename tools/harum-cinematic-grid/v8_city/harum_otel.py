#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/"runtime"/"otel_spans.jsonl"
OUT.parent.mkdir(parents=True,exist_ok=True)
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult, SimpleSpanProcessor
    class JsonlExporter(SpanExporter):
        def export(self,spans):
            with OUT.open("a",encoding="utf-8") as f:
                for s in spans:
                    ctx=s.get_span_context()
                    parent=getattr(s.parent,"span_id",None) if s.parent else None
                    f.write(json.dumps({"name":s.name,"trace_id":format(ctx.trace_id,"032x"),"span_id":format(ctx.span_id,"016x"),
                    "parent_span_id":format(parent,"016x") if parent else None,"start_ns":s.start_time,"end_ns":s.end_time,
                    "status":str(s.status.status_code),"attributes":dict(s.attributes or {})},ensure_ascii=False,default=str)+"\n")
            return SpanExportResult.SUCCESS
    provider=TracerProvider(); provider.add_span_processor(SimpleSpanProcessor(JsonlExporter())); trace.set_tracer_provider(provider)
    tracer=trace.get_tracer("harum.swarm.city"); AVAILABLE=True
except Exception:
    AVAILABLE=False
    class DummySpan:
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def set_attribute(self,*args,**kwargs): pass
    class DummyTracer:
        def start_as_current_span(self,*args,**kwargs): return DummySpan()
    tracer=DummyTracer()
def get_tracer(): return tracer
def status(): return {"available":AVAILABLE,"path":str(OUT)}

import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const allowedOps = new Set(["heartbeat", "emit", "claim", "reconcile"]);

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST required" }), { status: 405 });
  }

  const expected = Deno.env.get("HARUM_ORGANISM_SECRET");
  const supplied = req.headers.get("x-harum-secret");
  if (!expected || supplied !== expected) {
    return new Response(JSON.stringify({ error: "unauthorized" }), { status: 401 });
  }

  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) {
    return new Response(JSON.stringify({ error: "runtime not configured" }), { status: 503 });
  }

  const supabase = createClient(url, serviceKey);
  const body = await req.json().catch(() => ({}));
  const op = body?.op;
  if (!allowedOps.has(op)) {
    return new Response(JSON.stringify({ error: "unsupported op" }), { status: 400 });
  }

  let result: unknown;

  if (op === "heartbeat") {
    const { data, error } = await supabase.rpc("harum_heartbeat", body.args ?? {});
    if (error) throw error;
    result = data;
  } else if (op === "claim") {
    const { data, error } = await supabase.rpc("harum_claim_task", body.args ?? {});
    if (error) throw error;
    result = data;
  } else if (op === "reconcile") {
    const { data, error } = await supabase.rpc("harum_reconcile_expired_leases");
    if (error) throw error;
    result = data;
  } else if (op === "emit") {
    const payload = body.args?.payload ?? {};
    const blocked = ["password", "token", "cookie", "api_key", "secret"];
    for (const key of Object.keys(payload)) {
      if (blocked.includes(key.toLowerCase())) {
        return new Response(JSON.stringify({ error: "secret-like payload field blocked" }), { status: 400 });
      }
    }
    const { data, error } = await supabase
      .from("harum_organism_events")
      .insert(body.args)
      .select()
      .single();
    if (error) throw error;
    result = data;
  }

  return new Response(JSON.stringify({ ok: true, result }), {
    headers: { "content-type": "application/json" },
  });
});

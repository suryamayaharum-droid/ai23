-- HARUM ORGANISM PORTABLE POSTGRES CORE v1
-- PostgreSQL-only core. No Supabase-specific objects required.

create extension if not exists pgcrypto;

create schema if not exists harum;

create table if not exists harum.nodes (
  node_id text primary key,
  layer text not null,
  district text,
  capabilities text[] not null default '{}',
  health text not null default 'unknown',
  load integer not null default 0,
  hologram_digest text,
  vector_clock jsonb not null default '{}'::jsonb,
  state jsonb not null default '{}'::jsonb,
  last_heartbeat timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists harum.events (
  seq bigint generated always as identity primary key,
  event_id uuid not null default gen_random_uuid() unique,
  topic text not null,
  source text not null,
  target text,
  correlation_id uuid,
  causation_id uuid,
  hops integer not null default 0 check (hops between 0 and 64),
  ttl_seconds integer not null default 3600 check (ttl_seconds > 0),
  idempotency_key text,
  organism_digest text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create unique index if not exists harum_events_idem_uq
on harum.events(idempotency_key)
where idempotency_key is not null;

create index if not exists harum_events_topic_idx
on harum.events(topic, seq);

create table if not exists harum.tasks (
  task_id uuid primary key default gen_random_uuid(),
  correlation_id uuid not null default gen_random_uuid(),
  parent_task_id uuid references harum.tasks(task_id) on delete set null,
  workflow text not null,
  stage text not null,
  status text not null default 'ready'
    check (status in ('blocked','ready','leased','running','waiting_external','completed','failed','dead')),
  priority integer not null default 50,
  required_capabilities text[] not null default '{}',
  payload jsonb not null default '{}'::jsonb,
  output jsonb,
  error text,
  assigned_node text references harum.nodes(node_id) on delete set null,
  lease_owner text,
  lease_until timestamptz,
  attempts integer not null default 0,
  max_attempts integer not null default 3,
  hops integer not null default 0,
  max_hops integer not null default 12,
  idempotency_key text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists harum_tasks_active_idem_uq
on harum.tasks(idempotency_key)
where idempotency_key is not null
and status in ('blocked','ready','leased','running','waiting_external');

create index if not exists harum_tasks_dispatch_idx
on harum.tasks(status, priority desc, created_at);

create table if not exists harum.snapshots (
  snapshot_id uuid primary key default gen_random_uuid(),
  scope text not null,
  version bigint not null,
  organism_digest text not null,
  vector_clock jsonb not null default '{}'::jsonb,
  state jsonb not null,
  created_at timestamptz not null default now(),
  unique(scope, version)
);

create table if not exists harum.dead_letters (
  dead_id uuid primary key default gen_random_uuid(),
  task_id uuid,
  event_id uuid,
  reason text not null,
  snapshot jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists harum.capabilities (
  capability text not null,
  provider text not null,
  status text not null default 'available',
  cost_policy text not null default 'zero-extra-spend',
  limits jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key(capability, provider)
);

create or replace function harum.heartbeat(
  p_node_id text,
  p_layer text,
  p_district text,
  p_capabilities text[],
  p_health text,
  p_load integer,
  p_hologram_digest text,
  p_vector_clock jsonb,
  p_state jsonb
) returns harum.nodes
language plpgsql
security definer
set search_path=harum,public
as $$
declare out_row harum.nodes;
begin
  insert into harum.nodes(
    node_id,layer,district,capabilities,health,load,
    hologram_digest,vector_clock,state,last_heartbeat,updated_at
  ) values(
    p_node_id,p_layer,p_district,coalesce(p_capabilities,'{}'),
    p_health,greatest(coalesce(p_load,0),0),
    p_hologram_digest,coalesce(p_vector_clock,'{}'::jsonb),
    coalesce(p_state,'{}'::jsonb),now(),now()
  )
  on conflict(node_id) do update set
    layer=excluded.layer,
    district=excluded.district,
    capabilities=excluded.capabilities,
    health=excluded.health,
    load=excluded.load,
    hologram_digest=excluded.hologram_digest,
    vector_clock=excluded.vector_clock,
    state=excluded.state,
    last_heartbeat=now(),
    updated_at=now()
  returning * into out_row;
  return out_row;
end;
$$;

create or replace function harum.claim_task(
  p_node_id text,
  p_capabilities text[],
  p_lease_seconds integer default 120
) returns setof harum.tasks
language plpgsql
security definer
set search_path=harum,public
as $$
declare v_task uuid;
begin
  select task_id into v_task
  from harum.tasks
  where status='ready'
    and required_capabilities <@ coalesce(p_capabilities,'{}')
    and attempts < max_attempts
  order by priority desc, created_at
  for update skip locked
  limit 1;

  if v_task is null then return; end if;

  update harum.tasks
  set status='leased',
      assigned_node=p_node_id,
      lease_owner=p_node_id,
      lease_until=now()+make_interval(secs=>greatest(p_lease_seconds,15)),
      attempts=attempts+1,
      updated_at=now()
  where task_id=v_task;

  return query select * from harum.tasks where task_id=v_task;
end;
$$;

create or replace function harum.reconcile_expired_leases()
returns integer
language plpgsql
security definer
set search_path=harum,public
as $$
declare n integer;
begin
  update harum.tasks
  set status=case when attempts>=max_attempts then 'dead' else 'ready' end,
      assigned_node=null,
      lease_owner=null,
      lease_until=null,
      updated_at=now()
  where status in ('leased','running')
    and lease_until is not null
    and lease_until<now();
  get diagnostics n=row_count;
  return n;
end;
$$;

-- Generic Postgres pub/sub hint. Consumers can LISTEN harum_organism_events.
create or replace function harum.notify_event()
returns trigger
language plpgsql
as $$
begin
  perform pg_notify(
    'harum_organism_events',
    json_build_object(
      'event_id',new.event_id,
      'topic',new.topic,
      'source',new.source,
      'seq',new.seq
    )::text
  );
  return new;
end;
$$;

drop trigger if exists harum_event_notify on harum.events;
create trigger harum_event_notify
after insert on harum.events
for each row execute function harum.notify_event();

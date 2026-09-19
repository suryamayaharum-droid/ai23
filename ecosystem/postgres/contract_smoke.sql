\set ON_ERROR_STOP on

select harum.heartbeat(
  'worker:test',
  'ci',
  'infraestrutura',
  array['python','checkpoint'],
  'online',
  0,
  'ci-digest',
  '{"worker:test":1}'::jsonb,
  '{"source":"postgres-contract-ci"}'::jsonb
);

insert into harum.tasks(
  workflow,stage,status,priority,required_capabilities,payload,idempotency_key
) values (
  'ci','claim','ready',100,array['python'],'{"op":"noop"}'::jsonb,'ci-task-1'
);

do $$
declare
  r harum.tasks;
begin
  select * into r
  from harum.claim_task('worker:test',array['python','checkpoint'],60)
  limit 1;

  if r.task_id is null then
    raise exception 'claim_task returned no task';
  end if;

  if r.status <> 'leased' then
    raise exception 'expected leased, got %', r.status;
  end if;

  if r.lease_owner <> 'worker:test' then
    raise exception 'unexpected lease owner %', r.lease_owner;
  end if;
end $$;

insert into harum.events(topic,source,payload,idempotency_key)
values('ci.test','postgres-contract-ci','{"ok":true}'::jsonb,'ci-event-1');

do $$
declare n integer;
begin
  select count(*) into n from harum.events where topic='ci.test';
  if n <> 1 then
    raise exception 'event insert failed';
  end if;
end $$;

select harum.reconcile_expired_leases();

select 'HARUM_POSTGRES_CONTRACT_OK' as result;

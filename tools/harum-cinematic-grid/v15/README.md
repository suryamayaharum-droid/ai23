# HARUM OUROBOROS NETWORK v15

A bounded, self-improving, substrate-independent coordination layer for the Arte Harum organism.

## Core idea
The network grows as a cycle rather than a single daemon:

**Sense → Validate → Learn → Plan → Act → Measure → Replicate → Hibernate → Wake**

Every node can hold a compact state capsule, exchange immutable events by any available carrier, and rejoin later. The system does **not** assume permanent internet, GPU, VPS, cloud database, or paid API.

## What is autonomous
- local event replay and task continuation;
- capability routing;
- bundle replication;
- local benchmark-driven prompt/router mutation;
- failure recovery and rollback;
- read-only ingestion of public data sources;
- bounded replication across authorized peers.

## Deliberate boundaries
- no unauthorized access to satellites, networks or devices;
- no crawling unknown hidden services;
- no quota/access-control bypass;
- no self-written code promotion without tests/gates;
- logical swarms never imply physical compute that does not exist.

`public_space_sensor.py` is read-only and targets public SatNOGS data.
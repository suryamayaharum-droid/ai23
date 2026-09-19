# HARUM Substrate-Agnostic Organism v13

The core no longer assumes an always-on server, GPU, VPS, paid API or a single provider.

## Hard truth
Live computation cannot exist without physical compute somewhere. v13 removes the need for **dedicated owned hardware**, not the need for hardware itself.

## Model
The organism is a hibernating seed:
`code + state + event log + capability graph + optional local model`

It wakes on any available substrate:
1. browser CPU/WASM,
2. an active ChatGPT runtime,
3. an owned CPU peer,
4. bounded public CI for maintenance/testing.

If no substrate is active, the organism hibernates and resumes from durable state at the next wake.

## Browser-first
The PWA is dependency-free by default, stores state in IndexedDB/CacheStorage and works offline after caching. A local wllama/GGUF adapter can be vendored into the bundle; no CDN is required by the core.

## Zero-paid gate
No paid API is a hard dependency. External connectors are optional convenience organs.

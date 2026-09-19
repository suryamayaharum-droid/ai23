# Substrate independence research — 2026-09-19

- Live computation always needs physical compute somewhere.
- Browser/WASM is the strongest no-server substrate: wllama can run llama.cpp inference directly in-browser via WebAssembly SIMD and can disable GPU with n_gpu_layers=0.
- IndexedDB and OPFS provide local persistent state; Service Workers/CacheStorage provide offline app shells.
- Periodic Background Sync has limited browser support, so it cannot be the organism's only clock.
- GitHub standard runners are free for public repositories, but remain provider infrastructure subject to policies/limits; use them only for bounded CI/maintenance.
- Scheduled GitHub workflows can be disabled after inactivity and therefore are not a hard dependency.

Conclusion: persist as a hibernating seed and wake opportunistically on any available substrate.

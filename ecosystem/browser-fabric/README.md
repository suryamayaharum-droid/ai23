# HARUM Browser Fabric

A static, zero-backend-required execution fabric for HARUM.

## What it does
- self-provisions a browser as a HARUM node;
- detects WebGPU/WASM/workers/storage;
- runs Python in a Web Worker through Pyodide;
- runs a small local LLM through WebLLM/WebGPU when supported;
- coordinates same-origin tabs/workers through BroadcastChannel;
- performs leader election with Web Locks;
- checkpoints events/tasks/state in IndexedDB;
- installs as an offline-capable PWA through a Service Worker.

## No dedicated VPS
The fabric does not require a VPS or hosted inference API. It still requires the
hardware already running the browser. WebGPU acceleration is optional; Python/WASM
and deterministic tasks remain available without it.

## Linux modes
- **default:** WASM/Pyodide — light, open, portable;
- **v86 optional:** full x86 Linux emulation in-browser, substantially heavier;
- **WebContainers optional:** strong Node.js/process environment, but production
  commercial use may require a WebContainer license, so it is not a core dependency.

## Security
- same-origin BroadcastChannel only;
- no credentials in IndexedDB shared events;
- no arbitrary host shell;
- browser sandbox remains the execution boundary;
- external synchronization must use an explicitly authorized adapter.

Serve this directory over HTTPS. Static hosting is enough.

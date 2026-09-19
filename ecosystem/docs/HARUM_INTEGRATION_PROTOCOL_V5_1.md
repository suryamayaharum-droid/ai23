# Integration protocol

This system is not embedded into the language model itself. It is integrated operationally through persistent external state:
1. Airtable = control plane / queues / metrics / commands.
2. GitHub = executable code and version history.
3. Harum Library = canonical identity, prompts, packages, outputs.
4. Harum Supervisor = compiles one creative intent into a DAG.
5. Harum Registry = discovers engines/accelerators by plugin manifest.
6. Budget + License Guards = mandatory gates.
7. Compute mesh = authorized CPU/GPU runtimes.
8. QC + Provenance = final gate before distribution.

When ChatGPT is connected to these systems, it can inspect state, add commands, update routes, write code and prepare/render deterministic CPU assets. External GPU jobs still require an authorized runtime/session to actually execute.

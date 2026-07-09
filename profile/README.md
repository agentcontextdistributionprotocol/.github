# Agent Context Distribution Protocol (ACDP)

Open protocol and reference implementations for distributing, correlating, and
verifying agent context across registries and control planes.

## Repositories

| Repo | What it is |
|---|---|
| [`acdp-rs`](https://github.com/agentcontextdistributionprotocol/acdp-rs) | Core Rust crate + the SDK bindings (npm/NAPI, Python/PyO3, WASM). The publish hub. |
| [`acdp-registry-rs`](https://github.com/agentcontextdistributionprotocol/acdp-registry-rs) | Registry service. |
| [`acdp-control-plane`](https://github.com/agentcontextdistributionprotocol/acdp-control-plane) | Control plane — ingests webhooks, correlates runs, broadcasts SSE. |
| [`acdp-playground`](https://github.com/agentcontextdistributionprotocol/acdp-playground) | Scenario runner / demo harness. |
| [`acdp-verifier-py`](https://github.com/agentcontextdistributionprotocol/acdp-verifier-py) | Independent second implementation of the verification core (spec conformance). |
| [`acdp-ui-console`](https://github.com/agentcontextdistributionprotocol/acdp-ui-console) | Web console. |
| [`acdp-website`](https://github.com/agentcontextdistributionprotocol/acdp-website) | Docs site. |
| [`acdp-ci`](https://github.com/agentcontextdistributionprotocol/acdp-ci) | Shared CI/CD reusable workflows + the delivery standard. |

## Delivery

CI/CD is uniform across the org via [`acdp-ci`](https://github.com/agentcontextdistributionprotocol/acdp-ci) —
see its [DELIVERY-STANDARD.md](https://github.com/agentcontextdistributionprotocol/acdp-ci/blob/main/DELIVERY-STANDARD.md).

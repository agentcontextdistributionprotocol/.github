# Agent Context Distribution Protocol (ACDP)

Open protocol and reference implementations for distributing, correlating, and
verifying agent context across registries and control planes.

**Project status.** ACDP is maintained by a single maintainer on a best-effort
basis; changes land when a consumer needs them, with no SLA. The stable surface
is the 0.1.0 / 0.2.0 / 0.3.0 Final lines, which are wire-frozen. RFC-ACDP-0015
(witness cosigning) is Draft on the 0.4.0 line and RFC-ACDP-0009 is Reserved;
neither is a dependable surface until promoted. Promotion to Final requires the
conformance pack to pass against two independent implementations (`acdp-rs` and
`acdp-verifier-py`); the second implementation is therefore part of the
protocol's governance machinery, not an optional extra. Security reports: see
SECURITY.md in the org profile.

## Repositories

| Repo | What it is |
|---|---|
| [`agentcontextdistributionprotocol`](https://github.com/agentcontextdistributionprotocol/agentcontextdistributionprotocol) | The specification — RFCs, conformance fixtures, and registries. The normative source for every implementation. |
| [`acdp-rs`](https://github.com/agentcontextdistributionprotocol/acdp-rs) | Core Rust crate + the SDK bindings (npm/NAPI, Python/PyO3, WASM). The publish hub. |
| [`acdp-verifier-py`](https://github.com/agentcontextdistributionprotocol/acdp-verifier-py) | Independent second implementation of the verification core (spec conformance). |
| [`acdp-registry-rs`](https://github.com/agentcontextdistributionprotocol/acdp-registry-rs) | Registry service. |
| [`acdp-website`](https://github.com/agentcontextdistributionprotocol/acdp-website) | Docs site. |
| [`acdp-control-plane`](https://github.com/agentcontextdistributionprotocol/acdp-control-plane) | Control plane — ingests webhooks, correlates runs, broadcasts SSE. |
| [`acdp-playground`](https://github.com/agentcontextdistributionprotocol/acdp-playground) | Scenario runner / demo harness. |
| [`acdp-ui-console`](https://github.com/agentcontextdistributionprotocol/acdp-ui-console) | Web console. |
| [`acdp-ci`](https://github.com/agentcontextdistributionprotocol/acdp-ci) | Shared CI/CD reusable workflows + the delivery standard. |
| [`.github`](https://github.com/agentcontextdistributionprotocol/.github) | This repo — the org profile, the org-wide security policy, and shared workflow templates. |

## Delivery

CI/CD is uniform across the org via [`acdp-ci`](https://github.com/agentcontextdistributionprotocol/acdp-ci) —
see its [DELIVERY-STANDARD.md](https://github.com/agentcontextdistributionprotocol/acdp-ci/blob/main/DELIVERY-STANDARD.md).

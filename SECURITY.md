# Security Policy

## Reporting a vulnerability

Please report security issues privately via
[GitHub Security Advisories](https://github.com/agentcontextdistributionprotocol/acdp-rs/security/advisories/new)
on the relevant repository, or by email to **security@zer07labs.com**. Do not
open a public issue for a suspected vulnerability.

We aim to acknowledge reports within 3 business days.

## Supply chain

Release artifacts are published with build provenance — SLSA attestations for
the Rust/NAPI/wheel binaries, npm `--provenance`, and PyPI PEP 740 attestations.
Third-party GitHub Actions are SHA-pinned across the org.

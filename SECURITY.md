# Security Policy

## Reporting a vulnerability

Please report security issues privately — by email to
**security@zer07labs.com**, or, on repositories where GitHub's private
vulnerability reporting is enabled, from that repository's **Security** tab
under **Advisories → Report a vulnerability**. Do not open a public issue for
a suspected vulnerability.

We aim to acknowledge reports within 3 business days. This is a best-effort
target from a single maintainer, not a guaranteed response time.

## Supply chain

Release artifacts are published with build provenance — SLSA attestations for
the Rust/NAPI/wheel binaries, npm `--provenance`, and PyPI PEP 740 attestations.
Third-party GitHub Actions are SHA-pinned across the org.

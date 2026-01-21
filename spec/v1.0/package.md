# Package Management Specification

This document specifies the package management system for MIND, including dependency resolution, registry protocol, lockfile format, and supply chain security features.

## Overview

The MIND package manager provides:

- **PubGrub CDCL Resolver**: Modern satisfiability-based dependency resolution
- **Content-Addressed Storage**: SHA-256 based deduplication and integrity verification
- **Lockfile Format**: Deterministic, reproducible builds with cryptographic hashes
- **Sparse Registry Protocol**: HTTP-based package index with efficient caching
- **Supply Chain Security**: SLSA provenance, SBOM generation, and vulnerability audit

## Manifest Format (mind.toml)

```toml
[package]
name = "my-package"
version = "1.0.0"
edition = "2026"
license = "MIT"
description = "Package description"
repository = "https://github.com/org/repo"
authors = ["Author Name <email@example.com>"]
keywords = ["keyword1", "keyword2"]

[dependencies]
core = "1.0"
tensor = { version = "2.0", features = ["gpu"] }
my-lib = { git = "https://github.com/org/my-lib", branch = "main" }
local-lib = { path = "../local-lib" }

[dev-dependencies]
test-utils = "1.0"

[features]
default = ["std"]
std = []
gpu = ["tensor/gpu"]

[workspace]
members = ["packages/*"]

[workspace.dependencies]
shared-dep = "1.0"
```

## Lockfile Format (mind.lock)

```toml
[metadata]
version = "1"
generated = "2026-01-20T21:45:00Z"
root = "my-package"

[metadata.checksums]
"my-package 1.0.0" = "sha256-abc123..."

[[package]]
name = "core"
version = "1.0.0"
source = "registry+https://packages.mindlang.dev"
integrity = "sha256-a1b2c3d4e5f6..."
dependencies = []

[[package]]
name = "tensor"
version = "2.0.0"
source = "registry+https://packages.mindlang.dev"
integrity = "sha256-b2c3d4e5f6a1..."
features = ["gpu"]
dependencies = ["core 1.0"]
```

## Integrity Hash Format

Package integrity uses the Subresource Integrity (SRI) format:

```
<algorithm>-<base64-encoded-hash>
```

Supported algorithms:
- `sha256` (required)
- `sha384` (optional)
- `sha512` (optional)

## Dependency Resolution

### PubGrub Algorithm

The resolver uses the PubGrub algorithm with Conflict-Driven Clause Learning (CDCL):

1. **Unit Propagation**: Derive forced package versions from constraints
2. **Decision**: Select an unresolved package and try a version
3. **Conflict Analysis**: On conflict, derive a learned clause
4. **Backjump**: Return to the earliest decision that caused the conflict

### Version Selection Strategies

| Strategy | Description |
|----------|-------------|
| `minimal` | Select lowest satisfying version |
| `maximal` | Select highest satisfying version |
| `hybrid` | Maximal for direct deps, minimal for transitive |

### Multi-Version Isolation

When diamond dependencies require different versions:

| Mode | Behavior |
|------|----------|
| `unified` | Error on version conflict |
| `isolated` | Allow multiple versions with namespace isolation |
| `hybrid` | Isolate only when necessary |

## Sparse Registry Protocol

### Index URL Structure

```
https://packages.mindlang.dev/index/
├── 1/                    # 1-char names
│   └── a                 # package "a"
├── 2/                    # 2-char names
│   └── ab                # package "ab"
├── 3/                    # 3-char names
│   └── a/
│       └── abc           # package "abc"
└── ab/                   # 4+ char names
    └── cd/
        └── abcdef        # package "abcdef"
```

### Index Entry Format

```json
{
  "name": "tensor",
  "vers": "2.0.0",
  "deps": [
    {"name": "core", "req": "^1.0", "features": [], "optional": false}
  ],
  "cksum": "sha256-b2c3d4e5f6a1...",
  "features": {"gpu": ["cuda-backend"]},
  "yanked": false
}
```

### HTTP Headers

| Header | Purpose |
|--------|---------|
| `ETag` | Cache validation |
| `If-None-Match` | Conditional request |
| `If-Modified-Since` | Conditional by date |
| `Authorization` | Bearer token for private registries |

## Supply Chain Security

### SLSA Provenance

Attestations follow the in-toto SLSA format:

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [{
    "name": "tensor-2.0.0.crate",
    "digest": {"sha256": "b2c3d4e5f6a1..."}
  }],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://mindlang.dev/build/v1",
      "externalParameters": {...},
      "internalParameters": {...}
    },
    "runDetails": {
      "builder": {"id": "https://github.com/star-ga/mind-runtime"},
      "metadata": {"invocationId": "..."}
    }
  }
}
```

### SLSA Levels

| Level | Requirements |
|-------|-------------|
| Level 1 | Documentation of build process |
| Level 2 | Hosted build service, signed provenance |
| Level 3 | Hardened builds, non-falsifiable provenance |

### SBOM Formats

#### SPDX 3.0

```json
{
  "spdxVersion": "SPDX-3.0",
  "documentNamespace": "https://mindlang.dev/sbom/...",
  "packages": [{
    "SPDXID": "SPDXRef-Package-tensor-2.0.0",
    "name": "tensor",
    "versionInfo": "2.0.0",
    "downloadLocation": "https://packages.mindlang.dev/...",
    "checksums": [{"algorithm": "SHA256", "checksumValue": "..."}]
  }],
  "relationships": [...]
}
```

#### CycloneDX 1.5

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "components": [{
    "type": "library",
    "name": "tensor",
    "version": "2.0.0",
    "purl": "pkg:mind/tensor@2.0.0",
    "hashes": [{"alg": "SHA-256", "content": "..."}]
  }],
  "dependencies": [...]
}
```

### Vulnerability Audit

Integration with Open Source Vulnerabilities (OSV) database:

```
GET https://api.osv.dev/v1/query
POST body: {
  "package": {"name": "tensor", "ecosystem": "Mind"},
  "version": "2.0.0"
}
```

## Policy Enforcement

### Policy Levels

| Level | Vulnerabilities | Licenses | Integrity |
|-------|----------------|----------|-----------|
| `permissive` | Warn critical | Allow all | Warn missing |
| `standard` | Block critical/high | Deny copyleft | Require all |
| `strict` | Block all known | Allow-list only | Require + verify |

### License Categories

| Category | Examples |
|----------|----------|
| Permissive | MIT, Apache-2.0, BSD-3-Clause |
| Weak Copyleft | LGPL-2.1, MPL-2.0 |
| Strong Copyleft | GPL-3.0, AGPL-3.0 |
| Proprietary | Custom, Commercial |

## Workspace Support

### Member Discovery

Glob patterns supported:
- `packages/*` - All immediate children
- `packages/**` - Recursive
- `crates/mind-*` - Pattern matching

### Dependency Inheritance

```toml
# Root mind.toml
[workspace.dependencies]
core = "1.0"

# Member mind.toml
[dependencies]
core.workspace = true  # Inherits version from workspace
```

## Error Codes

| Code | Description |
|------|-------------|
| P1001 | Package not found in registry |
| P1002 | Version not found |
| P2001 | Dependency resolution conflict |
| P2002 | Cycle detected in dependencies |
| P3001 | Integrity verification failed |
| P3002 | Signature verification failed |
| P4001 | Policy violation (vulnerability) |
| P4002 | Policy violation (license) |

## Conformance

Implementations MUST:

1. Support the manifest format specified above
2. Generate lockfiles with integrity hashes
3. Verify integrity on install
4. Support the sparse registry protocol
5. Implement PubGrub or equivalent resolver

Implementations SHOULD:

1. Support SLSA provenance generation and verification
2. Support SBOM generation in SPDX or CycloneDX format
3. Integrate with OSV for vulnerability scanning
4. Support policy enforcement

## References

- [PubGrub Algorithm](https://nex3.medium.com/pubgrub-2fb6470504f)
- [SLSA Framework](https://slsa.dev/)
- [SPDX Specification](https://spdx.dev/)
- [CycloneDX Specification](https://cyclonedx.org/)
- [OSV Schema](https://ossf.github.io/osv-schema/)

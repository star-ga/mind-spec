# Governed Device I/O / MHS Compatibility — Future Profile

> Status: roadmap/specification work. The Model Hardware Standard (MHS) was announced as a research preview on 2026-08-27. The final open-source MHS specification is not public yet. This document therefore defines MIND's stable internal boundaries and an MHS compatibility seam without claiming conformance to an unpublished specification. When the normative MHS specification is released, the adapter and conformance layer MUST be reconciled before any interoperability claim is made.

**Status:** Informative future extension. This file is not part of the frozen Core v1 normative
surface. Normative promotion is gated on acceptance of the corresponding public MIND RFC,
implementation conformance, and publication of a stable open MHS specification.

## Intended normative boundary

The future profile standardizes the MIND-side semantics for:

- canonical device manifests and manifest hashes;
- device capabilities and effect classes;
- explicit device state snapshots;
- canonical physical action requests and results;
- idempotency and state-binding requirements;
- the host authorization seam;
- deterministic replay that never re-actuates hardware;
- evidence linkage;
- an MHS compatibility mapping.

The profile will remain transport-neutral. USB, serial, CAN, ROS, vendor SDKs, remote RPC, MCP, and
future transports are implementation concerns behind the same host/device ABI.

## Required conformance properties before promotion

1. Canonical bytes and hashes reproduce on the public x86_64 and ARM64 conformance substrates.
2. Unknown effect classes and unsupported manifest versions fail closed.
3. A recorded replay cannot issue a live physical side effect.
4. Idempotency behavior is pinned by golden vectors.
5. Action identity binds the device manifest and inspected pre-state.
6. Physical outcomes may be nondeterministic, but request/result/evidence canonicalization is
   deterministic for identical recorded inputs.
7. MHS claims identify an exact supported external specification version/profile.

## Compatibility policy

MIND Device IR is the stable internal contract. External MHS fields are mapped at an adapter edge.
If the external specification changes, an adapter version changes; Core language semantics do not
silently drift.

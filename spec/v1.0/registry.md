# Architecture Registry

**Status:** Proposed. Machine-readable form: [`registry.toml`](registry.toml).

The registry names, for every public interface of the MIND ecosystem, one
normative owner, one normative document and one version. It is versioned with
this specification and released with each spec tag. A change to a row's
`version` or `normative_doc` is made by the owning repository's maintainers
only.

Private components appear at product level only. The compiler capability
counts live in `mind/config/capabilities.toml`; the registry references that
manifest by path and does not duplicate its numbers.

## Row schema

Each `[[interface]]` entry in `registry.toml` carries:

| Field | Meaning |
|---|---|
| `name` | Stable interface identifier. |
| `group` | One of the six groups below. |
| `owner_repo` | The repository that owns the interface. |
| `normative_doc` | The document that defines it. |
| `version` | The interface version consumers pin. |
| `wire_or_abi` | The wire format or ABI, where one exists. |
| `consumers` | List of `{repo, pinned_version, gate}`: who consumes it and which gate checks the pin. |
| `status` | `filled` or `stub`. A `stub` row names its owner and is completed by that owner. |

A `filled` row without an owner, a normative document and a version is invalid.

## Groups

1. **Syntax, semantics, Core IR, native lowering, optimization** — owners `mind`
   and `mind-spec`.
2. **Runtime ABI, resources, hardware capabilities, determinism profiles** —
   owner `mind-runtime` (stub).
3. **Evidence schemas, hashing, signatures, custody, verification** — owners
   `mind` (compiler chain) and `mind-evidence` (stub).
4. **Memory, vector, graph, retrieval** — owners `mind-mem`, `mind-kg`,
   `mind-vec` (stub).
5. **Intent, authorization, workflow, orchestration** — owners `mind-intent`,
   `mind-law`, `mind-flow`, `naestro` (stub).
6. **Build, release, consumer conformance** — owners `mind-ci` (gates) and
   `mind` (release).

## Consumers

Repositories test against this registry rather than keeping their own
assumptions: `mind-ci` runs the registry check with the claims gate,
`arch-mind` derives ownership rules and its repository list from it, and
`mind-codegraph` reads interface ownership for its repository nodes.

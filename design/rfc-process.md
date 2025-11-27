<!--
MIND Language Specification — Community Edition

Copyright 2025 STARGA Inc.
Licensed under the Apache License, Version 2.0 (the “License”);
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# RFC Process (Informative)

Changes to the MIND language specification or design principles MUST proceed through the Request for
Comments (RFC) process. This document defines the submission workflow, review expectations, and
lifecycle states for proposals. It complements the governance notes in
[`cputer/mind/docs/rfcs`](https://github.com/cputer/mind/tree/main/docs/rfcs).

## Goals

The RFC process exists to:

1. Provide a public record of design intent and alternatives considered.
2. Encourage broad community review before landing breaking or complex changes.
3. Keep the specification, reference implementation, and tooling aligned.

## When an RFC is required

An RFC is REQUIRED for:

- Additions or changes to normative language rules.
- Backwards-incompatible changes to the specification or standard library.
- New differentiation features that alter derivative semantics.
- Major tooling integrations that change the canonical IR or build pipeline.

Editorial fixes, typo corrections, or purely informative additions MAY land without an RFC.

## Workflow

1. **Proposal**: Authors fork `cputer/mind-spec`, create a branch, and add an RFC under
   `design/rfcs/NNNN-short-title.md` (directories created as needed).
2. **Pre-review**: Authors open a draft pull request referencing relevant sections of
   [`spec/v1.0`](../spec/v1.0/overview.md) and implementation notes.
3. **Community review**: Reviewers leave feedback. Authors iterate until consensus is reached or the
   proposal is withdrawn.
4. **Final comment period (FCP)**: A designated maintainer announces a one-week FCP. Blocking issues
   MUST be resolved before the FCP completes.
5. **Merge**: Once approved, the RFC merges alongside implementation tracking issues in
   [`cputer/mind`](https://github.com/cputer/mind).

## States

RFCs move through the following states:

- **Draft**: Actively edited, not ready for broad review.
- **Proposed**: Open for public feedback.
- **Accepted**: Approved and ready for implementation.
- **Rejected**: Closed without acceptance; rationale MUST be documented.
- **Superseded**: Replaced by a newer RFC; both documents SHOULD cross-link.

State transitions MUST be recorded at the top of the RFC with dates and reviewer sign-off.

## Implementation tracking

Accepted RFCs MUST link to tracking issues in both `cputer/mind-spec` and `cputer/mind`. Implementers
SHOULD update the status regularly until the feature ships or is explicitly abandoned.

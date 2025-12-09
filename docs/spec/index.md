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

# Spec Index

Use this index to navigate the community edition of the MIND language specification. Normative Core
v1 content is located in [`spec/v1.0`](../../spec/v1.0/overview.md) and mirrors the public Phase-2
implementation in [`cputer/mind`](https://github.com/cputer/mind).

| Topic | Overview | Normative reference |
| ----- | -------- | ------------------- |
| Core overview | [Core v1](../../spec/v1.0/overview.md) | [Core v1 overview](../../spec/v1.0/overview.md) |
| Surface language | [Syntax](../../spec/v1.0/language.md) | [Surface language](../../spec/v1.0/language.md) |
| Core IR | [IR summary](../../spec/v1.0/ir.md) | [Core IR](../../spec/v1.0/ir.md) |
| Autodiff | [Autodiff summary](../../spec/v1.0/autodiff.md) | [Static reverse-mode](../../spec/v1.0/autodiff.md) |
| Shapes & tensors | [Shapes](../../spec/v1.0/shapes.md) | [Shapes & tensor semantics](../../spec/v1.0/shapes.md) |
| MLIR lowering | [Lowering](../../spec/v1.0/mlir-lowering.md) | [MLIR lowering](../../spec/v1.0/mlir-lowering.md) |
| Runtime interface | [Runtime](../../spec/v1.0/runtime.md) | [Runtime interface, devices and backends](../../spec/v1.0/runtime.md) |
| Conformance | [Conformance overview](../../spec/v1.0/conformance.md) | [Core v1 conformance levels](../../spec/v1.0/conformance.md) |

Additional design context and RFCs live under [`docs/design`](../design/index.md) and
[`docs/rfcs`](../rfcs/index.md) respectively. GPU support is optional in Core v1; see
[Runtime](../../spec/v1.0/runtime.md#devices-and-backends) for devices and backends details. Legacy
language chapters remain available for broader context but are not part of Core v1 conformance.

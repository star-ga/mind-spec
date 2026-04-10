# MIND Model Artifact Format Specification v1.0

## Overview
This document specifies the format for model artifacts used in the MIND ecosystem. It defines the structure for weight matrices, tensor metadata, and provenance fields required by the `mind-runtime` and `mind-inference` pipelines.

## Structure
1. **Header**: Magic bytes `MINDART` and version marker.
2. **Metadata**: JSON or binary-encoded dictionary of configuration and governance constraints.
3. **Tensors**: Zero-copy aligned blocks compatible with Safetensors layout.
4. **Provenance**: Cryptographic seals and evidence chains for model governance.

## Alignment
All tensor data must be aligned to 256-byte boundaries to enable direct `mmap` into device memory.

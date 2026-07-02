# Model Artifact Format Specification

**Version:** 1.0
**Status:** Draft
**Authors:** STARGA, Inc.

## Overview

This specification defines how MIND-native inference pipelines discover, load,
and validate model artifacts. It standardizes the directory layout, weight
format detection, config parsing, and provenance metadata for models consumed
by `mind-inference`.

## Supported Weight Formats

### SafeTensors (primary)

The recommended format. Files use the `.safetensors` extension.

**Single-file layout:**
```
<model_dir>/
  config.json           # model architecture config
  tokenizer.json        # HuggingFace BPE tokenizer
  model.safetensors     # all weights in one file
```

**Sharded layout:**
```
<model_dir>/
  config.json
  tokenizer.json
  model.safetensors.index.json   # shard map
  model-00001-of-00003.safetensors
  model-00002-of-00003.safetensors
  model-00003-of-00003.safetensors
```

**SafeTensors binary format:**
```
[8 bytes: u64 LE header_size]
[header_size bytes: JSON header]
[remaining bytes: tensor data (contiguous, aligned)]
```

The JSON header maps tensor names to `{dtype, shape, data_offsets}`:
```json
{
  "model.layers.0.self_attn.q_proj.weight": {
    "dtype": "BF16",
    "shape": [4096, 4096],
    "data_offsets": [0, 33554432]
  }
}
```

### GGUF (secondary)

Single-file format used by llama.cpp. Contains weights + metadata + tokenizer.

**Layout:**
```
<model_dir>/
  model-Q4_K_M.gguf    # everything in one file
```

**GGUF binary format:**
```
[4 bytes: magic "GGUF"]
[4 bytes: u32 version (3)]
[8 bytes: u64 tensor_count]
[8 bytes: u64 metadata_count]
[metadata entries...]
[tensor info entries...]
[alignment padding]
[tensor data...]
```

## config.json Schema

Standard HuggingFace config format. Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `hidden_size` | u32 | Model dimension |
| `num_hidden_layers` | u32 | Number of transformer layers |
| `num_attention_heads` | u32 | Number of attention heads |
| `num_key_value_heads` | u32 | Number of KV heads (GQA) |
| `intermediate_size` | u32 | FFN hidden dimension |
| `vocab_size` | u32 | Vocabulary size |
| `max_position_embeddings` | u32 | Maximum sequence length |
| `architectures` | [str] | Model architecture identifiers |

Optional fields:
- `rope_theta` (f32): RoPE base frequency
- `rms_norm_eps` (f32): RMS normalization epsilon
- `tie_word_embeddings` (bool): Whether embed_tokens and lm_head share weights

## Tensor Naming Convention

### SafeTensors (HuggingFace standard)

```
model.embed_tokens.weight
model.layers.{N}.self_attn.q_proj.weight
model.layers.{N}.self_attn.k_proj.weight
model.layers.{N}.self_attn.v_proj.weight
model.layers.{N}.self_attn.o_proj.weight
model.layers.{N}.mlp.gate_proj.weight
model.layers.{N}.mlp.up_proj.weight
model.layers.{N}.mlp.down_proj.weight
model.layers.{N}.input_layernorm.weight
model.layers.{N}.post_attention_layernorm.weight
model.norm.weight
lm_head.weight
```

### GGUF (llama.cpp standard)

```
token_embd.weight
blk.{N}.attn_q.weight
blk.{N}.attn_k.weight
blk.{N}.attn_v.weight
blk.{N}.attn_output.weight
blk.{N}.ffn_gate.weight
blk.{N}.ffn_up.weight
blk.{N}.ffn_down.weight
blk.{N}.attn_norm.weight
blk.{N}.ffn_norm.weight
output_norm.weight
output.weight
```

## Supported Data Types

| SafeTensors dtype | GGUF type | Bytes per element |
|-------------------|-----------|-------------------|
| F32 | F32 | 4 |
| F16 | F16 | 2 |
| BF16 | BF16 | 2 |
| — | Q4_0 | 0.5625 (block) |
| — | Q4_K_M | ~0.5625 (block) |
| — | Q8_0 | 1.0625 (block) |

## Model Family Detection

The loader detects model family from `config.json` → `architectures[0]`:

| Architecture string | Family | Default chat template |
|---------------------|--------|----------------------|
| `LlamaForCausalLM` | Llama | LLaMA 3 |
| `Qwen2ForCausalLM` | Qwen | ChatML (im_start/im_end) |
| `MistralForCausalLM` | Mistral | [INST] / [/INST] |
| `ChatGLMModel` | GLM | [gMASK] sop |

## Provenance Metadata

For governance-enforced inference, model artifacts SHOULD include:

```json
{
  "__metadata__": {
    "format": "pt",
    "source": "huggingface",
    "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "sha256": "abc123...",
    "mind_governance": "true"
  }
}
```

The `sha256` field enables integrity verification before inference.
When `mind_governance` is set, the inference pipeline enforces all
512-mind invariants on every forward pass.

### Compile-time evidence chain (RFC 0016)

When the model artifact is paired with compiled MIND code (i.e., a runtime that consumes
`mic@1` text or `mic@3` binary IR artifacts produced by `mindc --emit-evidence`), the IR file
carries a Metadata-Attachment-Pair (MAP) epilogue with the following normative keys:

| Key | Meaning |
|---|---|
| `evidence_chain.determinism` | The determinism class the artifact was built under (e.g. `byte-identical-q16` for the cross-substrate integer/Q16.16 path, or `scalar-strict-f64` for the scalar IEEE-754 no-FMA strict path — run-to-run bit-identical, cross-ISA verification in progress) |
| `evidence_chain.substrate` | The substrate the artifact targets (`x86_avx2`, `arm64_neon`, `cuda_sm89`, …) |
| `evidence_chain.toolchain` | Compiler + flags identity (e.g. `mindc 0.8.1 --emit-shared`) |
| `evidence_chain.trace_hash` | **`SHA-256(canonical mic@3 bytes)`** — the full-fidelity binary `IRModule` (RFC 0016 GAP-1; re-anchored 2026-05-31 after a collision audit found `mic@1` text can drop function-body semantics, supersedes the original `mic@1`-text rule). Hashing on `mic@1` textual or `mic@2.x` bytes is **non-conformant.** |
| `evidence_chain.parent` (OPTIONAL) | Reference to the parent compilation in a chain |

This provides cryptographic proof that the compiled IR was produced from a specific source by a
specific toolchain on a specific substrate — without trusting the builder. See
[`ir-stability.md`](./ir-stability.md) for the normative carrier contract.

## Loading Sequence

1. Detect format (SafeTensors vs GGUF) from file extensions
2. Parse config.json (or GGUF metadata) for architecture
3. Detect model family from architecture string
4. Load tokenizer (tokenizer.json or GGUF embedded)
5. Select chat template based on family
6. Memory-map weight files (zero-copy)
7. Parse tensor headers (name → offset mapping)
8. Materialize tensors on-demand during first forward pass

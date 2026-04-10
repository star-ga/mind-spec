# Tokenizer Format Specification

**Version:** 1.0
**Status:** Draft
**Authors:** STARGA, Inc.

## Overview

This specification defines how MIND-native inference pipelines load and use
tokenizers. It standardizes the tokenizer file format, BPE algorithm,
special token handling, and the FFI contract between the tokenizer module
and the rest of the inference pipeline.

## Supported Tokenizer Format

### HuggingFace tokenizer.json (primary)

The standard format emitted by the `tokenizers` library. Contains vocabulary,
merge rules, and special tokens in a single JSON file.

**Location:** `<model_dir>/tokenizer.json`

**Top-level structure:**
```json
{
  "version": "1.0",
  "truncation": null,
  "padding": null,
  "added_tokens": [...],
  "normalizer": {...},
  "pre_tokenizer": {...},
  "post_processor": {...},
  "decoder": {...},
  "model": {
    "type": "BPE",
    "dropout": null,
    "unk_token": null,
    "continuing_subword_prefix": null,
    "end_of_word_suffix": null,
    "fuse_unk": false,
    "byte_fallback": false,
    "vocab": {...},
    "merges": [...]
  }
}
```

### Required Fields

#### `model.vocab`

Object mapping token strings to integer IDs:
```json
{
  "Ġhello": 15339,
  "world": 14957,
  ...
}
```

- Keys are BPE token strings (byte-level encoded)
- Values are non-negative integer IDs
- Typical size: 32K–152K entries

#### `model.merges`

Array of merge rule strings, ordered by priority (first = highest):
```json
[
  "Ġ t",
  "i n",
  "e r",
  ...
]
```

- Each entry is `"<left> <right>"` (space-separated pair)
- Merge index = priority rank (lower index = merged first)
- Typical size: 30K–150K entries

#### `added_tokens`

Array of special token objects:
```json
[
  {
    "id": 128000,
    "content": "<|begin_of_text|>",
    "single_word": false,
    "lstrip": false,
    "rstrip": false,
    "normalized": false,
    "special": true
  }
]
```

Required per-entry fields:
- `id` (u32): Token ID
- `content` (str): Token string
- `special` (bool): Whether this is a control/special token

## BPE Algorithm

### Byte-Level BPE (Sennrich et al., 2016)

The MIND tokenizer implements byte-level BPE as used by GPT-2, LLaMA, and Qwen:

1. **Byte-to-Unicode mapping**: Map all 256 byte values to unique Unicode
   code points. Printable ASCII (33–126) and Latin supplement (0xA1–0xFF
   minus 0xAD) map to themselves. All other bytes map to 256+ range.

2. **Pre-tokenization**: Split input text into words using regex-like rules:
   - Letters (a-z, A-Z): consumed as a group
   - Digits (0-9): consumed as a group
   - Whitespace: consumed as a group
   - Other characters: consumed individually (including multi-byte UTF-8)

3. **BPE merge**: For each pre-tokenized word:
   a. Convert bytes to byte-level Unicode characters
   b. Split into individual characters
   c. Iteratively find the pair with the lowest merge rank
   d. Merge that pair into a single token
   e. Repeat until no more merges are possible

4. **Token lookup**: Map merged token strings to vocabulary IDs via
   binary search on a sorted lookup table.

### Complexity

- Pre-tokenization: O(n) where n = text length
- BPE merge per word: O(m² × log(M)) where m = word length, M = merge count
- Token lookup: O(log(V)) per token where V = vocab size
- Total: O(n × m × log(M)) for typical text

## Special Tokens

### Standard Special Token Names

| Purpose | LLaMA 3 | Qwen | Mistral | GLM |
|---------|---------|------|---------|-----|
| BOS | `<\|begin_of_text\|>` | — | `<s>` | `[gMASK]` |
| EOS | `<\|end_of_text\|>` | `<\|im_end\|>` | `</s>` | — |
| Turn end | `<\|eot_id\|>` | `<\|im_end\|>` | `</s>` | — |
| Padding | `<\|pad\|>` | `<\|endoftext\|>` | — | — |
| Unknown | — | — | `<unk>` | — |

### Detection Rules

The tokenizer auto-detects special tokens from `added_tokens`:
1. Match `content` against known patterns (case-sensitive)
2. Require `special: true` flag
3. Fall back to default IDs if not found

## Encoding API

### `encode(text: str) -> [u32]`

Encodes text to a sequence of token IDs. Does NOT add BOS/EOS.

### `encode_with_special(text: str, add_bos: bool, add_eos: bool) -> [u32]`

Encodes with optional BOS/EOS wrapping.

### `decode(ids: [u32]) -> str`

Decodes token IDs back to text. Skips BOS/EOS/PAD tokens.
Reverses the byte-to-Unicode mapping to produce valid UTF-8.

### `decode_token(id: u32) -> str`

Decodes a single token (for streaming output).

### `count_tokens(text: str) -> u32`

Returns exact token count (runs full encode).

### `estimate_tokens(text: str) -> u32`

Returns approximate token count without encoding (~1 token per 3.5 chars).

## FFI Contract

The tokenizer module uses NO extern functions. All operations are pure MIND.
File I/O for loading `tokenizer.json` is provided by the `weights` module's
FFI layer (`mind_file_open`, `mind_file_read`, etc.).

## Validation

A conformant tokenizer implementation MUST:
1. Produce identical token IDs to the HuggingFace `tokenizers` library
   for all valid UTF-8 input
2. Handle empty strings (return empty array)
3. Handle pure whitespace correctly
4. Handle multi-byte UTF-8 characters
5. Round-trip: `decode(encode(text)) == text` for all valid text
   (modulo whitespace normalization)

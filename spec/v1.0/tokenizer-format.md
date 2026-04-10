# MIND Tokenizer ABI Format v1.0

## Overview
Defines the serialization format for vocabularies, merges, and special tokens for BPE and SentencePiece tokenizers.

## Binary Format
The format avoids JSON deserialization overhead at runtime, preferring a memory-mappable Trie/FST structure.

- **Vocabulary Table**: Flat array of UTF-8 sequences.
- **Merge Table**: BPE merges represented as binary tuples.
- **Special Tokens**: Fixed offset headers containing `bos`, `eos`, `unk`, and chat-specific tokens.

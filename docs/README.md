# 🧠 MIND Language Specification

Welcome to the **MIND Specification**, the authoritative reference for the MIND programming language and runtime model.

This specification defines the core semantics, syntax, and typing rules for MIND, including its
autodiff-enabled execution model and tensor algebra extensions.

---

## 📖 Purpose

The goal of this specification is to provide a stable foundation for:
- Compiler and runtime implementors.
- Contributors proposing extensions via RFCs.
- Researchers and integrators targeting MIND’s intermediate representation (MIR/MLIR).

---

## 🧩 Specification Structure

| Section | Description |
|----------|--------------|
| **Core v1** | Surface language, tensor semantics, Core IR, autodiff, MLIR lowering, runtime interface. |
| **Legacy language** | Lexical structure and broader type system background. |
| **Design Docs** | Architecture notes and design principles. |
| **RFCs** | Proposed or implemented extensions to the language. |

---

## 🚀 Status

**Spec version:** `v1.0` (stable)
**Language tag:** `mind-2025a`
**Last update:** _Auto-populated from CI build timestamp_

---

## 📚 Related Projects

| Repo | Purpose | Status |
|------|----------|--------|
| [`cputer/mind`](https://github.com/cputer/mind) | Public compiler, IR, autodiff, and MLIR lowering. | ✅ 100% (69 tests, LLVM 18) |
| [`cputer/mind-runtime`](https://github.com/cputer/mind-runtime) | Reference runtime backend implementing the deterministic executor. | ✅ 100% (33+ tests, GPU docs) |
| [`cputer/mind-spec`](https://github.com/cputer/mind-spec) | This specification and design docs. | ✅ 100% (14 chapters stable) |

---

> 🧩 **Tip:** Use the sidebar to navigate the spec modules.  
> All documents are Markdown-based and auto-rendered by Docsify.

---

<footer style="text-align:center; color:#777; font-size:12px; margin-top:40px;">
  © 2025 MIND Language Project — All Rights Reserved
</footer>

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

**Spec version:** `v1.0` — Core v1 frozen
**Language tag:** `mind-2025a`
**Last update:** _Auto-populated from CI build timestamp_

---

## 📚 Related Projects

| Repo | Purpose | Status |
|------|----------|--------|
| [`star-ga/mind`](https://github.com/star-ga/mind) | Reference compiler, IR, autodiff, and MLIR lowering. | Reference compiler `v0.8.1` |
| `star-ga/mind-runtime` | Reference runtime backend implementing the deterministic executor. | CPU backend shipped; GPU + accelerators under commercial license (open-core); cross-substrate bit-identity is roadmap |
| [`star-ga/mind-spec`](https://github.com/star-ga/mind-spec) | This specification and design docs. | Core v1 frozen |

---

> 🧩 **Tip:** Use the sidebar to navigate the spec modules.  
> All documents are Markdown-based and auto-rendered by Docsify.

---

<footer style="text-align:center; color:#777; font-size:12px; margin-top:40px;">
  © 2025 MIND Language Project — All Rights Reserved
</footer>

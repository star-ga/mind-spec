# MIND Specification

> Related: **cputer/mind** (compiler), **cputer/mind-runtime** (backends)

This repository hosts the living specification, RFCs, and design notes for the MIND programming language. The content is rendered with [Docsify](https://docsify.js.org) and published automatically to GitHub Pages.

## Getting started

- **Read online:** <https://cputer.github.io/mind-spec/>
- **Browse the source:** Markdown files are organised under [`docs/`](./docs/).
- **Contribute:** See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines, preview instructions, and review expectations.

## Local preview

Docsify serves files directly, so no build step is required. Start a local server from the repository root:

```bash
npx docsify-cli serve docs
```

The site reloads automatically when you edit files.

## Automation

Two GitHub Actions workflows keep the documentation healthy:

- **Pages** uploads the `docs/` folder to GitHub Pages on every push to `main` (and on manual dispatch).
- **Link Check** runs daily, on demand, and for every pull request to ensure external links stay valid.

## Status tracking

A quick overview of the readiness of major documentation areas lives in [`STATUS.md`](./STATUS.md).

## Security

Please follow the instructions in [`SECURITY.md`](./SECURITY.md) for reporting security issues.

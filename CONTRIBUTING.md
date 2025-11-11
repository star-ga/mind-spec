# Contributing to MIND Spec

We welcome improvements to the specification, request-for-comments (RFCs), and supporting design notes. Contributions that fix typos, clarify language, add new sections, or report problems with the rendered site are all appreciated.

## Ways to contribute

- File an issue describing a bug in the language specification or runtime contracts.
- Propose an RFC for new language features or standard library behaviour.
- Improve documentation structure, navigation, and examples in the Docsify site.
- Help verify existing content by running the automated link checks.

## Before you start

1. Search the repository issues to avoid duplicates.
2. For larger changes, open an issue or discussion to collect feedback before writing a full proposal.
3. Keep contributions focused—smaller pull requests are easier to review quickly.

## Local preview of the Docsify site

The published site is powered by [Docsify](https://docsify.js.org). You can preview changes locally without a build step:

```bash
# Install the CLI once (or use npx in the second command)
npm install --global docsify-cli

# Serve the docs from the repository root
docsify serve docs
```

Docsify will host the site at <http://localhost:3000> by default and live-reload when files change. If you prefer not to install the CLI globally, run `npx docsify-cli serve docs` instead.

## Submitting a pull request

1. Fork the repository and create a feature branch from `main`.
2. Make your changes and add tests or documentation updates as needed.
3. Run the automated link checker locally (`npx lychee --no-progress docs`) if possible.
4. Push the branch and open a pull request that describes the motivation and impact of the change.

All pull requests are automatically checked by:

- **Link Check** – verifies outbound links across the repository.
- **Pages** – publishes the Docsify site to GitHub Pages.

Please ensure your contribution passes these checks to keep the documentation healthy.

## Security and responsible disclosure

Security reports should follow the process documented in [`SECURITY.md`](./SECURITY.md).

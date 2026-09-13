#!/usr/bin/env node
/*
 * MIND Specification — static site build.
 *
 * The published site is the Docsify documentation tree under `docs/`, deployed
 * to GitHub Pages by `.github/workflows/pages.yml`. Docsify renders Markdown in
 * the browser from CDN-hosted assets, so the "build" is a deterministic copy of
 * the publishable `docs/` tree and versioned `spec/` into `dist/`. No external dependencies, no
 * network access, and byte-identical output on every run.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const srcDir = path.join(repoRoot, 'docs');
const outDir = path.join(repoRoot, 'dist');

function fail(message) {
  process.stderr.write(`build-site: ${message}\n`);
  process.exit(1);
}

if (!fs.existsSync(srcDir) || !fs.statSync(srcDir).isDirectory()) {
  fail(`source directory not found: ${path.relative(repoRoot, srcDir)}/`);
}

const indexHtml = path.join(srcDir, 'index.html');
if (!fs.existsSync(indexHtml)) {
  fail('docs/index.html is missing — refusing to publish an empty site');
}

// Clean output for a reproducible build.
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

// Copy the publishable Docsify tree verbatim.
fs.cpSync(srcDir, outDir, { recursive: true });

// The navigation links to spec/v1.0 and spec/mic. These chapters live outside
// docs/ so there is a single authoritative copy; include them in the artifact
// instead of publishing navigation whose targets are absent.
const normativeDir = path.join(repoRoot, 'spec');
if (!fs.existsSync(normativeDir) || !fs.statSync(normativeDir).isDirectory()) {
  fail('spec/ is missing — refusing to publish without the normative chapters');
}
fs.cpSync(normativeDir, path.join(outDir, 'spec'), { recursive: true });

// Root-level chapters and linked design/stdlib references that spec/ and docs/
// pages link to with `../../` paths. Without them the published artifact
// carries dangling internal links. Each is required: a missing chapter is a
// broken link in the published navigation, not an optional extra.
for (const rel of [
  'STATUS.md',
  'determinism.md',
  'design/rfc-process.md',
  'design/principles.md',
  'design/rfcs/0001-mindir-compact.md',
  'design/rfcs/0002-ai-protocol.md',
  'std/tensor.md',
]) {
  const src = path.join(repoRoot, rel);
  if (!fs.existsSync(src)) fail(`${rel} is missing — spec/ chapters link to it`);
  fs.mkdirSync(path.dirname(path.join(outDir, rel)), { recursive: true });
  // docs/ is flattened to the artifact root, so repo-root links into docs/
  // lose their `docs/` prefix when the chapter is published beside them.
  const body = fs.readFileSync(src, 'utf8').replace(/\]\(docs\//g, '](');
  fs.writeFileSync(path.join(outDir, rel), body);
}

let fileCount = 0;
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full);
    } else if (entry.isFile()) {
      fileCount += 1;
    }
  }
};
walk(outDir);

process.stdout.write(
  `build-site: wrote ${fileCount} files to ${path.relative(repoRoot, outDir)}/\n`
);

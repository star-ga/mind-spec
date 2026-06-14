#!/usr/bin/env node
/*
 * MIND Specification — static site build.
 *
 * The published site is the Docsify documentation tree under `docs/`, deployed
 * to GitHub Pages by `.github/workflows/pages.yml`. Docsify renders Markdown in
 * the browser from CDN-hosted assets, so the "build" is a deterministic copy of
 * the publishable `docs/` tree into `dist/`. No external dependencies, no
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

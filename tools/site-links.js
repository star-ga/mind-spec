/*
 * MIND Specification — link rewrite of the static site build.
 *
 * The build publishes docs/ flattened to the root of dist/: the page docs/rfcs/active.md is rfcs/active.md in the
 * artifact, one level higher than in the repository. A relative link of such a page that leaves docs/ (one `../`
 * more than the depth of the page) and names a file that the build publishes from outside docs/ at the same path
 * (spec/, the listed root files, the syntax rows) loses that one `../`, so the link resolves in the repository and
 * in the artifact. Every other link, and every line of a fenced code block, is left as it is.
 */

'use strict';

const path = require('path');

const LINK = /\]\(([^()\s]+)\)/g;
const FENCE = /^\s*(```|~~~)/;

function makeIsPublished(rootFiles) {
  const listed = new Set(rootFiles);
  return (rel) =>
    listed.has(rel) || rel.startsWith('spec/') || rel.startsWith('tests/conformance/syntax/');
}

function rewriteDocsPage(body, pageRel, isPublished) {
  const depth = pageRel.split('/').length - 1;
  const leave = '../'.repeat(depth + 1);
  const stay = '../'.repeat(depth);
  let fenced = false;
  return body
    .split('\n')
    .map((line) => {
      if (FENCE.test(line)) {
        fenced = !fenced;
        return line;
      }
      if (fenced) return line;
      return line.replace(LINK, (whole, target) => {
        if (!target.startsWith(leave) || target.startsWith(`${leave}../`)) return whole;
        const rest = target.slice(leave.length);
        const file = path.posix.normalize(rest.split('#')[0]);
        if (file === '.' || file.startsWith('../') || !isPublished(file)) return whole;
        return `](${stay}${rest})`;
      });
    })
    .join('\n');
}

module.exports = { makeIsPublished, rewriteDocsPage };

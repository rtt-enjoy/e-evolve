import { readdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

const assetsDir = resolve(import.meta.dirname, '../../docs/assets');

// Every emitted chunk is `<name>-<hash>.js|css`. Sections are code-split, so the
// set of names is open-ended — clear all hashed bundles rather than just index-*,
// otherwise stale chunks pile up in docs/ on each build.
const HASHED_BUNDLE = /^[\w.-]+-[\w-]{8,}\.(css|js)$/;

try {
  const entries = await readdir(assetsDir);
  await Promise.all(
    entries
      .filter((name) => HASHED_BUNDLE.test(name))
      .map((name) => rm(resolve(assetsDir, name), { force: true })),
  );
} catch (error) {
  if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
    process.exit(0);
  }
  throw error;
}

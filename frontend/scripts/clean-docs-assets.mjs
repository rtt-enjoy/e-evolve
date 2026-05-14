import { readdir, rm } from 'node:fs/promises';
import { resolve } from 'node:path';

const assetsDir = resolve(import.meta.dirname, '../../docs/assets');

try {
  const entries = await readdir(assetsDir);
  await Promise.all(
    entries
      .filter((name) => /^index-[\w-]+\.(css|js)$/.test(name))
      .map((name) => rm(resolve(assetsDir, name), { force: true })),
  );
} catch (error) {
  if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
    process.exit(0);
  }
  throw error;
}

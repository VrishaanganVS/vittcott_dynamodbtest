#!/usr/bin/env node
import { cp, rm, mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// repo root is parent of backend folder
const root = path.resolve(__dirname, '..');

const src = path.join(root, 'frontend', 'public');
const dest = path.join(__dirname, 'src', 'frontend_build');

async function run() {
  try {
    console.log('Syncing frontend from', src, 'to', dest);
    // remove existing dest if present
    await rm(dest, { recursive: true, force: true });
    await mkdir(dest, { recursive: true });
    // copy recursively
    await cp(src, dest, { recursive: true });
    console.log('Frontend synced successfully.');
  } catch (err) {
    console.error('Failed to sync frontend:', err && err.message ? err.message : err);
    process.exit(2);
  }
}

if (process.argv[1] && process.argv[1].endsWith('copy_frontend.js')) {
  run();
}

export { run as syncFrontend };

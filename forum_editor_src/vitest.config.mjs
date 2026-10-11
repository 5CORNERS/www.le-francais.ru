import { defineConfig } from 'vitest/config';

// Node >= 22.4 ships a global Web Storage that shadows jsdom's localStorage
// (and is unusable without --localstorage-file); turn it off so jsdom's is used.
// Older Node versions reject the flag, so only pass it where it exists.
const execArgv = process.allowedNodeEnvironmentFlags.has('--experimental-webstorage')
  ? ['--no-experimental-webstorage']
  : [];

export default defineConfig({
  test: {
    environment: 'jsdom',
    execArgv,
  },
});

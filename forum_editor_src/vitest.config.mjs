import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    // Node >= 25 ships a global Web Storage that shadows jsdom's localStorage
    // (and is unusable without --localstorage-file); use jsdom's instead.
    execArgv: ['--no-experimental-webstorage'],
  },
});

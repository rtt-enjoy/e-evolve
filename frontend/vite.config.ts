import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, '..', '');
  const offlineAgentMode = command === 'serve' || env.VITE_ENABLE_OFFLINE_AGENT_UI === '1';

  return {
    plugins: [react()],
    base: './',
    envDir: '..',
    define: {
      __OFFLINE_AGENT_MODE__: JSON.stringify(offlineAgentMode),
    },
    build: {
      outDir: '../docs',
      emptyOutDir: false,
    },
  };
});

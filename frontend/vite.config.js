import { defineConfig } from 'vite'

export default defineConfig({
  // --- Development Server ---
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    // Dev proxy: routes /api and /health to local FastAPI backend
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  // --- Production Build ---
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
    // Increase chunk size warning limit for larger bundles
    chunkSizeWarningLimit: 1000,
  }
})

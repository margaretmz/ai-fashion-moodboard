import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7860',
        changeOrigin: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
        },
      },
      '/gradio_api': {
        target: 'http://127.0.0.1:7860',
        changeOrigin: true,
      },
      '/file': {
        target: 'http://127.0.0.1:7860',
        changeOrigin: true,
        rewrite: (path) => path
      },
    },
  },
})


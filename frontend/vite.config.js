import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
export default defineConfig({ plugins: [react(), VitePWA({ registerType: 'autoUpdate', manifest: { name: 'KrishiMitra AI', short_name: 'KrishiMitra', description: 'Predict. Advise. Act.', theme_color: '#166534', background_color: '#F8FAF7', display: 'standalone', icons: [] }, workbox: { navigateFallback: '/index.html' } })] });

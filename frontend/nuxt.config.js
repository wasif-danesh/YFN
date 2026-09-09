import tailwindcss from '@tailwindcss/vite'

// Render injects the API's public origin. Local development uses the existing API_BASE setting.
const apiBase = process.env.NUXT_PUBLIC_API_BASE
  || (process.env.NUXT_PUBLIC_API_ORIGIN ? `${process.env.NUXT_PUBLIC_API_ORIGIN.replace(/\/$/, '')}/api/v1` : 'http://localhost:8000/api/v1')

export default defineNuxtConfig({
  compatibilityDate: '2026-09-09',
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  vite: { plugins: [tailwindcss()] },
  runtimeConfig: { public: { apiBase } },
  app: { head: {
    title: 'API test console | Your Friendly Neighbourhood',
    htmlAttrs: { lang: 'en' },
    meta: [
      { name: 'description', content: 'Development console for testing the four Your Friendly Neighbourhood API endpoints.' },
      { name: 'robots', content: 'noindex, nofollow' },
    ],
  } },
  nitro: { preset: 'static' },
})

# Frontend · Registro de acceso a equipos por QR

Vue 3 + Vite + TypeScript + Vue Router + Pinia + PrimeVue. Ver SRS-IC-001 §7 y §9.1.

## Requisitos
Node 22.18+ (o 24.12+) y npm.

## Arranque
```bash
cd frontend
npm install
npm run dev
```

## Scripts
| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Type-check y build de producción |
| `npm run lint` | ESLint (0 warnings permitidos) |
| `npm run format` / `format:check` | Prettier |
| `npm run type-check` | `vue-tsc` |
| `npm test` / `npm run test:cov` | Vitest (cobertura mínima 75 %) |

## Estructura
- `src/api/` cliente HTTP; el access token vive solo aquí (nunca en localStorage ni Pinia).
- `src/stores/` Pinia; solo nombre y rol del usuario.
- `src/router/` rutas y guards (`public` / `user` / `admin`).
- `src/views/` pantallas W-01 a W-13 (placeholders hasta tener mockups, PEND-01).

## Reglas
Mobile-first desde 360 px, interfaz en español, sin secretos en el repo.

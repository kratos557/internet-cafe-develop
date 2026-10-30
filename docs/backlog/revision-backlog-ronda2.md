# Revisión del backlog v1.2, ronda 2 (7 agentes)

| Campo | Valor |
|---|---|
| Fecha | 23 de octubre de 2026 |
| Backlog revisado | `docs/backlog/backlog-mvp.md` v1.2 |
| Ronda anterior | `docs/backlog/revision-backlog.md` (5 bloqueantes, 17 altas, 17 medias) |
| Método | Los mismos 7 agentes verificaron si cada hallazgo de la ronda 1 quedó resuelto, volvieron a simular día por día las tareas de su equipo y buscaron problemas nuevos. Ninguno modificó archivos. |

## 1. Veredicto

**La v1.2 mejoró mucho.**
- No hay bloqueantes nuevos.
- De los 5 bloqueantes de la ronda 1, tres quedaron resueltos y dos a medias.
- Los tres hitos (reviews del 31/10 y del 7/11, entrega del 16/11) pasan de **"no demostrables"** a **"demostrables con riesgo"**.
- Quedan **9 hallazgos altos** y unos **20 medios**. Casi todos son de coordinación entre equipos (calendario, entornos, pruebas), no de alcance.

Lo que todos los revisores validaron:
- Las sumas del CSV coinciden con la sección 3: 114, 112 y 70 h + 42 h de reserva.
- Las fechas coinciden entre tablas, CSV y Gantt.
- Ninguna tarea termina antes que su dependencia y ninguna pasa de 6 h.
- Ninguna tarea Debe depende de una Debería.
- Los 37 endpoints están cubiertos o recortados.

## 2. Estado de los hallazgos de la ronda 1

| Hallazgo | Estado | Qué falta |
|---|---|---|
| B1 entorno dev | Resuelto | Detalle: OPS-11 termina el viernes 30, pero el hito dice jueves 29. |
| B2 clave pública del PC | Resuelto en papel | La firma no se activa en ningún entorno antes del congelamiento (ver R2-2). |
| B3 demo repetible | Parcial | El servidor cierra la sesión, pero en el Sprint 1 el PC no puede volver del tablero al QR sin reiniciar la app. Hay además una carrera entre RN-02 y la rotación del QR. |
| B4 regresión final | Resuelto | No queda margen si la aceptación encuentra defectos altos el jueves 12 (ver R2-6). |
| B5 producción sin admin | Parcial | Render Free no tiene consola: `create-admin` y la semilla no tienen dónde ejecutarse (ver R2-4). |
| A2 integraciones el mismo día | **No resuelto** | Las fechas Fin chocan con el corte del jueves (ver R2-1). |
| A16 cobertura de pruebas | Parcial | Nadie es dueño de oasdiff ni de la cobertura (RNF-MAN-01 y 03), y la DoD de la web no se puede verificar a tiempo. |
| A17 aceptación frente a recortes | Parcial | E-02 (últimos accesos) y E-06 (CSV) no están reescritos. |
| A1, A6, A10, A11, A15, M4, M6, M8, M14 | Parcial | Se detallan en las secciones 3 y 4. |
| A3, A4, A5, A7, A8, A9, A12, A13, A14, M1, M2, M3, M5, M7, M9, M10, M11, M13, M15, M16, M17 | **Resueltos** | — |

## 3. Hallazgos altos de la ronda 2

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| R2-1 | **El corte del jueves contradice las fechas Fin.** El calendario dice que el jueves a las 22:00 "todo está fusionado", pero el campo Fin significa "PR fusionado" y 12 tareas del Sprint 1 (BE-06, BE-07, SEC-05, DSK-03, DSK-05b, DSK-06, UI-06, OPS-11…) y 9 del Sprint 2 terminan el viernes. | Los 7 | Redefinir el corte: **jueves 22:00 = PR abierto con `ci-ok` en verde; viernes 18:00 = fusionado**, y Fin = fusionado antes del congelamiento del viernes. Adelantar al miércoles el inicio de BE-06 (con `events.py`) y dividir BE-07 en 07a (vista previa) y 07b (claim), ambas con fin el jueves. |
| R2-2 | **La firma RFC 9421 no corre desplegada antes del congelamiento.** Dev sigue en modo `token` hasta el lunes 9, así que la review del 7/11 no puede mostrarla y la primera prueba real entre Java y Python cae después del congelamiento. Riesgo técnico: detrás del proxy TLS de Render, `@target-uri` podría reconstruirse como `http://` y todas las firmas reales fallarían. | Desktop, Seguridad, Trazabilidad, Backend | `MACHINE_AUTH_MODE=token\|dual\|signature`: el PC envía token y firma hasta SEC-14. **Dev pasa a `signature` en la integración del viernes 6**, como criterio de DSK-12b y de la review. SEC-07 arma la URI desde `PUBLIC_API_BASE_URL`. Producción nace en `signature`, porque no hay PCs de producción antes del 10. OPS-14 depende de DSK-12b. |
| R2-3 | **Los repartos por persona no cuadran.** Backend en el S1 (29 h en bloques de 6, 6, 4…), Seguridad en el S2 (6, 4, 3, 3, 3, 2), Desktop en el S2 (cadena DSK-21 → DSK-10/11 que arranca el jueves) y Testing en el S1 (15 h). | Backend, Seguridad, Desktop, Testing | Dividir BE-07, SEC-07 (07a base y verificación; 07b ventana, nonce y bandera) y DSK-03 (03a par de claves y PKCS12 con certificado autofirmado; 03b pantalla y enroll). Pasar el módulo JWT a SEC-00 (+1 h) para que SEC-04 termine el miércoles. SEC-03b y SEC-09 empiezan el lunes 2. DSK-21 se adelanta a lunes y martes contra la API simulada. **Publicar un reparto sugerido por persona** en cada sprint. |
| R2-4 | **Ejecución en producción y secretos.** Render Free no tiene consola ni trabajos puntuales, así que la semilla, `create-admin` y el reset necesitan las llaves de cifrado fuera de Render. Además, con el repo público y sin GitHub Environments con aprobación, cualquier workflow modificado en una rama puede leer las credenciales del migrador y el deploy hook. Tampoco está definido Vercel producción. | PO, Backend, Seguridad | Workflows `seed`, `reset` y `create-admin` con `workflow_dispatch` en **GitHub Environments `dev` y `prod`** con revisores y restringidos a `main` y `v*`. La carpeta `.github/` a nombre del PO en CODEOWNERS. Pipeline: push a `main` → una sola cabeza de Alembic → `upgrade` → deploy hook → humo, con el auto-deploy de Render apagado. Producción solo desde etiquetas `v*`, y un segundo proyecto de Vercel desplegado por CLI. El `pg_dump` se guarda cifrado fuera de GitHub. |
| R2-5 | **El backlog sigue prometiendo cosas recortadas.** E-02 pide "sus últimos accesos" (HU-11 es Debería) y E-06 pide exportar a CSV (HU-33 es Debería). La mitigación de un riesgo aceptado dice "bloquear la cuenta por API", que depende de HU-26 (Debería), y RN-12 no tiene tarea. RF-EQU-05 sigue diciendo "≤ 60 s". | UI, Testing, Trazabilidad, Backend | Agregar a la sección 4: E-02 sin últimos accesos, E-06 sin CSV y RF-EQU-05 dentro de la desviación de 65 s. Subcomando `block-user` en el CLI de BE-20 (+1 h), que revoca las sesiones web y cierra el acceso activo (RN-12). QA-11 con 2 PCs en modo pasivo y 1 en kiosco (§15.4). |
| R2-6 | **No queda margen tras la aceptación.** QA-11, SEC-11 y SEC-12 terminan el jueves 12, la misma noche de la versión candidata. Si encuentran un defecto alto, no hay día hábil para corregirlo. Además, k6 y las pruebas de rate limit en producción chocarían con la aceptación. | Testing, Seguridad, Backend | **Pre-aceptación en dev el lunes 9** con los casos de QA-08. SEC-12 y la parte de SEC-11 que no depende de SEC-14 van del 9 al 11 en dev. OPS-09 depende de QA-11. Si hay defectos altos abiertos, `rc.2` el viernes 13 a las 14:00. k6 (BE-19) solo en dev, con el rate limit apagado y usando Locust con el firmador Python (k6 es JavaScript). |
| R2-7 | **Las pruebas tienen ciclos y la DoD de la web no se puede verificar.** "Los negativos se fusionan junto con el código" crea ciclos cuando una tarea QA cubre varias tareas de desarrollo encadenadas. La DoD dice que la web "se verifica en el E2E", pero QA-10 llega el 9/11. RNF-MAN-01 (oasdiff) y RNF-MAN-03 (cobertura) no tienen dueño. | Testing, UI, PO, Backend | El dev fusiona con su camino feliz. Testing abre su PR `test/QA-xx` hasta el viernes a las 18:00, y la historia se cierra con el punto 4 de la DoD. DoD de la web: Vitest en UI-04b (token y refresh) y UI-15 (guards), más evidencia en el PR (+1 h en UI-15). QA-10 +1 h para la prueba de humo de inicio, historial y admin. pytest-cov y oasdiff en OPS-05. La cobertura web del 75 % pasa a ser una desviación. |
| R2-8 | **El carril del PO no tiene capacidad declarada.** Suma ~38 h en Debe, ~20 h en la semana del Sprint 1 con ceremonias, y 8 h de preparación entre el jueves 22 (ya pasó) y el domingo 25. El suplente no puede entrar a Vercel Hobby, que no admite miembros. | PO | Declarar la capacidad del PO. Antes del sábado, **cargar solo la Preparación y el Sprint 1** en el Project. Pasar gitleaks al `ci-ok` mínimo de OPS-00. Mover OPS-05 de martes a jueves. El suplente opera con `workflow_dispatch`, y la DoD de las tareas OPS incluye "runbook actualizado". |
| R2-9 | **La cuota de Neon de producción se pasaría.** BE-09b consulta la BD cada 30 s, y junto con los latidos y el long-poll mantienen Neon despierto. Se estiman ~105 CU-h al mes en prod, por encima del límite de 100. | PO | Tope de 0,25 CU por proyecto (OPS-02). BE-09b solo consulta si hay sesiones o retos activos en memoria, o lo hace cada 60 s. Alerta al 70 % de la cuota (OPS-06). |

## 4. Hallazgos medios (se corrigen al aplicar la v1.3)

**API y seguridad**
- **Login automático tras el registro frente a RF-AUT-01:** el registro siempre responde 202 y la web llama a `/auth/login`. Si falla, muestra "Si ya tienes cuenta, inicia sesión" y la enumeración residual queda documentada.
- **Prueba de posesión del enrolamiento** (SRS §8.4): DSK-03 firma el código y SEC-05 verifica (+1 h). SEC-05 también valida que el JWK sea P-256 sin `d`, calcula la huella y devuelve el `keyid`. Se agrega un vector con cero inicial.
- **Carrera entre RN-02 y la rotación:** BE-05 no cierra una sesión cuyo reto de origen siga vigente, y DSK-05b cancela la rotación al recibir `approved`. Caso en QA-05.
- **`close_session()`** nace en BE-05 (S1), no en BE-09a.
- **BE-18 (contrato v0.2)** sube a 3 h y se publica en dos partes: latido y cierres el lunes, admin el martes. Seguridad lo aprueba.
- **Interfaz `pii`:** contrato de tipos y tamaños, blind index con el HMAC de SEC-00 desde el Sprint 1, y Seguridad revisa BE-04. Al aplicar SEC-06 se vuelven a sembrar solo los usuarios y sus sesiones, sin borrar los equipos enrolados.
- **BE-21:**
  - Los logs sin datos personales pasan a BE-02, en el Sprint 1.
  - `TrustedHostMiddleware` incluye los hosts de Render y Vercel.
  - OPS-12, SEC-11 y SEC-12 dependen de BE-21.
  - Se quita `APP_TIMEZONE`.
- **Rate limit detrás del NAT del campus:** saltos confiables por ruta, umbral por IP configurable y el refresh fuera del límite por IP.
- **Privilegios:**
  - Por defecto, el rol de la app solo tiene SELECT, INSERT y UPDATE.
  - El TRUNCATE de las pruebas usa la conexión del migrador.
  - SEC-10 prueba que `audit_log` solo admite INSERT.

**Escritorio**
- **Repetir la demo del Sprint 1:** botón "Volver al QR" solo en el perfil dev de DSK-06.
- **Kiosco:**
  - Libera la pantalla cuando hay sesión y vuelve a bloquear al cerrarse.
  - Recupera el bloqueo cuando vuelve la API tras un fail-open.
  - Usa un bloqueo de instancia única (FileLock).
- **Modo pasivo:** usa `java.awt.SystemTray`, porque JavaFX no tiene bandeja del sistema.
- **Empaquetado:** `org.beryx.jlink` desde DSK-01, porque ZXing es un módulo automático. WiX 3.14 fijo, y `--win-upgrade-uuid` fijo para que las reinstalaciones conserven `ProgramData`.
- **Enrolamiento:** se ejecuta como administrador (modo `--enroll` elevado). Enrolar los 3 PCs del piloto el martes 10 (OPS-12 con DSK-15).
- **Calidad:** Spotless desde DSK-01 y `System.nanoTime()` desde DSK-04a.

**Web**
- **Dependencias de UI-17 y UI-15:** UI-17 bloquea a UI-08, UI-10, UI-11 y UI-12; UI-15 es dependencia de integración de esas cuatro.
- **Wireframes de UI-07a:** el layout y la 404 entran ahí.
- **UI-11:** suma "editar" sala y equipo.
- **UI-05:** página de destino provisional en el Sprint 1.
- **Cola de caída del S2:** UI-12 entra, quedando solo con los filtros por sala y "activas".

**Pruebas, plataforma y Scrum**
- **Medir "< 1 s":** video a 60 fps que capture el celular y el PC, 20 corridas, p95 = valor 19. DSK-08 registra el momento de la detección para medir el ≤ 65 s.
- **Dependencias de QA-10:** el firmador de SEC-08 y el entorno dev.
- **Colas de caída corregidas:**
  - Se agregan ítems de Backend (idempotencia y auditoría del claim se completan el lunes 2).
  - Se quitan los ítems que no liberan nada (el MSW ya usado y el "fail-open configurable" que no existe).
- **Projects:**
  - La vista de defectos fuera del filtro `tipo:tarea`.
  - Campo Épica para el Roadmap.
  - Columna de dependencias bloqueantes en el CSV.
  - Títulos de menos de 256 caracteres.
  - Script de carga que se puede reanudar por `[ID]`.
- **Dependencias externas con dueño y fecha** (las pide el PO hoy):
  - PEND-07: salas y equipos del piloto.
  - PEND-06: dominios de correo.
  - PCs del piloto.
- **HU-29 y HU-30:** agregar criterios de aceptación.

## 5. Bajas

- **Dependencias bloqueantes del mismo día:** aceptar explícitamente "el mismo día si la dependencia se fusiona en la mañana".
- **Dependencias faltantes en tareas Debería:**
  - Cada tarea de UI debe depender de su tarea de API: ST-UI-02 → ST-SEC-02, ST-UI-05 → ST-BE-03, ST-UI-03 → ST-BE-02, ST-UI-01 → ST-SEC-01.
  - ST-DSK-02 debe depender de ST-BE-04.
  - ST-BE-02 y ST-BE-03 no deben depender de pantallas.
- **CSV:** `referencia_srs` sale recortada por un error del script.
- **Detalles de UI:**
  - Nombrar quién aprueba los wireframes del Sprint 2.
  - El login no muestra el enlace de recuperación.
  - Distinguir "Cerrar sesión web" de "Terminar acceso".
  - DSK-09 debe depender de UI-03.
- **Documentación:** UI-13 y UI-16 pueden entrar después de la versión candidata.
- **Tiempo del triaje** (15 min al día): presupuestarlo.
- **Prueba de humo con login de OPS-08:** necesita un usuario en producción.

## 6. Impacto en la capacidad

Las correcciones agregan unas **6–7 h a los equipos** y **3–4 h al PO**. Se reparten así:

| Equipo | Horas | Origen |
|---|---|---|
| Seguridad | +2 | JWT en SEC-00 y prueba de posesión |
| Backend | +2 | BE-18 y `block-user` |
| UI | +1 | Vitest |
| Testing | +1 | Humo del admin |
| Desktop | +0,5 | Firma del código de enrolamiento |

Se absorben así:
- **Backend:** los logs pasan de BE-21 a BE-02 (neutro).
- **Testing:** se compensa con la pre-aceptación del lunes 9 (que reemplaza parte de QA-11).
- **Resto:** con las colas de caída corregidas.

Los porcentajes de compromiso quedan casi iguales: ~103 % en el S1 y ~101 % en el S2.

## 7. Decisiones del PO

1. **Corte del jueves** = PR abierto con CI en verde; fusión hasta el viernes a las 18:00. *Recomendado.*
2. **Modo `dual`** y dev en `signature` desde el viernes 6; producción nace en `signature`. *Recomendado.*
3. **Producción** solo desde etiquetas `v*`, con GitHub Environments y aprobación. *Recomendado.*
4. **Capacidad del PO:** antes del sábado se carga solo la Preparación y el Sprint 1. *Recomendado.*
5. **Cobertura:** oasdiff y pytest-cov en CI; cobertura web como desviación. *Recomendado.*
6. **Prueba de posesión del enrolamiento:** implementarla (+1,5 h) en lugar de recortarla. *Recomendado:* detecta en el Sprint 1 errores del JWK que de otro modo aparecerían el 9/11.
7. **Bloqueo de cuentas** con `block-user` en el CLI. *Recomendado.*

> Advertencia de tiempo: hoy es viernes 23 y la socialización es mañana. Si se aplica la v1.3 hoy, conviene **no hacer una ronda 3 completa con los 7 agentes**. La ronda 2 alcanzó el límite de uso, y basta con validar la v1.3 con los scripts (fechas, dependencias y sumas) y un solo agente de integración.

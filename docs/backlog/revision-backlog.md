# Revisión del backlog del MVP (simulación con 7 agentes)

| Campo | Valor |
|---|---|
| Fecha | 22 de octubre de 2026 |
| Backlog revisado | `docs/backlog/backlog-mvp.md` v1.1 (con fechas) |
| Método | 7 agentes revisores (UI, Desktop, Backend, Seguridad, Testing, PO/DevOps/Scrum, Trazabilidad e integración) recorrieron en papel, día por día, cada tarea de su equipo. No escribieron código ni modificaron archivos. |
| Resultado | **5 bloqueantes, 17 altas, 17 medias y ~20 bajas** (sin duplicados). Ninguno de los tres hitos (review del 31/10, review del 7/11, entrega del 16/11) se puede demostrar tal como está el plan. |

La columna "Quién lo vio" indica cuántos revisores encontraron el mismo problema por su cuenta. Cuantos más, más fiable es el hallazgo.

## 1. Bloqueantes

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| B1 | **El entorno dev del Sprint 1 no tiene dueño.** Nadie aplica las migraciones ni la semilla en Neon dev (eso llega con OPS-08 en el Sprint 2). El rol de la app no tiene GRANT hasta SEC-10 (6/11). Además, nadie fija `FRONTEND_BASE_URL` (el dominio del QR) ni `API_BASE_URL`, OPS-04 necesita la URL de Render sin depender de OPS-03, y la integración del viernes 30 no tiene tarea. | Backend, Trazabilidad, PO, Testing, Desktop | **OPS-11** (PO, 3 h, jue 29): workflow manual que migra y siembra dev, fija `FRONTEND_BASE_URL` y `--workers 1`. **OPS-02** incluye `bootstrap_roles.sql`, GRANT base y `ALTER DEFAULT PRIVILEGES`. OPS-04 depende de OPS-03. **QA-02** pasa a ser un script idempotente que genera N códigos de enrolamiento a pedido. **Corte de PRs el jueves 29 en la noche** e integración el viernes 30. |
| B2 | **La clave pública del PC nunca se registra.** SEC-05 emite una "credencial provisional", pero ninguna tarea cambia `/machine/enroll` para recibir el JWK, ni hace que el escritorio genere el par de claves. Sin eso, SEC-07 no puede resolver el equipo por `keyid` y no hay firma RFC 9421 (objetivo del Sprint 2). Además, nada retira la credencial provisional, y si queda viva cualquiera puede saltarse la firma (downgrade). | Seguridad, Desktop, Trazabilidad, Backend | **Registrar la clave desde el Sprint 1**, sin re-enrolar después: DSK-03 genera el par P-256 en el PKCS12 al enrolar (+2 h), y SEC-05 guarda el JWK y su huella RFC 7638 (+1 h). La credencial provisional (token opaco de 256 bits guardado como hash, cabecera fija) se define en el contrato v0.1 (BE-01). En el Sprint 2, SEC-07 verifica la firma con una bandera `MACHINE_AUTH_MODE=token\|signature`. **SEC-14** (Seguridad, 2 h) retira la credencial provisional y QA-09 prueba que un token solo devuelve 401. |
| B3 | **La demo del Sprint 1 solo sale una vez.** BE-05 no implementa la regla RN-02 ("crear un reto cierra la sesión abierta del equipo"), y en el Sprint 1 no existe ninguna vía de cierre. Tras el primer claim, el PC queda ocupado y el long-poll responde `approved` de inmediato. | Backend, Trazabilidad, Desktop | BE-05 +1 h (RN-02 y RN-08), BE-07 +1 h (`superseded` y `MACHINE_BUSY`), QA-05 +1 h (casos de prueba de las dos reglas). |
| B4 | **No queda día hábil para la regresión final.** La versión candidata se crea el sábado 14, día de review, y QA-13 la debería probar entre el 13 y el 14. QA-12 cierra el informe antes de tener esos resultados, y los arreglos del domingo llegan a `v1.0.0` sin probar. | Testing, PO | Versión candidata el **jueves 12 en la noche**, QA-13 el viernes 13 y QA-12 cerrado esa misma noche. **QA-14** "humo de v1.0.0" (Testing, 1 h, lun 16). |
| B5 | **Producción no tiene administrador ni datos.** El registro solo crea estudiantes, HU-26 (gestión de usuarios) es Debería y QA-02 es solo para dev. Aun así, QA-11 ejecuta los escenarios E-01 a E-06 en producción. Tampoco hay limpieza de datos de prueba, backup ni `.msi` apuntando a producción. | Backend, Testing, Trazabilidad, PO | **BE-20** CLI `create-admin` y carga de salas y equipos del piloto (Backend, 2 h, de la reserva de estabilización). **OPS-12** (PO, lun 9): producción desde la etiqueta del congelamiento, administrador inicial, datos del piloto, limpieza, `.msi` de producción y `pg_dump` antes del 16. |

## 2. Altas

### Capacidad y flujo

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| A1 | **La capacidad está al 100 % y no se puede repartir por persona.** Con tareas de 5 y 6 h, varias personas quedan con 8 o 9 h. Las reuniones del jueves (refinamiento e integración) no se descontaron. Testing no tiene reserva en la estabilización, aunque debe volver a probar los arreglos. El carril del PO pasa de 22 h a ~35 h y no tiene suplente. | Todos | Dividir las tareas grandes (ver A2, A8, A11, A14). Dar 3 h de reserva a Testing. Nombrar un suplente del PO con acceso a las consolas y un runbook. Decidir qué cae primero (ver §5). |
| A2 | **Las integraciones caen el mismo día de la integración.** Diez tareas críticas terminan el viernes 30, la cadena de Backend es serial (18 h seguidas) y BE-06 depende de BE-05 sin necesidad. | Backend, Desktop, UI, Testing | BE-06 depende de BE-04 y BE-07 (de integración) y crea el registro de eventos (`events.py`); BE-07 solo llama a `notify()`. BE-02 y BE-03 se hacen en pareja. Integración interna de cada equipo el jueves 29 contra las APIs simuladas. |

### Plataforma y secretos (carril del PO)

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| A3 | **Nadie genera ni custodia las llaves:** `JWT_PRIVATE_KEY` (se necesita el 29), `DATA_ENC_KEYS` y `BLIND_INDEX_KEY`. Perder `DATA_ENC_KEYS` es perder los datos personales. | Seguridad, PO | **SEC-00** (Seguridad, 2 h, lun 26–mar 27): script `tools/keys`, `.env.example`, y la API no arranca sin llaves (sin valores por defecto). El PO carga llaves distintas por entorno y guarda un respaldo fuera de línea. |
| A4 | **El repositorio es público y el escaneo de secretos llega el 10/11.** Mientras tanto, estudiantes novatos generan llaves. | Seguridad, PO | Push protection, Dependabot y CodeQL en OPS-01. gitleaks, pip-audit y npm audit en OPS-05 desde el primer PR. |
| A5 | **El repositorio no está listo para el primer PR.** Faltan CODEOWNERS e invitaciones para los 16, y la protección de `main` no puede exigir checks que aún no existen. Con filtros por ruta, un workflow omitido deja el check requerido pendiente y bloquea el PR. | PO, Testing | **OPS-00** (PO, vie 23–dom 25): esqueleto de carpetas, `.env.example`, CODEOWNERS e invitaciones. CI mínima el lunes 26 con un job agregador `ci-ok` como único check requerido. PostgreSQL como servicio en la CI con los dos roles. |
| A6 | **No hay matriz de entornos ni de cuotas.** Render da 750 h por workspace y producción con pinger consume ~720. Neon reparte 100 CU-h por proyecto entre todas sus ramas. Vercel publica `main` como producción. | PO | Matriz antes del 26: dev = alias estable de Vercel + Render dev sin pinger + proyecto Neon dev; prod = rama o etiqueta de release + Render prod + proyecto Neon aparte. Pinger solo a prod y en horario de salas. Dividir OPS-08 en 08a (despliegue continuo a dev, Sprint 1) y 08b (producción). |

### Seguridad y API

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| A7 | **SEC-06 (cifrado) obliga a rehacer trabajo.** Registro, login, semilla y consultas se escribirían dos veces. El AAD con el id de la fila no se puede usar en un `TypeDecorator`. Tres migraciones simultáneas generan varias cabezas de Alembic. | Seguridad, Backend, Testing | BE-04 crea desde el principio las columnas finales (`*_ct`, `*_bidx`) con una interfaz `pii` provisional, y SEC-06 solo cambia la implementación (baja de 6 a 4 h). AAD = `tabla.columna` (desviación documentada). Dev se vuelve a sembrar en vez de migrar datos. Regla: rebase de `down_revision` antes de fusionar, y un check de CI que exija una sola cabeza. |
| A8 | **SEC-03 está incompleta y UI-04 contradice al SRS.** Faltan la gracia de 10 s del refresh, la validación de `Origin` y quién pone la cookie. Sin Web Locks, la pestaña que abre el QR y la pestaña existente hacen refresh a la vez, el servidor lo toma como reuso y cierra la sesión en plena demo. UI-04 guarda el token en un "store", pero el SRS §12.2 dice que va en una variable privada del módulo. | Seguridad, UI | Dividir SEC-03 en 03a (Sprint 1: cookie, refresh y logout) y 03b (Sprint 2: detección de reuso, gracia de 10 s y `Origin`). Dividir UI-04 en 04a (cliente y MSW, 3 h) y 04b (token en el módulo y refresh al arrancar, 2 h, depende de SEC-03a). Web Locks pasa al Sprint 2. |
| A9 | **El rol de BD mínimo llega tarde y las pruebas corren con superusuario,** lo que esconde los errores de permisos. | Seguridad, Testing | Los roles y GRANT base se crean en OPS-02. QA-01 crea los roles en Docker y en CI, y las pruebas corren con el rol de la app. SEC-10 queda en ajuste y prueba (3 h). |
| A10 | **El rate limit por IP puede bloquear a toda una sala,** porque detrás del rewrite de Vercel o del NAT del campus todos comparten IP. | Seguridad, Testing | SEC-09 limita primero por cuenta, define qué cabecera `X-Forwarded-For` es confiable y agrega `RATE_LIMIT_ENABLED` para las pruebas. `/machine/enroll` también queda limitado. |
| A11 | **El traspaso de vectores de firma a Desktop es frágil.** ECDSA no es determinista, así que Java no puede producir firmas idénticas a las de Python. DSK-12 (6 h) es demasiado grande. | Seguridad, Desktop | SEC-08 pasa a 4 h, solo el lunes 2 y como bloqueante. Los vectores comparan la base de firma y el digest, y SEC-08 entrega un firmador Python de referencia. DSK-12 se divide en 12a (firmador con JUnit contra los vectores, 4 h) y 12b (conexión con el cliente, 2 h). |

### Escritorio

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| A12 | **El escritorio no corrige el desfase de reloj (RF-EQU-08)** y DSK-05 fija "cada 45 s" en lugar de usar `rotate_after_s`. | Desktop, Trazabilidad | **DSK-20** (2 h): desfase calculado con la cabecera `Date`, reintento ante `MACHINE_CLOCK_SKEW`, cuenta regresiva con reloj monotónico y `rotate_after_s`. |
| A13 | **El cambio de modo remoto no tiene dueño.** El latido no devuelve `mode`, nadie aplica el modo en caliente, y JavaFX no puede bloquear la tecla Windows ni Alt+Tab sin un hook nativo. | Desktop, Trazabilidad | BE-08 devuelve `mode`. **DSK-21** gestor de ventana y modo (2 h) antes de DSK-10 y DSK-11, y DSK-11 depende de DSK-09. Decisión del PO: el bloqueo de Win y Alt+Tab queda como limitación documentada. |
| A14 | **El instalador llega tarde y es más complejo de lo estimado.** Temurin no trae JavaFX, jpackage necesita WiX y no crea tareas programadas, y "relanzar en ≤ 10 s" (RF-EQU-02) no tiene decisión. | Desktop | DSK-01 deja un proyecto modular con jlink. Dividir DSK-14 en 14a (`.msi` con runtime y truststore, lun 2–mié 4) y 14b (script `schtasks` que ejecuta TI). El relanzamiento automático queda recortado explícitamente en la sección 4. |

### Web, pruebas y alcance

| ID | Problema | Quién lo vio | Corrección propuesta |
|---|---|---|---|
| A15 | **Hay pantallas sin wireframe y trabajo de la web sin tarea.** Faltan el layout, la navegación por rol, los guards, la página 404 y el manejo de errores RFC 9457. Nadie regenera el cliente con el contrato v0.2. La pantalla de escaneo no tiene wireframe, ni las variantes de escritorio (pasivo, kiosco, bandeja). RF-QR-05 (conservar el token tras el login) y RF-QR-08 (mensajes de QR vencido o usado) no tienen tarea. | UI, Trazabilidad | UI-03 sube a 3 h. UI-07 +1 h (pantalla de escaneo). **UI-15** layout, guards, 404 y errores (4 h). **UI-17** cliente y MSW con el contrato v0.2 (2 h, lun 2). RF-QR-05 y RF-QR-08 pasan al criterio de UI-06 (+1 h). |
| A16 | **Parte de la cobertura de pruebas no tiene dueño.** Faltan las pruebas de componentes Vue, JUnit en el escritorio, el simulador `fake-pc`, la cobertura con oasdiff y el humo después de cada despliegue. Además, la DoD crea un ciclo: el PR de la API exige la prueba de integración, pero la escribe Testing en otra tarea que termina el mismo día. | Testing, PO, Desktop | Regla: el desarrollador entrega el camino feliz en su PR, Testing escribe los casos negativos en la misma rama y se fusionan juntos. DoD por nivel: tarea = unitarias + CI; historia = integración + despliegue en dev. JUnit entra en DSK-12a. Cobertura y oasdiff van en OPS-05, y el humo en OPS-08. Decisión del PO: pruebas de componentes Vue y `fake-pc`. |
| A17 | **Los escenarios de aceptación contradicen los recortes.** E-01 pide verificar el correo, que está recortado, y QA-08 y QA-11 prometen "E-01 a E-06 del SRS". El SRS v1.1 llega el 11–13/11, en plena aceptación. | Testing, Trazabilidad, PO | El PO aprueba la sección 4 ampliada el **sábado 24** y esa lista es la entrada de QA-08. Reescribir E-01 "sin OTP" y HU-08 "salvo clave no exportable". OPS-07 pasa a Debería, y hay que pedir hoy el dominio para el correo (PEND-02) o sacar HU-24. |

## 3. Medias

| ID | Problema | Corrección propuesta |
|---|---|---|
| M1 | BE-09 está duplicada con BE-11 y BE-14, y la tarea de inactividad no tiene mecanismo. | BE-09a: `close_session()` y cierre desde el PC. BE-09b: tarea `asyncio` cada 30 s que también expira retos, con una función invocable desde las pruebas. QA-06 prueba latido, PC, `superseded` e inactividad; QA-07 prueba los cierres web y admin. |
| M2 | `audit_log` nace en BE-14, después de quienes la usan (el claim, SEC-05, BE-12, BE-13). | La tabla y un helper `audit()` pasan a BE-04 o BE-12. |
| M3 | La respuesta del long-poll en el Sprint 1 es ambigua. | El contrato v0.1 fija `user{full_name, student_code_masked}` y `recent_accesses: []`. BE-06 suelta la conexión de BD antes de esperar. |
| M4 | Dependencias que faltan o están mal: DSK-08 termina antes de BE-09 y BE-10; DSK-03 no depende de SEC-05; DSK-05 no depende de BE-05 y BE-06; UI-05 no depende de SEC-02; UI-06 no depende de BE-07; UI-08 depende de UI-07 pero su wireframe es UI-02; DSK-04 empieza antes de UI-03; QA-07 no depende de BE-12, BE-13 y BE-15; OPS-05 no depende de QA-01. | Corregir las dependencias y mover DSK-08 al miércoles 4–viernes 6, o dividirla. |
| M5 | El punto 3 de la DoR falla en el Planning 2: los wireframes de UI-07 se aprueban el martes 3. | La DoR 3 pasa a decir "antes de iniciar la tarea". Dividir UI-07: historial y perfil el lunes 2, admin el martes 3. |
| M6 | UI-11 (4 h) está subestimada: le faltan deshabilitar y revocar la clave. Nadie aplica `MACHINE_DISABLED` ni cancela los retos al deshabilitar un equipo. | UI-11a salas y equipos (4 h) y UI-11b detalle del equipo (3 h). BE-12 cancela retos al deshabilitar, y SEC-07 rechaza equipos que no estén activos. |
| M7 | La CSP del §12.9 puede bloquear los estilos de PrimeVue y el WASM del escáner en iOS (suposición a verificar). | Criterio en UI-01 y UI-09: "funciona en el preview de Vercel con las cabeceras de OPS-04". Agregar `style-src` y servir el WASM desde el propio dominio. |
| M8 | El flujo después del registro es ambiguo (¿login automático o ir al login?) y falta la casilla de consentimiento. | Definirlo en el wireframe de UI-02 y en el criterio de UI-05. |
| M9 | Criterios difíciles de medir: el p95 menor a 1 s no tiene instrumentación, el "≤ 60 s" no se cumple con un latido cada 60 s, el reloj no se puede controlar en las pruebas y falta la zona horaria del CSV. | Fixture de reloj en QA-01 y `now()` inyectable. DSK-06 registra en el log los tiempos y QA-08 mide 20 corridas. Criterio "≤ 65 s". Variable `APP_TIMEZONE`. |
| M10 | No hay proceso de defectos. | Etiquetas `severidad:*`, triaje diario entre el PO y el líder de Testing, corrige el dueño del código según CODEOWNERS, Testing verifica, y la versión candidata exige 0 defectos críticos o altos abiertos. |
| M11 | Vercel: faltan el Ignored Build Step y la prueba de PEND-03 (commit de un colaborador), y la protección de los previews puede bloquear a los celulares (suposición). | Incluirlo en OPS-04 y probarlo con un commit de un colaborador. |
| M12 | Carga en GitHub Projects: Projects no importa CSV (suposición), hace falta un script en dos pasadas para sub-issues y dependencias, el título no lleva el ID, las historias duplican horas y 3 h no alcanzan para 138 issues. | Título `[ID] …`, historias sin estimación, filtro `label:tipo:tarea` en vistas e Insights, script `gh`/GraphQL y OPS-01 a 5 h. |
| M13 | La calidad del escritorio no tiene tarea: linters, JUnit en la DoD y logs sin PII. | Linters en DSK-01 (o en la estabilización) y logs en DSK-02. |
| M14 | En la API faltan requisitos Debe sin tarea: `TrustedHostMiddleware`, límite de tamaño del cuerpo, cabeceras de seguridad, logs sin PII y errores 422 que no repitan el `input` (la contraseña). | Agregarlos a BE-02 y QA-03 (+1 h). |
| M15 | SEC-11 duplica QA-07 (IDOR) y QA-09 (alteración). | SEC-11 se enfoca en MITM con el `.msi` instalado, CSRF y `Origin`, enumeración, rate limit a través de Vercel, credencial retirada y logs. |
| M16 | Ceremonias: un bloqueo del jueves en la noche llega al viernes de integración, y la review usa un dev que cambia y se suspende. | Corte de fusiones el viernes a las 22:00 con la etiqueta `sprint-N-review`, calentar Render antes de la review y refinamiento de 60 min. |
| M17 | Riesgos no declarados: con cuentas activas sin verificar, alguien puede registrarse con el correo de otro estudiante. El PKCS12 que lee la app también lo puede leer el estudiante. | Declararlos como riesgos aceptados en la sección 4 y en SEC-13. |

## 4. Bajas (se corrigen al aplicar, sin decisión del PO)

- HU-02 dice "listos el martes", pero termina el miércoles 28.
- `/readyz` está en BE-02, antes de que exista la BD: pasa a BE-03.
- Faltan los IDs DSK-17 y UI-15 en la numeración.
- ST-SEC-03 dura 8 h (más que el máximo de 6), y a las tareas ST-* les faltan dependencias.
- EP-03 cita RF-ADM-02 a 04, que pertenecen a EP-07.
- HU-25 va primera en el orden de entrada, pero su aviso por correo depende de HU-24.
- SEC-02 no fija los claims `iss`, `aud` y `jti`, y el líder de Seguridad no aprueba el contrato.
- UI-01 no instala Vitest. HU-07 cita el logout (RF-AUT-08), cuyo botón llega en el Sprint 2.
- El CSV se descarga con fetch + Blob, no con un enlace directo. El escáner valida contra `location.origin`.
- RF-EQU-10 (cierre al apagar) no tiene tarea: queda como Debería.
- Nadie publica el `.msi` en Releases: pasa a OPS-08.
- BE-19 no alcanza para 300 equipos que firman sus peticiones: se divide.
- En QA-05, la prueba concurrente necesita TRUNCATE en lugar de rollback.
- OPS-01 y OPS-09 quedan fuera de las iteraciones, y HU-05 mezcla tareas de los dos sprints.
- En el CSV, `referencia_srs` está recortada (por ejemplo, HU-09 solo dice "RF-QR-01").

## 5. Impacto en la capacidad

Todas las cifras de esta sección son estimadas. Se validan con el script cuando se apliquen los cambios.

| Equipo | S1 hoy | Correcciones S1 | Movido a S2 | S1 resultante | S2 hoy | Correcciones S2 | S2 resultante | Capacidad |
|---|---|---|---|---|---|---|---|---|
| Backend | 28 | +3 | −0 | 31 | 28 | +4 | 32 | 28 |
| Seguridad | 20 | +3 | −3 (SEC-03b) | 20 | 21 | +4 | 25 | 21 |
| Testing | 14 | +1 | 0 | 15 | 14 | 0 | 14 | 14 |
| UI | 21 | +4 | −1 (Web Locks) | 24 | 21 | +12 | 33 | 21 |
| Desktop | 28 | +3 | 0 | 31 | 28 | +5 | 33 | 28 |
| **Total** | **111** | | | **121** | **112** | | **137** | **112** |

Las correcciones agregan unas **35 h de trabajo de equipos** y **13 h al carril del PO**. **UI es el cuello de botella**: 3 personas diseñan e implementan.

**Palancas para que cuadre (decisiones del PO):**

| Opción | Libera | Comentario |
|---|---|---|
| a. Escáner dentro de la web (UI-09) pasa a Debería | UI 5 h | La cámara nativa ya abre `/s#token` (RF-QR-01). |
| b. Exportación CSV (BE-15 y su botón) pasa a Debería | BE 2 h, UI 1 h | La consulta con filtros se mantiene. |
| c. "Últimos 5 accesos" en el PC pasa a Debería | BE 2 h, DSK 1 h | El tablero muestra nombre, código y cronómetro. |
| d. Tareas que no son funcionalidad nueva pasan a la estabilización y usan las reservas: BE-20, DSK-14b, SEC-14, linters del escritorio | ~7 h | Las reservas de defectos bajan de 49 a ~42 h. |
| e. Pruebas de componentes Vue y `fake-pc` como desviación documentada | ~6 h | Se cubren con E2E en Playwright y pruebas manuales. |
| f. Mover 1 persona del frente API (9 personas) a UI durante el Sprint 2 | +7 h en UI | Alivia el cuello de botella; Seguridad sigue ajustado. |
| g. Contrato v0.2 (BE-18) al lunes 2 y logs del escritorio al S2 | S1: BE 2 h, DSK 1 h | Las palancas a–d solo alivian el S2. Esta es la única para el S1. |

Resultado estimado:

- **Sprint 2:** con a + b + c + d queda en ~120/112 (+7 %). Sumando f (UI pasa a 28 h de capacidad), queda en ~120/119, prácticamente al 100 %.
- **Sprint 1:** queda en ~121/112 (+8 %). Con g baja a ~118/112 (+5 %).

Se recomienda publicar una **cola de caída**: si un viernes de integración llega atrasado, primero se cae lo de la cola y no se toca el objetivo del sprint. Por ejemplo, en el S1 caerían los casos negativos de QA-04 y el cronómetro de DSK-06.

## 6. Decisiones que necesita el PO

1. **Clave del PC desde el Sprint 1 (B2):** se recomienda registrar el JWK en el enrolamiento del Sprint 1 para no re-enrolar en el Sprint 2.
2. **Palancas de capacidad (§5):** se recomiendan a + b + c + d + f + g, más la cola de caída.
3. **Kiosco (A13):** se recomienda dejar el bloqueo de Win y Alt+Tab como limitación documentada, sin hook nativo.
4. **Criterio del latido (M9):** se recomienda "≤ 65 s" en lugar de un latido cada 50 s.
5. **Pruebas de componentes Vue y `fake-pc` (A16):** se recomienda la desviación documentada (opción e).
6. **Dominio de correo (A17):** pedirlo hoy a TI o sacar HU-24 del todo.
7. **Aprobar la sección 4 ampliada el sábado 24** con los nuevos recortes y riesgos aceptados: RF-EQU-02 sin relanzamiento automático, E-01 sin OTP, riesgos de M17 y AAD sin id de fila.

## 7. Lo que los revisores validaron sin problemas

- Las sumas de horas del CSV coinciden con la capacidad declarada por equipo y sprint (111, 112 y 63 h + 49 h de reserva).
- Ninguna tarea pasa de 6 h, salvo ST-SEC-03.
- Las fechas coinciden entre las tablas, el CSV y los Gantt.
- Se respetan las dependencias bloqueantes declaradas: contrato → clientes, wireframes → pantallas, BE-02 → BE-03 y BE-12 → BE-13.
- Los 37 endpoints del §10.3 están cubiertos o recortados explícitamente.
- La transacción de confirmación y el algoritmo del long-poll del SRS §8.1 están bien reflejados en BE-06 y BE-07.
- La caché de nonces y el rate limit en memoria son válidos con una sola instancia.
- Los recortes de correo, roles de BD y TPM son coherentes entre sí.
- Iteraciones de 7 días, límite de una tarea en progreso, ramas `tipo/ID` y paso automático a "Hecho" al fusionar.

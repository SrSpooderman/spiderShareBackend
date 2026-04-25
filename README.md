# Siguiente Lista de Trabajo

## Integracion Steam

Referencias: <https://partner.steamgames.com/doc/api>, <https://partner.steamgames.com/doc/webapi_overview>, <https://partner.steamgames.com/doc/features/auth>

1. Crear el modelo de vinculacion usuario-Steam.
   Anadir una tabla tipo `user_steam_accounts` con `user_id`, `steam_id_64`, timestamps y constraint unico por usuario y por Steam ID.
   Implementarlo en `app/modules/steam/infrastructure/models.py` y una migracion Alembic nueva, sin mezclarlo con la tabla `users`.
   Esta tabla sera la base para enlazar un usuario interno con su cuenta Steam y para colgar juegos/ownership despues.

2. Configurar credenciales y cliente Web API de Steam.
   Anadir `STEAM_WEB_API_KEY`, `STEAM_APP_ID` y `STEAM_WEB_API_BASE_URL` al settings y `.env.example`.
   Completar `app/shared/infrastructure/providers/steam/steam_client.py` con llamadas HTTPS a `partner.steam-api.com` o `api.steampowered.com`.
   El cliente debe envolver `AuthenticateUserTicket` y, mas adelante, `CheckAppOwnership` o `GetPublisherAppOwnership`.

3. Implementar el caso de uso para vincular Steam.
   Crear un servicio de aplicacion en `app/modules/steam/application` que reciba el usuario actual y un ticket/token de Steam.
   Validar el ticket con Steam, extraer el SteamID64 devuelto y persistirlo mediante un repositorio del modulo `steam`.
   Debe controlar errores de ticket invalido, SteamID ya vinculado a otro usuario y usuario que ya tiene cuenta Steam vinculada.

4. Exponer endpoints autenticados para vincular y consultar Steam.
   Crear `app/modules/steam/entrypoints/routes.py` con `POST /steam/link`, `GET /steam/me` y, si hace falta, `DELETE /steam/link`.
   Usar `get_current_user` de auth para que solo un usuario logueado pueda vincular o ver su SteamID.
   Registrar el router en `app/bootstrap/app_factory.py` y definir schemas Pydantic para requests/responses.

5. Preparar el diseno para juegos y ownership futuro.
   Crear una tarea posterior para tablas `steam_games` y `user_steam_games`, usando `appid` como identificador externo.
   Guardar datos minimos al inicio: `appid`, nombre opcional, estado de ownership, fecha de ultima comprobacion y fuente Steam.
   La comprobacion debe vivir en el modulo `steam`, no en `users`, para mantener separada la identidad interna de los datos de plataforma.

6. Cubrir integracion con tests y dobles de Steam.
   Anadir tests unitarios para el servicio de vinculacion usando un fake del `SteamClient`, sin llamar a la API real.
   Probar casos: ticket valido, ticket invalido, SteamID duplicado, usuario ya vinculado y respuesta correcta del endpoint.
   Dejar la API real solo para pruebas manuales o integracion controlada con variables de entorno configuradas.

## Tests unitarios

### Pasos

1. Crear la estructura base de tests.
   Anadir una carpeta `tests/` con subcarpetas por modulo: `tests/auth`, `tests/users` y `tests/steam`.
   Configurar `pytest.ini` para que descubra archivos `test_*.py` y pueda importar `app` desde la raiz del proyecto.
   Mantener los tests de aplicacion sin base de datos real siempre que sea posible.

2. Preparar fakes y fixtures reutilizables.
   Crear fakes en memoria para repositorios como `UserRepository` y, despues, el repositorio de Steam.
   Crear un fake de `SteamClient` que devuelva SteamID64 valido, ticket invalido o errores controlados segun el caso.
   Anadir fixtures para usuarios activos, usuarios inactivos, usuarios por rol, hashes de password y tokens JWT si se prueban endpoints.

3. Probar casos de uso de auth y users.
   Cubrir registro correcto, username duplicado, login correcto, password incorrecta y usuario inactivo.
   Verificar que `RegisterUser` hashea la password y que `LoginUser` devuelve token solo con credenciales validas.
   Probar que el registro asigna `role=user` por defecto y que los mappers conservan el rol.

4. Probar casos de uso de Steam.
   Cubrir vinculacion correcta con ticket valido y persistencia del `steam_id_64`.
   Cubrir ticket invalido, usuario ya vinculado y SteamID ya asociado a otro usuario.
   Cubrir consulta de cuenta Steam vinculada y ausencia de vinculacion para un usuario sin Steam.

5. Probar endpoints con dependencias sustituidas.
   Usar `TestClient` de FastAPI y overrides de dependencias para evitar base de datos y llamadas reales a Steam.
   Cubrir `POST /steam/link`, `GET /steam/me`, `DELETE /steam/link` si se implementa y `/auth/me` para autenticacion.
   Verificar codigos HTTP esperados: `200/201`, `400`, `401`, `403`, `404` y `409` segun el flujo.

6. Ejecutar y mantener la suite.
   Comando esperado: `pytest`.
   Los tests unitarios no deben requerir `STEAM_WEB_API_KEY`, red, Docker ni MySQL.
   Si se anaden tests de integracion reales, separarlos con marks como `integration` y documentar variables necesarias.

### Tareas

1. Anadir configuracion minima de pytest.
   Completar `pytest.ini` con `testpaths = tests` y patrones de descubrimiento.
   Revisar si hace falta `pythonpath = .` para importar los modulos del backend.
   Dejar preparada una marca `integration` para pruebas que no sean unitarias.

2. Crear tests de auth actuales.
   Implementar tests para `RegisterUser` y `LoginUser` usando un repositorio fake.
   Evitar tocar la base de datos real y validar errores de dominio, no solo respuestas felices.
   Estos tests protegen el flujo actual antes de tocar Steam o roles.

3. Crear tests de roles y autorizacion.
   Probar usuarios `user`, `admin` y `super_admin` con dependencias de autorizacion.
   Verificar que `admin` no accede a acciones exclusivas de `super_admin`.
   Verificar que un usuario inactivo no accede aunque tenga rol elevado.

4. Crear tests del modulo Steam antes de exponer API real.
   Definir tests para el servicio de vinculacion con un `SteamClient` fake.
   Confirmar que el servicio no guarda nada si Steam rechaza el ticket.
   Confirmar que los constraints de negocio devuelven errores claros para la capa HTTP.

5. Crear tests de rutas Steam con overrides.
   Usar `app.dependency_overrides` para simular usuario actual, repositorio y cliente Steam.
   Validar payloads de entrada/salida y codigos HTTP.
   Confirmar que un usuario no autenticado no puede vincular ni consultar Steam.

6. Anadir tests de repositorio solo si se decide probar persistencia.
   Si se prueba SQLAlchemy, usar una base temporal y migraciones controladas.
   Probar unicidad de `user_id` y `steam_id_64` en `user_steam_accounts`.
   Mantener estos tests separados de los unitarios puros para que la suite rapida siga siendo estable.

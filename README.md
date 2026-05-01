# Siguiente Lista de Trabajo

## Arrancar en desarrollo

docker compose -f docker-compose.yml -f docker-compose.dev.yml up

## Tests unitarios

### Pasos

1. Crear la estructura base de tests.
   Anadir una carpeta `tests/` con subcarpetas por modulo: `tests/auth`, `tests/users` y `tests/steam`.
   Configurar `pytest.ini` para que descubra archivos `test_*.py` y pueda importar `app` desde la raiz del proyecto.
   Mantener los tests de aplicacion sin base de datos real siempre que sea posible.

2. Preparar fakes y fixtures reutilizables.
   Crear fakes en memoria para repositorios como `UserRepository` y, despues, el repositorio de Steam.
   Crear un fake de `SteamClient` que resuelva vanity URLs, devuelva perfiles publicos o errores controlados segun el caso.
   Anadir fixtures para usuarios activos, usuarios inactivos, usuarios por rol, hashes de password y tokens JWT si se prueban endpoints.

3. Probar casos de uso de auth y users.
   Cubrir registro correcto, username duplicado, login correcto, password incorrecta y usuario inactivo.
   Verificar que `RegisterUser` hashea la password y que `LoginUser` devuelve token solo con credenciales validas.
   Probar que el registro asigna `role=user` por defecto y que los mappers conservan el rol.

4. Probar casos de uso de Steam.
   Cubrir vinculacion correcta con SteamID64 directo y persistencia del `steam_id_64`.
   Cubrir vinculacion correcta con vanity URL resuelta por Steam.
   Cubrir usuario Steam inexistente, usuario ya vinculado y SteamID ya asociado a otro usuario.
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
   Confirmar que el servicio no guarda nada si Steam no encuentra el usuario o devuelve un error.
   Confirmar que los constraints de negocio devuelven errores claros para la capa HTTP.

5. Crear tests de rutas Steam con overrides.
   Usar `app.dependency_overrides` para simular usuario actual, repositorio y cliente Steam.
   Validar payloads de entrada/salida y codigos HTTP.
   Confirmar que un usuario no autenticado no puede vincular ni consultar Steam.

6. Anadir tests de repositorio solo si se decide probar persistencia.
   Si se prueba SQLAlchemy, usar una base temporal y migraciones controladas.
   Probar unicidad de `user_id` y `steam_id_64` en `user_steam_accounts`.
   Mantener estos tests separados de los unitarios puros para que la suite rapida siga siendo estable.

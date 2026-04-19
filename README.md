
# Siguiente Lista De Trabajo

Confirmar que la base local está limpia

Como borraste la migración anterior y creaste una nueva, asegúrate de que MySQL no tenga todavía registrada la versión vieja en alembic_version.

Si no tienes datos importantes, lo más simple es resetear el volumen de Docker antes de levantar todo.

Levantar Docker y comprobar que Alembic aplica la migración

Tu docker-compose.yml ya ejecuta alembic upgrade head al iniciar la API.
No tienes que ejecutar Alembic manualmente para aplicar la migración si arrancas el servicio api.

Verificar que la tabla users se crea bien

Después de levantar Docker, comprueba que existe la tabla users y que no existe user.

Limpiar detalles de estilo en models.py, user.py, ports.py y mappers.py

No es urgente, pero antes de seguir conviene dejar imports ordenados, líneas en blanco entre clases/funciones, y el mapped_column del id más legible.

Decidir si password_hash puede ser opcional en dominio

En base de datos ya es obligatorio.
Yo lo dejaría también como obligatorio en User y UserCreate, porque auth sin email va a depender totalmente de username + password.

Implementar el repositorio SQLAlchemy de usuarios

Este es el siguiente paso real.
Debe implementar el puerto UserRepository.

Métodos mínimos:

buscar usuario por id
buscar usuario por username
crear usuario
quizá actualizar last_login_at más adelante
Crear dependencia de sesión de base de datos

Necesitas una dependencia tipo get_db para abrir/cerrar sesiones SQLAlchemy en FastAPI.

Preparar wiring simple de usuarios

En users/wiring.py puedes crear funciones que construyan el repositorio usando la sesión de DB.

Implementar PasswordHasher

Usando bcrypt/passlib, porque ya lo tienes en requirements.

Implementar RegisterUser

Registro sin email:

recibe username y password
comprueba si el username ya existe
hashea password
crea UserCreate
guarda con el repositorio
devuelve usuario público
Implementar LoginUser
Login sin email:

busca por username
valida password
comprueba is_active
genera JWT
opcionalmente actualiza last_login_at
Implementar JwtService
JWT simple con:

sub: UUID del usuario
username
exp
algoritmo desde settings
secret desde settings
Crear dependencia get_current_user
Esta será la pieza para validar JWT en rutas protegidas.

Crear rutas mínimas de auth
Para tu caso:

POST /auth/register
POST /auth/login
GET /auth/me
Registrar routers en create_app
Ahora app_factory.py (line 3) solo tiene /health.
Cuando tengas rutas, toca registrar auth y luego users.

Probar flujo completo
Flujo mínimo:

arranca Docker
migración crea tabla
register crea usuario
login devuelve token
/auth/me acepta token
/auth/me rechaza token inválido o ausente

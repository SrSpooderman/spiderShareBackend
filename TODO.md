# TODO - siguientes tareas

## Modulo de videos

Objetivo inicial: anadir un sistema de videos donde cada video quede relacionado con el usuario que lo sube.

Estado actual:

- Existe `VIDEO_STORAGE_PATH`.
- Docker ya reserva almacenamiento para videos.
- Existe la carpeta `storage/videos`.
- Existe el placeholder `app/shared/infrastructure/providers/storage/video_storage.py`.
- Todavia no existe modulo `app/modules/videos`.

## Decisiones pendientes

Antes de implementar, hay que concretar estas reglas:

1. Propiedad y permisos.
   - Un video pertenece a un usuario uploader.
   - Falta decidir si otros usuarios pueden verlo.
   - Falta decidir si habra videos publicos, privados o compartidos.
   - Falta decidir que pueden hacer `admin` y `super_admin`.

2. Metadata del video.
   - Campos minimos posibles:
     - `id`
     - `uploader_user_id`
     - `title`
     - `description`
     - `filename`
     - `storage_path`
     - `mime_type`
     - `size_bytes`
     - `duration_seconds`
     - `visibility`
     - `created_at`
     - `updated_at`
   - Falta decidir cuales son obligatorios desde la primera version.

3. Archivo y almacenamiento.
   - Falta definir tamano maximo.
   - Falta definir formatos permitidos: por ejemplo `mp4`, `webm`, `mov`.
   - Falta decidir si se guarda el nombre original.
   - Falta decidir si se generan nombres internos con UUID.
   - Falta decidir si se sirve el archivo desde FastAPI o desde otro servicio.

4. Procesamiento.
   - Falta decidir si habra validacion real de duracion/formato.
   - Falta decidir si se generaran thumbnails.
   - Falta decidir si habra transcodificacion.
   - Falta decidir si el upload sera directo o por chunks.

5. API.
   - Endpoints candidatos:
     - `POST /videos`
     - `GET /videos`
     - `GET /videos/{video_id}`
     - `GET /videos/{video_id}/stream`
     - `PATCH /videos/{video_id}`
     - `DELETE /videos/{video_id}`
   - Falta decidir payloads y respuestas.

## Plan tecnico propuesto

1. Crear estructura del modulo.

```text
app/modules/videos/
  domain/
    video.py
    ports.py
  application/
    upload_video.py
    list_videos.py
    get_video.py
    delete_video.py
  entrypoints/
    routes.py
    schemas.py
  infrastructure/
    models.py
    mappers.py
    repository.py
  wiring.py
```

2. Definir dominio.
   - Crear entidad `Video`.
   - Crear entidad `VideoCreate`.
   - Crear enum de visibilidad si aplica: `private`, `public`, `unlisted`.
   - Crear puerto `VideoRepository`.
   - Crear puerto `VideoStorage`.

3. Crear infraestructura.
   - Modelo SQLAlchemy `VideoModel`.
   - Mapper model/domain.
   - Repositorio SQLAlchemy.
   - Implementacion local de storage usando `VIDEO_STORAGE_PATH`.

4. Crear casos de uso.
   - `UploadVideo`: valida usuario, metadata y archivo.
   - `ListVideos`: lista videos visibles para el usuario actual.
   - `GetVideo`: obtiene metadata si hay permiso.
   - `DeleteVideo`: borra metadata y archivo si hay permiso.

5. Crear rutas FastAPI.
   - Subida con `UploadFile`.
   - Listado de videos.
   - Consulta de metadata.
   - Descarga o streaming.
   - Borrado.

6. Crear migracion Alembic.
   - Tabla `videos`.
   - Foreign key a `users.id`.
   - Indices por `uploader_user_id` y `created_at`.

7. Crear tests.
   - Unitarios de dominio.
   - Unitarios de casos de uso con fakes.
   - Tests de storage local usando directorio temporal.
   - Tests HTTP con `TestClient`.
   - Integracion de repositorio si hace falta.

## Primera version minima sugerida

Para empezar sin bloquearse:

- Cada video pertenece a un usuario.
- Solo el uploader, `admin` o `super_admin` pueden verlo.
- Formato permitido: `video/mp4`.
- Tamano maximo: pendiente de decidir.
- Guardado local en `VIDEO_STORAGE_PATH`.
- Nombre interno: `{video_id}.mp4`.
- Metadata inicial:
  - `id`
  - `uploader_user_id`
  - `title`
  - `description`
  - `storage_path`
  - `mime_type`
  - `size_bytes`
  - `created_at`
  - `updated_at`

## Preguntas para cerrar antes de implementar

1. Que limite de tamano tendra un video?
2. Que formatos se aceptan?
3. Los videos seran privados por defecto?
4. Otros usuarios podran ver videos ajenos?
5. Hace falta streaming/range requests desde el primer dia?
6. Hace falta thumbnail?
7. Hace falta borrar el archivo fisico cuando se borra el registro?
8. Hace falta editar titulo/descripcion despues de subir?
9. Hace falta paginacion en `GET /videos`?
10. Hace falta asociar videos con Steam/juegos en el futuro?

# App Música Personal — Backend

Backend en FastAPI + SQLite para tu app de música personal, usando `yt-dlp` como fuente (búsqueda, streaming y descarga).

## Requisitos

- Python 3.10 o superior
- **ffmpeg** instalado en el sistema (necesario para convertir audio a Opus)
  - Windows: `winget install ffmpeg` (o descárgalo de https://ffmpeg.org/download.html y agrégalo al PATH)
  - Linux: `sudo apt install ffmpeg`
  - Mac: `brew install ffmpeg`

## Instalación

```bash
cd app-musica-backend
python3 -m venv venv

# Activar entorno virtual
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
```

## Correr el servidor

```bash
uvicorn app.main:app --reload
```

Se abre en: http://localhost:8000
Documentación interactiva (Swagger, para probar todo desde el navegador): http://localhost:8000/docs
**Interfaz visual (frontend): http://localhost:8000/app/**

La base de datos `musica.db` se crea sola la primera vez que corres el servidor.

## Endpoints principales

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/music/search?q=texto&limit=10` | Busca canciones en YouTube |
| GET | `/music/stream/{video_id}` | Redirige a URL de audio para reproducir sin descargar |
| POST | `/music/download/{video_id}?title=..&artist=..` | Descarga el audio (Opus 128kbps) y lo guarda en tu biblioteca |
| POST | `/music/library/add?video_id=..&title=..&artist=..` | Guarda una canción en tu biblioteca sin descargarla |
| GET | `/music/library/downloaded` | Lista solo las canciones ya descargadas |
| GET | `/music/file/{video_id}` | Sirve el archivo de audio descargado |
| GET | `/songs/` | Lista toda tu biblioteca |
| DELETE | `/songs/{song_id}` | Elimina una canción de la biblioteca |

## Flujo típico de uso

1. Buscas: `GET /music/search?q=nombre+cancion` → te devuelve una lista con `external_id` (el video_id de YouTube), título, artista, duración, miniatura.
2. Para reproducir sin guardar: `GET /music/stream/{video_id}` → te redirige a la URL de audio directa.
3. Para guardar en tu biblioteca (sin descargar el archivo): `POST /music/library/add` con esos datos.
4. Para descargarla de verdad al disco: `POST /music/download/{video_id}` (los archivos quedan en la carpeta `downloads/`).

## Estructura del proyecto

```
app/
  main.py              → punto de entrada
  config.py            → variables de entorno
  database.py          → conexión SQLite
  schemas.py           → validación de datos (Pydantic)
  models/models.py     → tablas: songs, playlists, favorites
  routers/songs.py     → CRUD de biblioteca
  routers/music.py     → búsqueda, streaming, descarga (yt-dlp)
  services/music_service.py → lógica de yt-dlp
```

## Frontend

La interfaz ya está incluida en `frontend/index.html` y se sirve automáticamente en **http://localhost:8000/app/** al correr el backend — no necesitas otro servidor.

Tiene: buscador, pestañas de Búsqueda / Biblioteca / Descargadas, reproductor con barra de progreso tipo waveform, y botones para guardar y descargar canciones. Diseño oscuro con acento verde, optimizado para móvil (se ve bien también en portátil).

Si luego empacas esto en una APK con Capacitor y el backend no vive en `localhost`, cambia la URL en la consola del navegador:
```js
localStorage.setItem('api_base', 'https://tu-backend-en-la-nube.com')
```

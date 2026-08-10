# Guía: Backend en la nube (Render) + APK con Capacitor

## Parte 1 — Subir el backend a Render

### 1. Sube tu proyecto backend a GitHub
Si no tienes el repo aún:
```powershell
cd app-musica-backend
git init
git add .
git commit -m "Backend inicial"
```
Crea un repositorio nuevo en https://github.com/new (puede ser privado) y sigue las instrucciones de GitHub para conectarlo y hacer push.

### 2. Crea el servicio en Render
1. Entra a https://render.com y crea una cuenta (puedes usar tu cuenta de GitHub).
2. Click en **New +** → **Web Service**.
3. Conecta tu repositorio de GitHub.
4. Render detectará el `Dockerfile` automáticamente — déjalo usar Docker (no elijas "Python" manualmente).
5. Configura:
   - **Name**: `frecuencia-backend` (o el que quieras)
   - **Instance type**: Free
6. Click **Create Web Service**.

Render construirá la imagen (con ffmpeg incluido) y te dará una URL como:
```
https://frecuencia-backend.onrender.com
```

### ⚠️ Importante: capa gratuita de Render
- El servicio se "duerme" tras ~15 min sin uso; la primera petición después tarda unos segundos en responder mientras despierta.
- El almacenamiento es **efímero**: los archivos descargados en `downloads/` se borran cada vez que el servicio se reinicia o se redepliega. Para descargas persistentes necesitarías un "Persistent Disk" (de pago) o guardar los audios en un servicio externo (ej. Cloudinary, S3). Por ahora, el streaming (sin descargar) funciona siempre igual de bien.

### 3. Prueba que responde
Abre en el navegador: `https://frecuencia-backend.onrender.com/health` — debe responder `{"status":"healthy"}`.

---

## Parte 2 — Configurar el frontend para usar el backend en la nube

Ya tienes el proyecto de Capacitor en `app-musica-mobile/`, con tu `index.html` copiado dentro de `www/`.

Abre `app-musica-mobile/www/index.html`, busca esta línea (cerca del inicio del `<script>`):
```js
const API_BASE = localStorage.getItem('api_base') || 'http://localhost:8000';
```
Cámbiala por tu URL de Render:
```js
const API_BASE = localStorage.getItem('api_base') || 'https://frecuencia-backend.onrender.com';
```

---

## Parte 3 — Compilar la APK

Necesitas **Android Studio** instalado (gratis): https://developer.android.com/studio

```powershell
cd app-musica-mobile
npm install
npx cap sync android
npx cap open android
```

Esto abre Android Studio con el proyecto. Ahí:
1. Espera que termine de sincronizar Gradle (barra de progreso abajo).
2. Menú **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**.
3. Cuando termine, aparece un aviso abajo a la derecha: click en **locate** para encontrar el archivo `.apk`.

Ese `.apk` lo puedes pasar directo a tu Poco X7 Pro (por cable, WhatsApp, Drive, etc.) e instalarlo. Puede que Android te pida habilitar "Instalar apps de fuentes desconocidas" la primera vez.

---

## Resumen del flujo completo
1. Backend corriendo en Render (accesible desde cualquier lugar).
2. `index.html` apuntando a esa URL.
3. Capacitor empaca ese `index.html` como app Android nativa.
4. Compilas la APK en Android Studio e instalas en tu celular.

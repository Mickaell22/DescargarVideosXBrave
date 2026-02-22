<div align="center">

# 🎬 Descargador de Videos

### Descarga videos de tus redes sociales favoritas con un solo click

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-red?style=for-the-badge&logo=youtube&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-green?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-compatible-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/macOS-compatible-000000?style=for-the-badge&logo=apple&logoColor=white)

</div>


---

## ✨ Características

- 🖥️ **Interfaz moderna** con tema oscuro (CustomTkinter)
- 📋 **Cola de descargas** — agrega múltiples URLs y descárgalas en secuencia
- 🔍 **Info previa del video** — ve título, autor y duración antes de descargar
- 📁 **Explorador de carpetas** — selecciona el destino sin escribir rutas
- 📂 **Abrir carpeta** — accede a tus descargas con un click al terminar
- 📜 **Historial de descargas** — registro de todos los videos descargados
- ⚠️ **Anti-duplicados** — aviso si intentas descargar un video ya descargado
- 📊 **Barra de progreso** en tiempo real
- 🍪 **Soporte de cookies** para videos privados (Facebook, Instagram)

---

## 🌐 Plataformas Soportadas

<div align="center">

| Plataforma | Videos Públicos | Videos Privados |
|:---:|:---:|:---:|
| ![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=flat&logo=youtube&logoColor=white) | ✅ | ❌ |
| ![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=flat&logo=facebook&logoColor=white) | ✅ | ✅ (con cookies) |
| ![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=flat&logo=instagram&logoColor=white) | ✅ | ✅ (con cookies) |
| ![TikTok](https://img.shields.io/badge/TikTok-000000?style=flat&logo=tiktok&logoColor=white) | ✅ | ❌ |
| ![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=flat&logo=twitter&logoColor=white) | ✅ | ❌ |
| Reddit, Vimeo y +1000 sitios más | ✅ | — |

</div>

---

## 🚀 Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/DescargarVideos.git
cd DescargarVideos
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecuta la app

```bash
python video_downloader.py
```

> **Linux:** Asegúrate de tener `xdg-utils` instalado (`sudo apt install xdg-utils`) para que el botón "Abrir carpeta" funcione.
> **macOS:** No requiere dependencias adicionales.

---

## 🎮 Cómo Usar

### Descarga Simple
1. Pega la URL del video en el campo de entrada
2. Haz click en **"Ver Info"** para previsualizar el video *(opcional)*
3. Selecciona la **calidad** deseada
4. Elige la **carpeta de destino** con el explorador 📁
5. Presiona **"Agregar a Cola"** o **"Descargar Video"**

### Cola de Descargas
1. Pega la primera URL y haz click en **"Agregar a Cola"**
2. Repite con todas las URLs que quieras
3. Presiona **"Iniciar Cola"** para descargar todas en secuencia

### Videos Privados (Facebook / Instagram)
> ⚠️ Requiere estar autenticado en el navegador

1. **Inicia sesión** en Facebook/Instagram desde **Brave**
2. **Cierra completamente** Brave (todas las ventanas)
3. Selecciona **"Usar cookies de Brave: si"**
4. Pega la URL y descarga

---

## ⚙️ Opciones de Calidad

| Opción | Resolución | Recomendado para |
|:---:|:---:|:---|
| `best` | Hasta 4K | Máxima calidad, archivos grandes |
| `720p` | HD | Equilibrio calidad/tamaño |
| `480p` | SD | Conexiones lentas |
| `360p` | Baja | Ahorro de espacio |

---

## 🔧 Solución de Problemas

<details>
<summary><b>❌ Error: "Could not copy cookie database"</b></summary>

**Causa:** Brave está abierto mientras se intenta acceder a las cookies.

**Solución:**
1. Cierra **completamente** Brave (todas las ventanas)
2. Intenta descargar de nuevo
3. O cambia "Usar cookies" a **"no"** (solo para videos públicos)

</details>

<details>
<summary><b>❌ Error: "Cannot parse data" o "Unsupported URL"</b></summary>

**Causas posibles:**
- Video privado o restringido
- URL incorrecta o expirada
- Estructura de la plataforma cambió

**Solución:**
1. Verifica que puedas ver el video en tu navegador
2. Para videos privados: inicia sesión → cierra Brave → usa cookies
3. Actualiza yt-dlp: `pip install --upgrade yt-dlp`

</details>

<details>
<summary><b>❌ Error: "No video formats found"</b></summary>

- El video puede estar protegido o ser solo una imagen
- Prueba con una calidad diferente
- Verifica que el enlace sea correcto

</details>

<details>
<summary><b>❌ El programa no inicia</b></summary>

```bash
pip install -r requirements.txt
python video_downloader.py
```

Verifica que tengas Python 3.7 o superior instalado.

</details>

---

## 🛠️ Tecnologías

| Librería | Uso |
|:---:|:---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Interfaz gráfica moderna con tema oscuro |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Motor de descarga (soporte +1000 sitios) |
| `threading` | Descargas sin bloquear la interfaz |
| `json` | Historial de descargas persistente |
| `tkinter.filedialog` | Explorador de carpetas nativo |

---

## 📋 URLs de Ejemplo

```
YouTube:   https://www.youtube.com/watch?v=dQw4w9WgXcQ
Facebook:  https://www.facebook.com/watch?v=123456789
Instagram: https://www.instagram.com/reel/ABC123/
TikTok:    https://www.tiktok.com/@usuario/video/123456789
Twitter:   https://twitter.com/usuario/status/123456789
```

---

## 📜 Licencia

Este proyecto es de código abierto y está disponible para uso **personal y educativo**.

---

<div align="center">

Adaptado por MICKAEL22 | Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)

</div>

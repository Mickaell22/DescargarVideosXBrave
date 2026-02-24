# ── Imports ligeros primero ────────────────────────────────────────────────
import tkinter as tk
import threading
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog


# ── Splash inmediata (aparece antes de cargar los módulos pesados) ─────────
def _show_splash():
    s = tk.Tk()
    s.overrideredirect(True)
    s.configure(bg="#1c1c1c")
    w, h = 380, 130
    sw, sh = s.winfo_screenwidth(), s.winfo_screenheight()
    s.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    s.attributes("-topmost", True)
    tk.Label(s, text="🎬  Descargador de Videos",
             bg="#1c1c1c", fg="white",
             font=("Arial", 17, "bold")).pack(pady=(26, 6))
    tk.Label(s, text="Iniciando, un momento...",
             bg="#1c1c1c", fg="#888888",
             font=("Arial", 10)).pack()
    s.update()
    return s


_splash_win = _show_splash()

# ── Imports pesados (se cargan mientras la splash está visible) ────────────
import customtkinter as ctk  # noqa: E402
import yt_dlp                # noqa: E402


HISTORY_FILE = Path(__file__).parent / "download_history.json"


class MyLogger:
    """Logger personalizado para yt-dlp"""
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def debug(self, msg):
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        self.log_callback(msg)

    def warning(self, msg):
        self.log_callback(f"⚠️ {msg}")

    def error(self, msg):
        self.log_callback(f"✗ {msg}")


class VideoDownloaderApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Descargador de Videos - Redes Sociales")
        self.window.geometry("750x850")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.download_path = str(Path.home() / "Downloads" / "MisVideos")
        self.create_download_folder()

        self.is_downloading = False
        self.download_queue = []        # Lista de URLs en cola
        self.queue_running = False      # Si la cola está corriendo

        self.history = self.load_history()

        self.create_widgets()

        # Cerrar splash cuando la ventana principal está lista
        _splash_win.destroy()

    # ─────────────────────────────────────────────
    #  Carpeta & paths
    # ─────────────────────────────────────────────

    def create_download_folder(self):
        Path(self.download_path).mkdir(parents=True, exist_ok=True)

    def browse_folder(self):
        """Abrir explorador de carpetas para elegir destino"""
        folder = filedialog.askdirectory(
            title="Selecciona la carpeta de destino",
            initialdir=self.path_entry.get() or self.download_path
        )
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def open_download_folder(self):
        """Abrir la carpeta de descargas en el explorador (multiplataforma)"""
        path = self.path_entry.get().strip() or self.download_path
        if not os.path.exists(path):
            messagebox.showwarning("Carpeta no encontrada", f"La carpeta no existe:\n{path}")
            return
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    # ─────────────────────────────────────────────
    #  Historial
    # ─────────────────────────────────────────────

    def load_history(self):
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_to_history(self, url, title, uploader, duration):
        entry = {
            "url": url,
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        # Evitar duplicados exactos en el historial
        self.history = [h for h in self.history if h["url"] != url]
        self.history.insert(0, entry)
        self.history = self.history[:100]   # Máximo 100 entradas
        self.save_history()
        self.refresh_history_list()

    def is_duplicate(self, url):
        """Comprueba si la URL ya fue descargada antes"""
        return any(h["url"] == url for h in self.history)

    def refresh_history_list(self):
        """Actualizar la lista de historial en la UI"""
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        if not self.history:
            self.history_text.insert("end", "  Sin descargas aún\n")
        else:
            for h in self.history[:20]:
                dur = ""
                if h.get("duration"):
                    m, s = divmod(int(h["duration"]), 60)
                    dur = f"  [{m}m{s:02d}s]"
                self.history_text.insert(
                    "end",
                    f"• {h['date']}  —  {h['title'][:45]}{dur}\n"
                )
        self.history_text.configure(state="disabled")

    # ─────────────────────────────────────────────
    #  Cola de descargas
    # ─────────────────────────────────────────────

    def add_to_queue(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Por favor ingresa una URL válida")
            return

        if url in self.download_queue:
            messagebox.showwarning("Ya en cola", "Esa URL ya está en la cola de descargas")
            return

        self.download_queue.append(url)
        self.url_entry.delete(0, "end")
        self.refresh_queue_list()
        self.add_log(f"+ URL agregada a la cola ({len(self.download_queue)} en total)")

    def remove_from_queue(self):
        """Eliminar la URL seleccionada de la cola"""
        selected = self.queue_listbox.curselection()
        if not selected:
            return
        idx = selected[0]
        if idx < len(self.download_queue):
            removed = self.download_queue.pop(idx)
            self.add_log(f"- Eliminado de la cola: {removed[:60]}...")
            self.refresh_queue_list()

    def refresh_queue_list(self):
        self.queue_listbox.delete(0, "end")
        for i, url in enumerate(self.download_queue, 1):
            short = url if len(url) <= 70 else url[:67] + "..."
            self.queue_listbox.insert("end", f"{i}. {short}")
        self.queue_count_label.configure(
            text=f"Cola: {len(self.download_queue)} video(s)"
        )

    def start_queue(self):
        if self.queue_running:
            messagebox.showwarning("Cola activa", "Ya hay una cola en ejecución")
            return
        if not self.download_queue:
            messagebox.showwarning("Cola vacía", "Agrega URLs a la cola primero")
            return

        output_path = self.path_entry.get().strip()
        if not output_path:
            messagebox.showwarning("Ruta vacía", "Especifica la carpeta de destino")
            return
        try:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta: {e}")
            return

        # Leer StringVars en el hilo principal antes de pasarlos al hilo de cola
        quality     = self.quality_var.get()
        use_cookies = self.use_cookies_var.get()

        self.queue_running = True
        self.start_queue_btn.configure(state="disabled", text="Ejecutando cola...")
        thread = threading.Thread(target=self._run_queue, args=(output_path, quality, use_cookies), daemon=True)
        thread.start()

    def _run_queue(self, output_path, quality, use_cookies):
        total = len(self.download_queue)
        self.add_log(f"\n▶ Iniciando cola: {total} video(s)\n")

        while self.download_queue:
            url = self.download_queue[0]
            self.add_log(f"\n[Cola] {len(self.download_queue)} restante(s) — {url[:60]}")
            self.download_video(url, output_path, quality, use_cookies, silent=True)
            # Quitar de la cola solo si descargó (o falló)
            if self.download_queue and self.download_queue[0] == url:
                self.download_queue.pop(0)
            self.window.after(0, self.refresh_queue_list)

        self.queue_running = False
        self.window.after(0, lambda: self.start_queue_btn.configure(
            state="normal", text="▶ Iniciar Cola"
        ))
        self.add_log("\n✓ Cola finalizada")

    # ─────────────────────────────────────────────
    #  Info del video antes de descargar
    # ─────────────────────────────────────────────

    def fetch_video_info(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Ingresa una URL primero")
            return
        self.info_btn.configure(state="disabled", text="Consultando...")
        self.add_log(f"\nConsultando info de: {url[:60]}...")
        thread = threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True)
        thread.start()

    def _fetch_info_thread(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        if self.use_cookies_var.get() == "si":
            ydl_opts['cookiesfrombrowser'] = ('brave',)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title    = info.get('title', 'Sin título')
            uploader = info.get('uploader', 'Desconocido')
            duration = info.get('duration', 0)
            views    = info.get('view_count')
            platform = self.detectar_plataforma(url).upper()

            dur_str = ""
            if duration:
                m, s = divmod(int(duration), 60)
                dur_str = f"{m}m {s:02d}s"

            lines = [
                "",
                "┌─ INFO DEL VIDEO ───────────────────────",
                f"│ Título:    {title[:55]}",
                f"│ Autor:     {uploader}",
                f"│ Duración:  {dur_str or 'N/A'}",
                f"│ Plataforma:{platform}",
            ]
            if views:
                lines.append(f"│ Vistas:    {views:,}")
            lines.append("└────────────────────────────────────────")
            lines.append("")

            for line in lines:
                self.add_log(line)

        except Exception as e:
            self.add_log(f"✗ No se pudo obtener info: {e}")
        finally:
            self.window.after(0, lambda: self.info_btn.configure(
                state="normal", text="Ver Info"
            ))

    # ─────────────────────────────────────────────
    #  Widgets
    # ─────────────────────────────────────────────

    def create_widgets(self):
        # ── Título ──
        ctk.CTkLabel(
            self.window,
            text="Descargador de Videos",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 0))

        ctk.CTkLabel(
            self.window,
            text="Soporta: YouTube, Facebook, Instagram, TikTok, Twitter, y más",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(4, 10))

        # ── URL ──
        url_frame = ctk.CTkFrame(self.window)
        url_frame.pack(pady=8, padx=20, fill="x")

        ctk.CTkLabel(url_frame, text="URL del Video:").pack(pady=(8, 2))

        url_row = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_row.pack(fill="x", padx=10, pady=(0, 8))

        self.url_entry = ctk.CTkEntry(
            url_row,
            placeholder_text="Pega aquí la URL del video...",
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.info_btn = ctk.CTkButton(
            url_row,
            text="Ver Info",
            width=90,
            command=self.fetch_video_info
        )
        self.info_btn.pack(side="left")

        # ── Opciones (calidad + cookies) ──
        opts_frame = ctk.CTkFrame(self.window)
        opts_frame.pack(pady=8, padx=20, fill="x")

        # Calidad
        ctk.CTkLabel(opts_frame, text="Calidad:").pack(side="left", padx=(10, 4))
        self.quality_var = ctk.StringVar(value="best")
        ctk.CTkOptionMenu(
            opts_frame,
            values=["best", "720p", "480p", "360p"],
            variable=self.quality_var,
            width=110
        ).pack(side="left", padx=(0, 20))

        # Cookies
        ctk.CTkLabel(opts_frame, text="Cookies de Brave:").pack(side="left", padx=(0, 4))
        self.use_cookies_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(
            opts_frame,
            values=["si", "no"],
            variable=self.use_cookies_var,
            width=80
        ).pack(side="left")

        ctk.CTkLabel(
            opts_frame,
            text="(cierra Brave si hay error)",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        ).pack(side="left", padx=8)

        # ── Carpeta de destino ──
        path_frame = ctk.CTkFrame(self.window)
        path_frame.pack(pady=8, padx=20, fill="x")

        ctk.CTkLabel(path_frame, text="Carpeta de destino:").pack(pady=(8, 2))

        path_row = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_row.pack(fill="x", padx=10, pady=(0, 8))

        self.path_entry = ctk.CTkEntry(path_row)
        self.path_entry.insert(0, self.download_path)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            path_row,
            text="📁 Explorar",
            width=100,
            command=self.browse_folder
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            path_row,
            text="Abrir carpeta",
            width=110,
            command=self.open_download_folder
        ).pack(side="left")

        # ── Botones principales ──
        btn_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.download_button = ctk.CTkButton(
            btn_frame,
            text="⬇ Descargar Video",
            command=self.start_download,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
            width=200
        )
        self.download_button.pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="+ Agregar a Cola",
            command=self.add_to_queue,
            height=42,
            width=160
        ).pack(side="left", padx=8)

        # ── Cola de descargas ──
        queue_outer = ctk.CTkFrame(self.window)
        queue_outer.pack(pady=6, padx=20, fill="x")

        queue_header = ctk.CTkFrame(queue_outer, fg_color="transparent")
        queue_header.pack(fill="x", padx=8, pady=(6, 2))

        self.queue_count_label = ctk.CTkLabel(
            queue_header,
            text="Cola: 0 video(s)",
            font=ctk.CTkFont(weight="bold")
        )
        self.queue_count_label.pack(side="left")

        self.start_queue_btn = ctk.CTkButton(
            queue_header,
            text="▶ Iniciar Cola",
            command=self.start_queue,
            width=130,
            height=30
        )
        self.start_queue_btn.pack(side="right", padx=(0, 4))

        ctk.CTkButton(
            queue_header,
            text="✕ Quitar",
            command=self.remove_from_queue,
            width=80,
            height=30,
            fg_color="#555",
            hover_color="#444"
        ).pack(side="right", padx=(0, 4))

        # Listbox de la cola (usando Tkinter clásico con estilo oscuro)
        import tkinter as tk
        self.queue_listbox = tk.Listbox(
            queue_outer,
            height=4,
            bg="#2b2b2b",
            fg="#dcdcdc",
            selectbackground="#1f538d",
            selectforeground="white",
            borderwidth=0,
            highlightthickness=0,
            font=("Consolas", 10)
        )
        self.queue_listbox.pack(fill="x", padx=8, pady=(0, 8))

        # ── Barra de progreso ──
        self.progress_bar = ctk.CTkProgressBar(self.window, width=680)
        self.progress_bar.pack(pady=(8, 0))
        self.progress_bar.set(0)

        # ── Log ──
        ctk.CTkLabel(self.window, text="Estado:").pack(pady=(6, 0))
        self.log_text = ctk.CTkTextbox(self.window, width=700, height=120)
        self.log_text.pack(pady=(4, 0), padx=20)

        # ── Historial ──
        hist_frame = ctk.CTkFrame(self.window)
        hist_frame.pack(pady=8, padx=20, fill="x")

        ctk.CTkLabel(
            hist_frame,
            text="Historial de descargas:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(6, 2))

        self.history_text = ctk.CTkTextbox(hist_frame, width=700, height=100, state="disabled")
        self.history_text.pack(padx=8, pady=(0, 8))

        self.refresh_history_list()
        self.add_log("Listo para descargar videos")

    # ─────────────────────────────────────────────
    #  Log
    # ─────────────────────────────────────────────

    def add_log(self, message):
        def _update():
            self.log_text.insert("end", f"{message}\n")
            self.log_text.see("end")
        self.window.after(0, _update)

    # ─────────────────────────────────────────────
    #  Detección de plataforma
    # ─────────────────────────────────────────────

    def detectar_plataforma(self, url):
        url_lower = url.lower()
        if 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        return 'other'

    # ─────────────────────────────────────────────
    #  Progress hook
    # ─────────────────────────────────────────────

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                pct = d['downloaded_bytes'] / d['total_bytes']
                self.window.after(0, lambda p=pct: self.progress_bar.set(p))
            elif '_percent_str' in d:
                try:
                    pct = float(d['_percent_str'].strip().replace('%', '')) / 100
                    self.window.after(0, lambda p=pct: self.progress_bar.set(p))
                except Exception:
                    pass

            if '_percent_str' in d:
                speed = d.get('_speed_str', 'N/A')
                self.add_log(f"Descargando: {d['_percent_str']} - Velocidad: {speed}")

        elif d['status'] == 'finished':
            self.window.after(0, lambda: self.progress_bar.set(1))
            self.add_log("Descarga completada, procesando...")

    # ─────────────────────────────────────────────
    #  Descarga
    # ─────────────────────────────────────────────

    def download_video(self, url, output_path, quality, use_cookies, silent=False):
        try:
            plataforma = self.detectar_plataforma(url)
            self.add_log(f"Iniciando descarga desde: {url}")
            self.add_log(f"→ Plataforma detectada: {plataforma.upper()}")

            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s [%(uploader)s].%(ext)s'),
                'logger': MyLogger(self.add_log),
                'progress_hooks': [self.progress_hook],
                'merge_output_format': 'mp4',
                'postprocessor_args': {'ffmpeg': ['-c:a', 'aac']},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
                'extractor_retries': 3,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'ignoreerrors': False,
                'nocheckcertificate': False,
            }

            if use_cookies == "si":
                self.add_log("→ Usando cookies de Brave...")
                ydl_opts['cookiesfrombrowser'] = ('brave',)

            if quality == "best":
                if plataforma == 'youtube':
                    ydl_opts['format'] = 'bestvideo[height<=2160][protocol^=https]+bestaudio[protocol^=https]/best[height<=2160]/bestvideo+bestaudio/best'
                    self.add_log("→ Formato: YouTube optimizado (hasta 4K)")
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    self.add_log("→ Formato: Mejor calidad disponible")
            elif quality == "720p":
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                self.add_log("→ Formato: 720p")
            elif quality == "480p":
                ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
                self.add_log("→ Formato: 480p")
            elif quality == "360p":
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                self.add_log("→ Formato: 360p")

            if plataforma == 'facebook':
                self.add_log("→ Aplicando optimizaciones para Facebook...")
                ydl_opts['extractor_args'] = {'facebook': {'logged_in_tab': False}}
            elif plataforma == 'instagram':
                self.add_log("→ Aplicando optimizaciones para Instagram...")
                if use_cookies != "si":
                    self.add_log("  ⚠️ Consejo: Usa cookies para mejor compatibilidad")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.add_log("→ Extrayendo información del video...")
                info = ydl.extract_info(url, download=True)

                if info:
                    title    = info.get('title', 'Video sin título')
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Desconocido')

                    self.add_log("")
                    self.add_log(f"✓ ¡Descarga completada!")
                    self.add_log(f"  Título: {title}")
                    self.add_log(f"  Autor:  {uploader}")
                    if duration:
                        m, s = divmod(int(duration), 60)
                        self.add_log(f"  Duración: {m}m {s:02d}s")
                    self.add_log(f"  Guardado en: {output_path}")

                    # Guardar en historial
                    self.window.after(0, lambda: self.add_to_history(url, title, uploader, duration))

                    if not silent:
                        messagebox.showinfo(
                            "¡Éxito!",
                            f"Video descargado correctamente:\n\n{title}\n\nGuardado en:\n{output_path}"
                        )
                else:
                    raise Exception("No se pudo extraer información del video")

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            self.add_log("")
            self.add_log(f"✗ Error de descarga: {error_msg}")

            if "cookie" in error_msg.lower() or "could not copy" in error_msg.lower():
                self.add_log("")
                self.add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.add_log("⚠️  ERROR DE COOKIES")
                self.add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.add_log("1. CIERRA completamente Brave")
                self.add_log("2. Intenta descargar de nuevo")
                if not silent:
                    messagebox.showerror(
                        "Error de Cookies",
                        "El navegador Brave está abierto y bloqueó el acceso a las cookies.\n\n"
                        "SOLUCIÓN:\n"
                        "1. Cierra Brave completamente\n"
                        "2. Intenta de nuevo\n\n"
                        "O cambia 'Usar cookies' a 'no'"
                    )
            elif "Cannot parse data" in error_msg or "Unsupported URL" in error_msg:
                self.add_log("")
                self.add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.add_log("⚠️  NO SE PUEDE ACCEDER AL VIDEO")
                self.add_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                self.add_log("• Video privado, URL inválida, o necesitas autenticación")
                if not silent:
                    messagebox.showerror(
                        "Video no accesible",
                        "No se puede acceder a este video.\n\n"
                        "Verifica que:\n"
                        "• El video sea público O\n"
                        "• Estés usando cookies con sesión iniciada"
                    )
            else:
                if not silent:
                    messagebox.showerror("Error", f"Error al descargar:\n\n{error_msg}")

        except Exception as e:
            self.add_log(f"✗ Error inesperado: {e}")
            if not silent:
                messagebox.showerror("Error", f"Error inesperado:\n\n{e}")

        finally:
            self.is_downloading = False
            self.window.after(0, lambda: self.download_button.configure(
                state="normal", text="⬇ Descargar Video"
            ))
            self.window.after(0, lambda: self.progress_bar.set(0))

    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Descarga en progreso", "Ya hay una descarga en progreso")
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vacía", "Por favor ingresa una URL válida")
            return

        # ── Comprobación de duplicado ──
        if self.is_duplicate(url):
            respuesta = messagebox.askyesno(
                "Video ya descargado",
                "Esta URL ya fue descargada anteriormente.\n\n¿Deseas descargarla de nuevo?"
            )
            if not respuesta:
                return

        output_path = self.path_entry.get().strip()
        if not output_path:
            messagebox.showwarning("Ruta vacía", "Por favor especifica una carpeta de destino")
            return

        try:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta: {e}")
            return

        quality     = self.quality_var.get()
        use_cookies = self.use_cookies_var.get()

        self.is_downloading = True
        self.download_button.configure(state="disabled", text="Descargando...")
        self.progress_bar.set(0)

        thread = threading.Thread(
            target=self.download_video,
            args=(url, output_path, quality, use_cookies),
            daemon=True
        )
        thread.start()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.run()

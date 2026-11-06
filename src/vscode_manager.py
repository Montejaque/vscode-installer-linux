#!/usr/bin/env python3
"""VS Code Installer & Updater: instalación de usuario, sin sudo."""
import os
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

HOME = Path.home()
ROOT = HOME / ".local"
DEST = ROOT / "opt" / "vscode"
BIN = ROOT / "bin" / "code"
MENU = ROOT / "share" / "applications" / "visual-studio-code.desktop"
URL = "https://update.code.visualstudio.com/latest/linux-x64/stable"

def read_version(binary):
    try:
        result = subprocess.run([str(binary), "--version"], capture_output=True,
                                text=True, timeout=20)
        match = re.search(r"(?m)^\d+\.\d+\.\d+", result.stdout)
        return match.group() if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def version_at(directory):
    """Lee la versión del manifiesto; no ejecuta el binario ni necesita root."""
    manifests = [
        directory / "resources" / "app" / "package.json",
        directory / "resources" / "app" / "product.json",
    ]
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            value = data.get("version") or data.get("productVersion")
            if value and re.match(r"^\d+\.\d+\.\d+", str(value)):
                return str(value)
        except (OSError, ValueError, TypeError):
            continue
    return None

def version():
    """Versión de la copia gestionada por esta aplicación."""
    return version_at(DEST) if (DEST / "code").is_file() else None

def detect_installed():
    """Detecta VS Code instalado por apt, snap, manualmente o por esta app."""
    candidates = [
        DEST / "code",
        Path("/usr/share/code/code"),
        Path("/usr/lib/code/code"),
        Path("/opt/visual-studio-code/code"),
        Path("/snap/bin/code"),
        Path("/usr/bin/code"),
        BIN,
    ]
    path_code = shutil.which("code")
    if path_code:
        candidates.append(Path(path_code))
    seen = set()
    for binary in candidates:
        try:
            resolved = binary.resolve()
        except OSError:
            continue
        if str(resolved) in seen or not resolved.is_file():
            continue
        seen.add(str(resolved))
        detected = version_at(resolved.parent)
        if not detected:
            detected = read_version(resolved)
        if detected:
            return detected, str(binary)
    return None, None

def _atomic_write(path, content, mode=0o644):
    """Escribe un archivo de integración sin dejarlo parcialmente escrito."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.chmod(mode)
    os.replace(temporary, path)


def _refresh_desktop_caches():
    """Actualiza índices locales cuando las herramientas están disponibles."""
    commands = [
        ["update-desktop-database", str(MENU.parent)],
        ["gtk-update-icon-cache", "-f", "-t", str(ROOT / "share" / "icons" / "hicolor")],
    ]
    for command in commands:
        if shutil.which(command[0]):
            try:
                subprocess.run(command, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=15, check=False)
            except (OSError, subprocess.TimeoutExpired):
                pass


def integration():
    """Crea y comprueba lanzador, icono, menú y PATH en el perfil del usuario."""
    executable = DEST / "code"
    if not executable.is_file():
        raise RuntimeError("No existe el ejecutable de VS Code en ~/.local/opt/vscode/code.")
    if not version_at(DEST):
        raise RuntimeError("No se encuentran los metadatos de versión de VS Code.")

    BIN.parent.mkdir(parents=True, exist_ok=True)
    MENU.parent.mkdir(parents=True, exist_ok=True)
    launcher = '#!/bin/sh\nexec "$HOME/.local/opt/vscode/code" "$@"\n'
    _atomic_write(BIN, launcher, 0o755)
    if not os.access(BIN, os.X_OK):
        raise RuntimeError("No se ha podido crear el lanzador ejecutable ~/.local/bin/code.")

    icon = DEST / "resources" / "app" / "resources" / "linux" / "code.png"
    icon_name = "com.visualstudio.code"
    if icon.is_file():
        target = ROOT / "share" / "icons" / "hicolor" / "256x256" / "apps" / "visual-studio-code.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary_icon = target.with_name(target.name + ".tmp")
        shutil.copy2(icon, temporary_icon)
        os.replace(temporary_icon, target)
        icon_name = str(target)

    desktop_entry = (
        "[Desktop Entry]\n"
        "Version=1.0\n"
        "Type=Application\n"
        "Name=Visual Studio Code\n"
        "Comment=Editor de código\n"
        'Exec="' + str(BIN) + '" --new-window %F\n'
        'TryExec="' + str(BIN) + '"\n'
        "Icon=" + icon_name + "\n"
        "Terminal=false\n"
        "Categories=Development;IDE;TextEditor;\n"
        "StartupNotify=true\n"
        "StartupWMClass=code\n"
    )
    _atomic_write(MENU, desktop_entry)
    if not MENU.is_file() or str(BIN) not in MENU.read_text(encoding="utf-8"):
        raise RuntimeError("No se ha podido verificar el acceso del menú de aplicaciones.")

    marker = "# VSCode Installer user PATH"
    profile = HOME / ".profile"
    content = profile.read_text(encoding="utf-8") if profile.exists() else ""
    if marker not in content:
        with profile.open("a", encoding="utf-8") as file:
            file.write('\n' + marker + '\nexport PATH="$HOME/.local/bin:$PATH"\n')

def install(log, progress):
    if sys.platform != "linux" or os.uname().machine not in ("x86_64", "amd64"):
        raise RuntimeError("Solo Linux x86_64.")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".vscode-staging-", dir=DEST.parent) as tmp:
        tmp = Path(tmp)
        archive = tmp / "code.tar.gz"
        log("Conectando con los servidores oficiales de Microsoft...")
        request = urllib.request.Request(URL, headers={"User-Agent": "VSCodeInstaller/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            total = int(response.headers.get("Content-Length") or 0)
            downloaded = 0
            progress(2, "Descargando VS Code...")
            with archive.open("wb") as file:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = min(55, 2 + int(downloaded * 53 / total))
                        progress(percent, f"Descargando VS Code... {downloaded / 1048576:.1f} / {total / 1048576:.1f} MB")
                    else:
                        progress(2, f"Descargando VS Code... {downloaded / 1048576:.1f} MB")
        if archive.stat().st_size < 50_000_000:
            raise RuntimeError("Descarga incompleta o inesperadamente pequeña.")
        extracted = tmp / "extracted"
        extracted.mkdir()
        log("Validando y extrayendo el paquete...")
        progress(58, "Leyendo el paquete descargado...")
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                raise RuntimeError("Archivo vacío.")
            for member in members:
                parts = Path(member.name).parts
                if member.name.startswith("/") or ".." in parts or member.isdev():
                    raise RuntimeError("Ruta peligrosa en el archivo.")
                if member.issym() or member.islnk():
                    from pathlib import PurePosixPath
                    target = PurePosixPath(member.linkname)
                    if target.is_absolute() or ".." in target.parts:
                        raise RuntimeError("Enlace no seguro en el archivo.")
            count = len(members)
            for index, member in enumerate(members, 1):
                tar.extract(member, extracted)
                if index == count or index % max(1, count // 100) == 0:
                    progress(58 + int(index * 27 / count), f"Extrayendo archivos... {index * 100 // count}%")
        # No depender del nombre ni de la profundidad del directorio raíz del TAR.
        executables = [p for p in extracted.rglob("code")
                       if p.is_file() and (p.parent / "resources" / "app" / "package.json").is_file()]
        if not executables:
            raise RuntimeError("No se encontró la estructura oficial de VS Code (code y resources/app/package.json).")
        candidate = executables[0].parent
        package_version = version_at(candidate)
        if not package_version:
            raise RuntimeError("El paquete descargado no contiene una versión válida en package.json.")
        (candidate / "code").chmod((candidate / "code").stat().st_mode | 0o111)
        log("Paquete de Microsoft validado: versión " + package_version)
        backup = DEST.parent / "vscode.previous"
        if backup.exists():
            shutil.rmtree(backup)
        had_old = DEST.exists()
        log("Aplicando instalación / actualización...")
        progress(88, "Instalando archivos y preparando accesos...")
        try:
            if had_old:
                os.replace(DEST, backup)
            os.replace(candidate, DEST)
            progress(94, "Verificando la versión instalada...")
            installed_version = version()
            if not installed_version:
                raise RuntimeError("No se puede leer la versión desde resources/app/package.json tras instalar.")
            log("Versión instalada verificada: " + installed_version)
            integration()
        except Exception:
            if DEST.exists():
                shutil.rmtree(DEST, ignore_errors=True)
            if had_old and backup.exists():
                os.replace(backup, DEST)
                integration()
            raise
        if backup.exists():
            shutil.rmtree(backup)
        progress(100, "Proceso completado.")
        log("VS Code " + (version() or "") + " instalado. Preferencias y extensiones conservadas.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VS Code Installer & Updater — Punto Vuela Montejaque")
        self.geometry("900x680")
        self.configure(bg="white")
        self.busy = False
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Primary.TButton", background="#000000", foreground="#F3D54E",
                        font=("Inter", 10, "bold"), padding=10)
        frame = tk.Frame(self, bg="white", padx=24, pady=24)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="VS Code Installer & Updater", font=("Inter", 20, "bold"),
                 fg="#000000", bg="white").pack(anchor="w")
        tk.Label(frame, text="Linux x64 · Sin root · Punto Vuela Montejaque",
                 fg="#333333", bg="white").pack(anchor="w")
        tk.Frame(frame, bg="#F3D54E", height=5).pack(fill="x", pady=16)
        self.status = tk.Label(frame, bg="white", fg="black")
        self.status.pack(anchor="w", pady=8)
        bar = tk.Frame(frame, bg="white")
        bar.pack(fill="x", pady=10)
        self.buttons = []
        for label, action in [("Instalar / actualizar", self.start),
                              ("Comprobar versión", self.refresh),
                              ("Reparar acceso", self.repair)]:
            button = ttk.Button(bar, text=label, command=action)
            button.pack(side="left", padx=(0, 12))
            self.buttons.append(button)
        self.progress_text = tk.Label(frame, text="Preparado", bg="white", fg="#333333")
        self.progress_text.pack(anchor="w", pady=(4, 2))
        self.progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 8))
        self.log_area = tk.Text(frame, height=12, bg="#F7F7F7", fg="#000000")
        self.log_area.pack(fill="both", expand=True)
        footer = tk.Frame(frame, bg="white")
        footer.pack(fill="x", pady=(10, 0))
        tk.Label(footer, text="Desarrollador: Francisco Javier Gallego Orellana",
                 bg="white", fg="#000000", font=("Inter", 10, "bold")).pack(anchor="w")
        tk.Label(footer, text="Punto Vuela Montejaque · Avenida Andalucía, 48 · 29360 Montejaque (Málaga)",
                 bg="white", fg="#333333").pack(anchor="w")
        tk.Label(footer, text="Teléfono: 633 402 959 · Correo: montejaque@puntosvuela.es",
                 bg="white", fg="#333333").pack(anchor="w")
        ttk.Button(footer, text="Ver guía de uso", command=self.show_guide).pack(anchor="e", pady=(5, 0))
        self.refresh()

    def log(self, msg):
        self.after(0, lambda: (self.log_area.insert("end", msg + "\n"),
                               self.log_area.see("end")))

    def set_progress(self, value, message):
        def update():
            self.progress["value"] = value
            self.progress_text.config(text=f"{message}  ({value}%)")
        self.after(0, update)

    def show_guide(self):
        window = tk.Toplevel(self)
        window.title("Guía de uso — VS Code Installer & Updater")
        window.geometry("700x560")
        window.configure(bg="white")
        area = tk.Text(window, wrap="word", padx=18, pady=18, bg="#FAFAFA",
                       fg="#111111", font=("Inter", 10))
        area.pack(fill="both", expand=True, padx=12, pady=12)
        guide = """GUÍA DE USO

1. INSTALAR / ACTUALIZAR
Pulsa «Instalar / actualizar». Se descarga la versión estable oficial desde Microsoft. La barra muestra el progreso de descarga, extracción, instalación y verificación. No necesita sudo.

2. COMPROBAR VERSIÓN
Pulsa «Comprobar versión» para detectar la versión instalada en las ubicaciones habituales de Linux.

3. UBICACIÓN
La copia administrada por este programa se instala en ~/.local/opt/vscode. El lanzador se crea en ~/.local/bin/code y aparece en el menú de aplicaciones.

4. DATOS Y CONFIGURACIÓN
Las preferencias y extensiones existentes se conservan durante las actualizaciones.

5. CONTACTO
Desarrollador: Francisco Javier Gallego Orellana
Centro: Punto Vuela Montejaque
Dirección: Avenida Andalucía, 48, 29360 Montejaque (Málaga)
Teléfono: 633 402 959
Correo: montejaque@puntosvuela.es
"""
        area.insert("1.0", guide)
        area.config(state="disabled")

    def refresh(self):
        detected, location = detect_installed()
        if detected:
            managed = " (gestionada aquí)" if location == str(DEST / "code") else " (instalación existente)"
            self.status.config(text=f"VS Code detectado: {detected}{managed} · {location}")
        else:
            self.status.config(text="VS Code no detectado en las ubicaciones habituales")

    def repair(self):
        if not (DEST / "code").exists():
            messagebox.showwarning("Sin instalación", "Primero instala VS Code.")
            return
        try:
            integration()
            messagebox.showinfo("Correcto", "Acceso del menú reparado.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def start(self):
        if self.busy:
            return
        self.busy = True
        for button in self.buttons:
            button.config(state="disabled")
        def work():
            try:
                self.set_progress(0, "Iniciando...")
                install(self.log, self.set_progress)
                self.after(0, self.refresh)
                self.after(0, lambda: messagebox.showinfo("Listo", "VS Code instalado o actualizado."))
            except Exception as exc:
                error = str(exc)
                self.log("ERROR: " + error)
                self.after(0, lambda: messagebox.showerror("Error", error))
            finally:
                self.after(0, self.done)
        threading.Thread(target=work, daemon=True).start()

    def done(self):
        self.busy = False
        for button in self.buttons:
            button.config(state="normal")

if __name__ == "__main__":
    App().mainloop()

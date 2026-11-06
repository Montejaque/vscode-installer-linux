#!/usr/bin/env python3
"""VS Code Installer & Updater: instalación de usuario, sin sudo."""
import os
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

def version():
    binary = DEST / "code"
    if not binary.is_file():
        return None
    try:
        result = subprocess.run([str(binary), "--version"], capture_output=True,
                                text=True, timeout=20)
        match = re.search(r"(?m)^\d+\.\d+\.\d+", result.stdout)
        return match.group() if match else None
    except (OSError, subprocess.TimeoutExpired):
        return None

def integration():
    BIN.parent.mkdir(parents=True, exist_ok=True)
    MENU.parent.mkdir(parents=True, exist_ok=True)
    BIN.write_text('#!/bin/sh\nexec "$HOME/.local/opt/vscode/code" "$@"\n')
    BIN.chmod(0o755)
    icon = DEST / "resources" / "app" / "resources" / "linux" / "code.png"
    icon_name = "com.visualstudio.code"
    if icon.is_file():
        target = ROOT / "share/icons/hicolor/256x256/apps/visual-studio-code.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon, target)
        icon_name = str(target)
    MENU.write_text("[Desktop Entry]\nType=Application\nName=Visual Studio Code\n"
                    'Exec="' + str(BIN) + '" --new-window %F\n'
                    "Icon=" + icon_name + "\nTerminal=false\n"
                    "Categories=Development;IDE;TextEditor;\nStartupNotify=true\n")
    marker = "# VSCode Installer user PATH"
    profile = HOME / ".profile"
    content = profile.read_text() if profile.exists() else ""
    if marker not in content:
        with profile.open("a") as file:
            file.write('\n' + marker + '\nexport PATH="$HOME/.local/bin:$PATH"\n')

def install(log):
    if sys.platform != "linux" or os.uname().machine not in ("x86_64", "amd64"):
        raise RuntimeError("Solo Linux x86_64.")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".vscode-staging-", dir=DEST.parent) as tmp:
        tmp = Path(tmp)
        archive = tmp / "code.tar.gz"
        log("Descargando VS Code estable desde Microsoft...")
        request = urllib.request.Request(URL, headers={"User-Agent": "VSCodeInstaller/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response, archive.open("wb") as file:
            shutil.copyfileobj(response, file)
        if archive.stat().st_size < 50_000_000:
            raise RuntimeError("Descarga incompleta o inesperadamente pequeña.")
        extracted = tmp / "extracted"
        extracted.mkdir()
        log("Validando y extrayendo el paquete...")
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                raise RuntimeError("Archivo vacío.")
            # Rechazar rutas absolutas, escapes y entradas especiales.
            for member in members:
                parts = Path(member.name).parts
                if member.name.startswith("/") or ".." in parts or member.isdev():
                    raise RuntimeError("Ruta peligrosa en el archivo.")
                if member.issym() or member.islnk():
                    # Los paquetes de Electron pueden contener enlaces simbólicos.
                    # No se extraen enlaces hasta verificar sus destinos.
                    from pathlib import PurePosixPath
                    target = PurePosixPath(member.linkname)
                    if target.is_absolute() or ".." in target.parts:
                        raise RuntimeError("Enlace no seguro en el archivo.")
            tar.extractall(extracted, members=members)
        candidates = [p for p in extracted.iterdir() if p.is_dir() and (p / "code").is_file()]
        if not candidates:
            raise RuntimeError("No se encontró el ejecutable de VS Code.")
        candidate = candidates[0]
        if not (candidate / "resources/app/package.json").is_file():
            raise RuntimeError("Paquete de VS Code inválido.")
        (candidate / "code").chmod((candidate / "code").stat().st_mode | 0o111)
        backup = DEST.parent / "vscode.previous"
        if backup.exists():
            shutil.rmtree(backup)
        had_old = DEST.exists()
        log("Aplicando actualización con copia de recuperación...")
        try:
            if had_old:
                os.replace(DEST, backup)
            os.replace(candidate, DEST)
            if not version():
                raise RuntimeError("La nueva instalación no supera la comprobación de versión.")
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
        log("VS Code " + (version() or "") + " instalado. Preferencias y extensiones conservadas.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VS Code Installer & Updater — Punto Vuela Montejaque")
        self.geometry("850x560")
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
        self.log_area = tk.Text(frame, height=16, bg="#F7F7F7", fg="#000000")
        self.log_area.pack(fill="both", expand=True)
        tk.Label(frame, text="Desarrollador: Francisco Javier Gallego Orellana",
                 bg="white", fg="#333333").pack(anchor="w", pady=(12, 0))
        self.refresh()

    def log(self, msg):
        self.after(0, lambda: (self.log_area.insert("end", msg + "\n"),
                               self.log_area.see("end")))

    def refresh(self):
        self.status.config(text="Versión instalada: " + (version() or "no detectada"))

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
                install(self.log)
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

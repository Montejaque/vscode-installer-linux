# VS Code Installer & Updater — Punto Vuela Montejaque

Gestor gráfico para instalar, actualizar y reparar Visual Studio Code estable en Linux x86_64 **sin root ni sudo**. VS Code se descarga como archivo oficial TAR.GZ de Microsoft, no como AppImage.

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque

## Uso
```bash
chmod +x run.sh
./run.sh
```

Requiere Linux x86_64, Python 3, Tkinter e Internet. El gestor instala VS Code en `~/.local/opt/vscode`, crea `~/.local/bin/code` y el acceso al menú en `~/.local/share/applications/visual-studio-code.desktop`. Conserva las extensiones y preferencias del usuario.

## Identidad visual
Negro `#000000` y amarillo corporativo `#F3D54E`.

## AppImage del gestor
```bash
chmod +x build-appimage.sh
./build-appimage.sh
```
Requiere `appimagetool`. El AppImage empaqueta **el gestor**, no VS Code, y utiliza Python 3 y Tkinter del equipo anfitrión. No se ha generado todavía un binario AppImage en este entorno: no hay appimagetool/mksquashfs y no hay conectividad para obtenerlos. El script de construcción está incluido; no se debe presentar la estructura AppDir como un ejecutable terminado.

## Seguridad
La descarga procede de `https://update.code.visualstudio.com/latest/linux-x64/stable`. El gestor no requiere privilegios elevados. La verificación criptográfica de la descarga no está implementada todavía. Prueba primero en un equipo no crítico.

## Licencia
MIT para el gestor. Visual Studio Code y la tipografía Inter conservan sus licencias respectivas.

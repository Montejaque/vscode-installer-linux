# VS Code Installer & Updater — Punto Vuela Montejaque

Gestor gráfico para instalar, actualizar y reparar Visual Studio Code estable en Linux x86_64 **sin root ni sudo**. VS Code se descarga desde el servidor oficial de Microsoft en formato TAR.GZ; no se instala como AppImage.

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque

## Uso del gestor
El paquete AppImage se ejecuta directamente. Dentro de la aplicación, pulsa **Instalar / actualizar** para descargar e instalar automáticamente VS Code estable. También permite comprobar la versión y reparar el acceso del menú.

La instalación de VS Code se realiza en `~/.local/opt/vscode`, crea `~/.local/bin/code` y el acceso al menú en `~/.local/share/applications/visual-studio-code.desktop`. Conserva las preferencias y extensiones del usuario. No necesita sudo.

## Requisitos del equipo
- Linux x86_64.
- Soporte AppImage/FUSE de la distribución.
- Conexión a Internet para descargar VS Code desde Microsoft.

El gestor se compila en GitHub Actions con PyInstaller, que incorpora el intérprete Python y los componentes de Tkinter en el ejecutable. El usuario no necesita instalar Python ni Tkinter por separado.

## Compilación y distribución
La compilación se realiza automáticamente en GitHub Actions al actualizar `main`, o manualmente desde **Actions → Build Linux AppImage → Run workflow**.

El artefacto generado se llama `VSCode-Installer-Updater-x86_64.AppImage`. Al publicar una etiqueta `v*` (por ejemplo, `v1.0.0`), el workflow crea un GitHub Release y adjunta el AppImage.

## Identidad visual
Negro `#000000` y amarillo `#F3D54E`.

## Seguridad y compatibilidad
La descarga de VS Code procede de `https://update.code.visualstudio.com/latest/linux-x64/stable`. El gestor no requiere privilegios elevados y conserva los datos del usuario. La descarga todavía no incorpora verificación criptográfica de firma/hash. El AppImage se compila en Ubuntu 22.04; debe probarse en las distribuciones objetivo antes de distribuirlo ampliamente.

## Licencia
MIT para el gestor. Visual Studio Code y la tipografía Inter conservan sus licencias respectivas.
# Guía de instalación y uso

## Requisitos
- Linux x86_64.
- Python 3 y Tkinter.
- Conexión a Internet para descargar Visual Studio Code estable desde Microsoft.
- No necesita root ni sudo.

## Instalación del gestor
Descarga el ZIP del proyecto, descomprímelo y ejecuta:

```bash
cd vscode-installer-linux
chmod +x run.sh
./run.sh
```

## Instalar o actualizar Visual Studio Code
Pulsa **Instalar / actualizar**. El programa descarga el archivo TAR.GZ oficial de Microsoft y lo instala en `~/.local/opt/vscode`. El lanzador se crea en `~/.local/bin/code` y el acceso de escritorio en `~/.local/share/applications`.

La configuración y las extensiones del usuario permanecen en sus directorios habituales y no se eliminan durante la actualización.

## Reparar el acceso
Si VS Code ya está instalado pero no aparece en el menú, usa **Reparar acceso**.

## Identidad visual
Negro `#000000` y amarillo `#F3D54E`. Desarrollador: Francisco Javier Gallego Orellana. Centro: Punto Vuela Montejaque.

## AppImage
El repositorio contiene el directorio AppDir y el script `build-appimage.sh`. Para construirlo se necesita `appimagetool` y `mksquashfs`. El binario AppImage todavía no está generado. El paquete AppImage previsto ejecutará el gestor y depende de Python/Tkinter disponibles en el sistema.

## Limitaciones de verificación
No se ha podido probar una descarga e instalación real de VS Code en este entorno porque no hay conectividad DNS hacia los servidores externos. La descarga tampoco cuenta aún con verificación criptográfica de firma/hash. Antes de usarlo de forma general, validar en un equipo de pruebas.

## Solución de problemas
- Si falta Tkinter, el administrador del equipo deberá proporcionar el paquete de Tkinter correspondiente a la distribución.
- Si el comando `code` no se reconoce en una terminal ya abierta, abre una terminal nueva o ejecuta `export PATH="$HOME/.local/bin:$PATH"`.
- Para iniciar directamente: `~/.local/bin/code`.

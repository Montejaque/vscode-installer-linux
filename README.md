# VS Code Installer & Updater — Punto Vuela Montejaque

Gestor gráfico para **instalar, actualizar, comprobar y reparar el acceso a Visual Studio Code Stable** en Linux x86_64. El gestor se distribuye como AppImage; Visual Studio Code se descarga aparte desde los servidores oficiales de Microsoft en formato TAR.GZ.

> **Instalación por usuario: no necesita root, sudo, APT ni instalación en directorios del sistema.**

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
**Plataforma objetivo:** Linux x86_64 (incluido Ubuntu 20.04)  
**Interfaz:** Tkinter · **Empaquetado:** PyInstaller · **Distribución:** AppImage

## Descargar

- **[Últimas versiones y AppImage](https://github.com/Montejaque/vscode-installer-linux/releases/latest)**
- [Todas las versiones publicadas](https://github.com/Montejaque/vscode-installer-linux/releases)
- [Estado de compilaciones en GitHub Actions](https://github.com/Montejaque/vscode-installer-linux/actions)

Descarga `VSCode-Installer-Updater-x86_64.AppImage`. El AppImage es el administrador; no contiene una instalación completa de VS Code.

## Inicio rápido

1. Descarga el AppImage desde la sección [Releases](https://github.com/Montejaque/vscode-installer-linux/releases/latest).
2. Abre una terminal en la carpeta de descarga.
3. Dale permiso de ejecución y ábrelo:

   ```bash
   chmod +x VSCode-Installer-Updater-x86_64.AppImage
   ./VSCode-Installer-Updater-x86_64.AppImage
   ```

4. En la ventana, pulsa **Instalar / actualizar**.
5. Espera a que finalicen la descarga, extracción, instalación y comprobación de versión.

También puedes utilizar **Comprobar versión** o **Reparar acceso**. El botón **Desinstalar y eliminar datos** permite retirar la instalación gestionada y sus datos de usuario tras mostrar una confirmación detallada.

## Qué hace el programa

- Descarga la versión Stable para Linux x64 desde Microsoft: [endpoint oficial](https://update.code.visualstudio.com/latest/linux-x64/stable).
- Comprueba que el paquete descargado contiene la estructura esperada de VS Code.
- Lee y valida la versión desde los metadatos de `resources/app/package.json` (con alternativa a `product.json`), sin depender de ejecutar el binario para validar la instalación.
- Extrae el paquete en un directorio temporal y localiza el ejecutable aunque el TAR.GZ incluya un directorio raíz.
- Muestra el progreso de descarga y extracción, y los pasos de instalación y verificación.
- Mantiene una copia temporal de la instalación anterior durante la actualización y la restaura si falla la validación o integración.
- Crea o repara el lanzador de terminal y el acceso al menú de aplicaciones. La entrada `.desktop` usa rutas absolutas al ejecutable y al icono (los archivos de menú no expanden `$HOME`), tiene permiso de ejecución y se valida; si existe una carpeta Escritorio configurada, crea también allí un acceso directo.
- Conserva los datos de usuario: configuración, extensiones y proyectos.

## Rutas de instalación

Todo lo que administra el programa queda dentro del perfil del usuario:

| Elemento | Ruta |
|---|---|
| Aplicación de VS Code | `~/.local/opt/vscode` |
| Ejecutable principal | `~/.local/opt/vscode/code` |
| Lanzador de terminal | `~/.local/bin/code` |
| Acceso al menú | `~/.local/share/applications/visual-studio-code.desktop` |
| Icono local | `~/.local/share/icons/hicolor/256x256/apps/visual-studio-code.png` |
| PATH del usuario | Entrada en `~/.profile` |
| Preferencias | `~/.config/Code` |
| Extensiones | `~/.vscode/extensions` |

El comando `code` estará disponible en nuevas sesiones de terminal después de que el perfil vuelva a cargarse. Si no aparece inmediatamente, cierra y vuelve a abrir la terminal o ejecuta `source ~/.profile`.

**No se modifican** `/usr`, `/opt` del sistema, APT, Snap ni los paquetes instalados por el administrador del equipo.

## Requisitos

- Linux de 64 bits con arquitectura `x86_64` o `amd64`.
- Entorno gráfico compatible con Tkinter.
- Conexión a Internet para descargar VS Code.
- Soporte AppImage/FUSE de la distribución. Si la distribución no puede ejecutar AppImage directamente, consulta la documentación de tu sistema para el modo de extracción de AppImage.

El AppImage incorpora el gestor y sus dependencias Python/Tkinter empaquetadas mediante PyInstaller. No necesitas instalar Python ni Tkinter para utilizar la aplicación.

## Compilación y publicación

El workflow [Build and publish Linux AppImage](.github/workflows/build-appimage.yml):

- Se ejecuta automáticamente al hacer push a `main` o al publicar una etiqueta `v*`.
- También admite ejecución manual desde **Actions → Build and publish Linux AppImage → Run workflow**.
- Construye el ejecutable en un contenedor Ubuntu 20.04 para favorecer la compatibilidad con sistemas Ubuntu antiguos.
- Genera `VSCode-Installer-Updater-x86_64.AppImage`.
- Sube el AppImage como artefacto de Actions (retención configurada de 30 días).
- En los eventos push publica un GitHub Release y adjunta el AppImage. En los pushes a `main` asigna una etiqueta automática `v1.0.<número-de-ejecución>`; las etiquetas `v*` conservan su nombre.

La compilación satisfactoria no sustituye las pruebas de ejecución en los equipos Linux de destino.

## Desarrollo local

Código principal: `src/vscode_manager.py`  
Workflow de distribución: `.github/workflows/build-appimage.yml`  
Guía de uso: [docs/GUIA-INSTALACION.md](docs/GUIA-INSTALACION.md)

Para ejecutar el código fuente en un entorno con Python 3 y Tkinter:

```bash
python3 src/vscode_manager.py
```

Para generar el AppImage de distribución, utiliza el workflow de GitHub Actions descrito arriba.

## Seguridad y limitaciones conocidas

- El gestor no solicita privilegios elevados ni ejecuta comandos con `sudo`.
- La extracción comprueba rutas absolutas, referencias a `..` y enlaces inseguros antes de extraer.
- La versión se contrasta con los metadatos del paquete oficial.
- **La descarga todavía no verifica una firma criptográfica ni un hash publicado por Microsoft.** La procedencia se basa en el endpoint HTTPS oficial. No distribuyas paquetes modificados ni descargados de fuentes no oficiales.
- La compatibilidad real debe probarse en cada distribución y escritorio objetivo; AppImage/FUSE y las bibliotecas gráficas pueden variar.
- La actualización de VS Code se realiza cuando el usuario pulsa el botón del gestor; el programa no configura un servicio de actualización en segundo plano.

## Identidad visual y licencia

Colores de la interfaz: negro `#000000` y amarillo `#F3D54E`.

El código del gestor se distribuye bajo licencia MIT (consulta [LICENSE](LICENSE), si está presente). Visual Studio Code, sus componentes y la tipografía Inter mantienen sus respectivas licencias y condiciones de Microsoft y de sus titulares.

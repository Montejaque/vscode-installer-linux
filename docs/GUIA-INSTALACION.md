# Guía de instalación y uso

## 1. Qué es esta aplicación

VS Code Installer & Updater — Punto Vuela Montejaque es un gestor gráfico para instalar, actualizar, comprobar y reparar el acceso a Visual Studio Code Stable en Linux x86_64.

El gestor se distribuye como archivo AppImage. **El AppImage no es Visual Studio Code**: al pulsar «Instalar / actualizar», la aplicación descarga el paquete TAR.GZ oficial de Microsoft y lo instala en el perfil del usuario.

La instalación es local al usuario y no necesita root, sudo, APT ni permisos de administrador.

## 2. Requisitos

- Linux x86_64 (arquitectura `x86_64` o `amd64`).
- Entorno gráfico compatible con Tkinter.
- Conexión a Internet.
- Soporte AppImage/FUSE de la distribución.

El gestor incluye Python y Tkinter en el ejecutable generado con PyInstaller. No tienes que instalarlos por separado.

## 3. Descargar y ejecutar el gestor

1. Entra en [Releases](https://github.com/Montejaque/vscode-installer-linux/releases/latest).
2. Descarga `VSCode-Installer-Updater-x86_64.AppImage`.
3. Abre una terminal en la carpeta donde se ha descargado.
4. Ejecuta:

   ```bash
   chmod +x VSCode-Installer-Updater-x86_64.AppImage
   ./VSCode-Installer-Updater-x86_64.AppImage
   ```

Si el sistema no permite iniciar AppImages, comprueba que la distribución tenga soporte FUSE/AppImage. No ejecutes el gestor con sudo.

## 4. Instalar o actualizar VS Code

1. Abre el gestor.
2. Pulsa **Instalar / actualizar**.
3. La aplicación se conecta al endpoint oficial de Microsoft para Linux x64 Stable: `https://update.code.visualstudio.com/latest/linux-x64/stable`.
4. Se descarga el TAR.GZ y la barra de progreso informa del avance.
5. El gestor valida la estructura y los metadatos del paquete, lo extrae en una carpeta temporal y prepara la instalación.
6. Se instala en el perfil del usuario y se comprueba la versión.
7. Al terminar, se muestra el resultado.

La comprobación de versión lee los metadatos de `resources/app/package.json` o `product.json`. Así se evita que una validación dependa exclusivamente de poder iniciar el binario durante el proceso de instalación.

Durante una actualización, el gestor conserva temporalmente la instalación anterior. Si falla la validación o la integración, intenta restaurar esa copia.

## 5. Ubicaciones utilizadas

| Elemento | Ruta |
|---|---|
| Instalación administrada | `~/.local/opt/vscode` |
| Ejecutable | `~/.local/opt/vscode/code` |
| Lanzador de terminal | `~/.local/bin/code` |
| Acceso al menú | `~/.local/share/applications/visual-studio-code.desktop` |
| Icono | `~/.local/share/icons/hicolor/256x256/apps/visual-studio-code.png` |
| PATH | Entrada añadida a `~/.profile` |

Los datos de usuario de VS Code permanecen en sus ubicaciones habituales:

- Preferencias y estado: `~/.config/Code`.
- Extensiones: `~/.vscode/extensions`.
- Proyectos: permanecen en las carpetas donde los tengas guardados.

No se modifican directorios del sistema como `/usr` o `/opt`, ni se instalan paquetes mediante APT o Snap.

**Importante:** después de crear la entrada de PATH, abre una terminal nueva para utilizar `code`. También puedes recargar el perfil con:

```bash
source ~/.profile
```

## 6. Funciones de la ventana

### Instalar / actualizar
Descarga e instala la versión Stable más reciente de Microsoft. Muestra el progreso de descarga, extracción, instalación y verificación.

### Comprobar versión
Busca una instalación de VS Code en las ubicaciones habituales y muestra la versión detectada y su ruta.

### Reparar acceso
Vuelve a crear el lanzador `~/.local/bin/code`, el acceso al menú y la integración de usuario de la instalación administrada. No vuelve a descargar VS Code.

### Desinstalar y eliminar datos
El botón solicita confirmación antes de borrar la instalación administrada en `~/.local/opt/vscode`, la copia temporal de recuperación, el lanzador `~/.local/bin/code`, el acceso del menú, el icono, el acceso del Escritorio que haya creado el gestor, y los datos de usuario de VS Code (`~/.config/Code`, `~/.vscode`, cachés y datos locales). También retira exclusivamente la entrada PATH añadida por este programa.

**Esta operación elimina preferencias, perfiles y extensiones y no se puede deshacer.** No elimina carpetas de proyectos ni instalaciones independientes realizadas con APT, Snap u otros métodos. El AppImage del propio gestor no se borra automáticamente porque puede estar ejecutándose desde cualquier ubicación.

### Ver guía de uso
Abre las instrucciones integradas en la propia aplicación.

## 7. Solución de problemas

### El AppImage no se abre
Comprueba que tiene permiso de ejecución y que el sistema admite AppImage/FUSE. No lo ejecutes con sudo.

### El comando `code` no se reconoce
Abre una terminal nueva o ejecuta `source ~/.profile`. Comprueba que existe `~/.local/bin/code` y que `~/.local/bin` está incluido en PATH.

### El acceso del menú no aparece
Abre el gestor y pulsa **Reparar acceso**. Esta opción vuelve a generar el lanzador y el archivo `.desktop` usando la ruta absoluta del ejecutable y del icono, marca el acceso como ejecutable y valida su contenido. Comprueba que la instalación administrada existe en `~/.local/opt/vscode`.

### La instalación o actualización falla
Consulta el registro que aparece en la ventana del gestor. El programa valida que el paquete contenga el ejecutable y los metadatos esperados. Si falla una actualización después de apartar la instalación anterior, intenta restaurarla automáticamente. Comprueba también la conexión a Internet y el espacio libre del perfil de usuario.

### No se puede iniciar VS Code
La validación de instalación confirma la estructura y versión del paquete, pero no garantiza que todos los componentes gráficos y bibliotecas del sistema sean compatibles. Comprueba los requisitos de tu distribución y ejecuta `~/.local/opt/vscode/code` desde una terminal para ver posibles mensajes de error.

## 8. Compilación y publicación

La compilación y publicación se automatizan mediante [GitHub Actions](https://github.com/Montejaque/vscode-installer-linux/actions):

- Se activa con cambios en `main`, con etiquetas `v*` o manualmente.
- PyInstaller empaqueta el gestor en un entorno Ubuntu 20.04 para favorecer compatibilidad con sistemas antiguos.
- Se genera el archivo `VSCode-Installer-Updater-x86_64.AppImage`.
- El artefacto de Actions queda disponible durante 30 días.
- En eventos push se crea un GitHub Release y se adjunta el AppImage. Los pushes a `main` reciben una etiqueta automática `v1.0.<número-de-ejecución>`.

Consulta [las versiones publicadas](https://github.com/Montejaque/vscode-installer-linux/releases).

## 9. Seguridad y limitaciones

- No requiere privilegios de administrador.
- La extracción rechaza rutas absolutas, referencias a `..`, dispositivos y enlaces simbólicos o duros con destinos no seguros.
- La versión se lee de los metadatos del paquete descargado.
- La descarga se realiza mediante HTTPS desde el dominio oficial de Microsoft.
- **Actualmente no se verifica una firma criptográfica ni un hash del archivo descargado.**
- Debe probarse en cada distribución de destino; la compatibilidad AppImage/FUSE y las dependencias gráficas pueden variar.
- La actualización se inicia manualmente desde la aplicación; no hay un actualizador residente en segundo plano.

## 10. Autoría y contacto

**Desarrollador:** Francisco Javier Gallego Orellana  
**Centro:** Punto Vuela Montejaque  
**Dirección:** Avenida Andalucía, 48, 29360 Montejaque (Málaga)  
**Teléfono:** 633 402 959  
**Correo:** montejaque@puntosvuela.es

Identidad visual: negro `#000000` y amarillo `#F3D54E`.

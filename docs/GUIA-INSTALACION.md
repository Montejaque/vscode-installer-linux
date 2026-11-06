# Guía de instalación y uso

## Requisitos
- Linux x86_64.
- Conexión a Internet.
- Soporte AppImage/FUSE de la distribución.

El AppImage incorpora el ejecutable del gestor, Python y Tkinter mediante PyInstaller. No es necesario instalar Python ni Tkinter por separado. No requiere root ni sudo para instalar VS Code en el perfil del usuario.

## Descargar y ejecutar
1. Descarga `VSCode-Installer-Updater-x86_64.AppImage` desde Releases o desde el artefacto de GitHub Actions.
2. Abre una terminal en la carpeta donde lo has descargado.
3. Ejecuta:

    chmod +x VSCode-Installer-Updater-x86_64.AppImage
    ./VSCode-Installer-Updater-x86_64.AppImage

## Instalar o actualizar Visual Studio Code
En la ventana del gestor, pulsa **Instalar / actualizar**. El programa descarga automáticamente la versión estable oficial de Microsoft para Linux x64 en formato TAR.GZ. La barra de progreso informa del avance de descarga, extracción, instalación y verificación. Al terminar, muestra la versión instalada.

El gestor crea:
- Lanzador: `~/.local/bin/code`.
- Acceso al menú: `~/.local/share/applications/visual-studio-code.desktop`.
- Icono local, cuando está disponible en el paquete descargado.
- Entrada de PATH en `~/.profile` para que el comando `code` esté disponible en nuevas terminales.

No se utiliza sudo. Las preferencias y extensiones existentes se conservan. Durante la actualización se mantiene una copia temporal de recuperación y se restaura la instalación anterior si falla la validación de la nueva.

## Guía integrada y contacto
La ventana incluye el botón **Ver guía de uso**, con instrucciones y datos de contacto del centro.

- Desarrollador: Francisco Javier Gallego Orellana.
- Centro: Punto Vuela Montejaque.
- Dirección: Avenida Andalucía, 48, 29360 Montejaque (Málaga).
- Teléfono: 633 402 959.
- Correo: montejaque@puntosvuela.es.

## Otras opciones
- **Comprobar versión:** muestra la versión de VS Code instalada.
- **Reparar acceso:** vuelve a crear el lanzador y la entrada del menú sin reinstalar VS Code.

## Construcción y publicación
GitHub Actions compila el gestor mediante PyInstaller y genera el AppImage. Cada push a `main` produce un artefacto descargable. Al publicar una etiqueta `v*`, el workflow crea un GitHub Release con el AppImage adjunto.

## Limitaciones y seguridad
La compilación del AppImage en Ubuntu 22.04 no sustituye la prueba de ejecución en cada distribución objetivo, especialmente sistemas antiguos. La descarga de VS Code aún no incorpora verificación criptográfica de firma/hash. Se recomienda probar primero en un equipo de pruebas.

## Identidad y autoría
Desarrollador: Francisco Javier Gallego Orellana.  
Centro: Punto Vuela Montejaque.  
Colores: negro `#000000` y amarillo `#F3D54E`.
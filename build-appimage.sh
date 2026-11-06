#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
echo "La compilación oficial se realiza en GitHub Actions."
echo "Abre la pestaña Actions del repositorio y ejecuta 'Build Linux AppImage'."
echo "El workflow compila el gestor con PyInstaller e incluye Python/Tkinter."

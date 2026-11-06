#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [[ -z "$TOOL" || ! -x "$TOOL" ]]; then
  echo "ERROR: falta appimagetool; no se puede crear un AppImage válido." >&2
  exit 1
fi
mkdir -p "$ROOT/dist"
ARCH=x86_64 "$TOOL" "$ROOT/AppDir" "$ROOT/dist/VSCode-Installer-Updater-x86_64.AppImage"
chmod +x "$ROOT/dist/VSCode-Installer-Updater-x86_64.AppImage"
